# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import logging
from contextlib import contextmanager
from functools import wraps
from requests import HTTPError
import pytz
from dateutil.parser import parse
from markupsafe import Markup

from orj import api, fields, models, _
from orj.modules.registry import Registry
from orj.tools import ormcache_context, email_normalize
from orj.osv import expression
from orj.sql_db import BaseCursor

from orj.addons.google_calendar.utils.google_event import GoogleEvent
from orj.addons.google_calendar.utils.google_calendar import GoogleCalendarService
from orj.addons.google_account.models.google_service import TIMEOUT

_logger = logging.getLogger(__name__)


# API requests are sent to Google Calendar after the current transaction ends.
# This ensures changes are sent to Google only if they really happened in the Orj database.
# It is particularly important for event creation , otherwise the event might be created
# twice in Google if the first creation crashed in Orj.
def after_commit(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        assert isinstance(self.env.cr, BaseCursor)
        dbname = self.env.cr.dbname
        context = self.env.context
        uid = self.env.uid

        if self.env.context.get('no_calendar_sync'):
            return

        @self.env.cr.postcommit.add
        def called_after():
            db_registry = Registry(dbname)
            with db_registry.cursor() as cr:
                env = api.Environment(cr, uid, context)
                try:
                    func(self.with_env(env), *args, **kwargs)
                except Exception as e:
                    _logger.warning("Could not sync record now: %s" % self)
                    _logger.exception(e)

    return wrapped

@contextmanager
def google_calendar_token(user):
    yield user._get_google_calendar_token()


class GoogleSync(models.AbstractModel):
    _name = 'google.calendar.sync'
    _description = "Synchronize a record with Google Calendar"

    google_id = fields.Char('Google Calendar Id', copy=False)
    need_sync = fields.Boolean(default=True, copy=False)
    active = fields.Boolean(default=True)

    def write(self, vals):
        google_service = GoogleCalendarService(self.env['google.service'])
        if 'google_id' in vals:
            self.env.registry.clear_cache()  # _event_ids_from_google_ids
        synced_fields = self._get_google_synced_fields()
        if 'need_sync' not in vals and vals.keys() & synced_fields and not self.env.user.google_synchronization_stopped:
            vals['need_sync'] = True

        result = super().write(vals)
        if self.env.user._get_google_sync_status() != "sync_paused":
            for record in self:
                if record.need_sync and record.google_id:
                    record.with_user(record._get_event_user())._google_patch(google_service, record.google_id, record._google_values(), timeout=3)

        return result

    @api.model_create_multi
    def create(self, vals_list):
        if any(vals.get('google_id') for vals in vals_list):
            self.env.registry.clear_cache()  # _event_ids_from_google_ids
        if self.env.user.google_synchronization_stopped:
            for vals in vals_list:
                vals.update({'need_sync': False})
        records = super().create(vals_list)
        self._handle_allday_recurrences_edge_case(records, vals_list)

        google_service = GoogleCalendarService(self.env['google.service'])
        if self.env.user._get_google_sync_status() != "sync_paused":
            for record in records:
                if record.need_sync and record.active:
                    record.with_user(record._get_event_user())._google_insert(google_service, record._google_values(), timeout=3)
        return records

    def _handle_allday_recurrences_edge_case(self, records, vals_list):
        """
        When creating 'All Day' recurrent event, the first event is wrongly synchronized as
        a single event and then its recurrence creates a duplicated event. We must manually
        set the 'need_sync' attribute as False in order to avoid this unwanted behavior.
        """
        if vals_list and self._name == 'calendar.event':
            forbid_sync = all(not vals.get('need_sync', True) for vals in vals_list)
            records_to_skip = records.filtered(lambda r: r.need_sync and r.allday and r.recurrency and not r.recurrence_id)
            if forbid_sync and records_to_skip:
                records_to_skip.with_context(send_updates=False).need_sync = False

    def unlink(self):
        """We can't delete an event that is also in Google Calendar. Otherwise we would
        have no clue that the event must must deleted from Google Calendar at the next sync.
        """
        synced = self.filtered('google_id')
        # LUL TODO find a way to get rid of this context key
        if self.env.context.get('archive_on_error') and self._active_name:
            synced.write({self._active_name: False})
            self = self - synced
        elif synced:
            # Since we can not delete such an event (see method comment), we archive it.
            # Notice that archiving an event will delete the associated event on Google.
            # Then, since it has been deleted on Google, the event is also deleted on Orj DB (_sync_google2orj).
            self.action_archive()
            return True
        return super().unlink()

    def _from_google_ids(self, google_ids):
        if not google_ids:
            return self.browse()
        return self.browse(self._event_ids_from_google_ids(google_ids))

    @api.model
    @ormcache_context('google_ids', keys=('active_test',))
    def _event_ids_from_google_ids(self, google_ids):
        return self.search([('google_id', 'in', google_ids)]).ids

    def _sync_orj2google(self, google_service: GoogleCalendarService):
        if not self:
            return
        if self._active_name:
            records_to_sync = self.filtered(self._active_name)
        else:
            records_to_sync = self
        cancelled_records = self - records_to_sync

        updated_records = records_to_sync.filtered('google_id')
        new_records = records_to_sync - updated_records
        if self.env.user._get_google_sync_status() != "sync_paused":
            for record in cancelled_records:
                if record.google_id and record.need_sync:
                    record.with_user(record._get_event_user())._google_delete(google_service, record.google_id)
            for record in new_records:
                record.with_user(record._get_event_user())._google_insert(google_service, record._google_values())
            for record in updated_records:
                record.with_user(record._get_event_user())._google_patch(google_service, record.google_id, record._google_values())

    def _cancel(self):
        self.with_context(dont_notify=True).write({'google_id': False})
        self.unlink()

    @api.model
    def _sync_google2orj(self, google_events: GoogleEvent, write_dates=None, default_reminders=()):
        """Synchronize Google recurrences in Orj. Creates new recurrences, updates
        existing ones.

        :param google_recurrences: Google recurrences to synchronize in Orj
        :param write_dates: A dictionary mapping Orj record IDs to their write dates.
        :return: synchronized orj recurrences
        """
        write_dates = dict(write_dates or {})
        existing = google_events.exists(self.env)
        new = google_events - existing - google_events.cancelled()

        orj_values = [
            dict(self._orj_values(e, default_reminders), need_sync=False)
            for e in new
        ]
        new_orj = self.with_context(dont_notify=True)._create_from_google(new, orj_values)
        cancelled = existing.cancelled()
        cancelled_orj = self.browse(cancelled.orj_ids(self.env))

        # Check if it is a recurring event that has been rescheduled.
        # We have to check if an event already exists in Orj.
        # Explanation:
        # A recurrent event with `google_id` is equal to ID_RANGE_TIMESTAMP can be rescheduled.
        # The new `google_id` will be equal to ID_TIMESTAMP.
        # We have to delete the event created under the old `google_id`.
        rescheduled_events = new.filter(lambda gevent: not gevent.is_recurrence_follower())
        if rescheduled_events:
            google_ids_to_remove = [event.full_recurring_event_id() for event in rescheduled_events]
            cancelled_orj += self.env['calendar.event'].search([('google_id', 'in', google_ids_to_remove)])

        cancelled_orj.exists()._cancel()
        synced_records = new_orj + cancelled_orj
        pending = existing - cancelled
        pending_orj = self.browse(pending.orj_ids(self.env)).exists()
        for gevent in pending:
            orj_record = self.browse(gevent.orj_id(self.env))
            if orj_record not in pending_orj:
                # The record must have been deleted in the mean time; nothing left to sync
                continue
            # Last updated wins.
            # This could be dangerous if google server time and orj server time are different
            updated = parse(gevent.updated)
            # Use the record's write_date to apply Google updates only if they are newer than Orj's write_date.
            orj_record_write_date = write_dates.get(orj_record.id, orj_record.write_date)
            # Migration from 13.4 does not fill write_date. Therefore, we force the update from Google.
            if not orj_record_write_date or updated >= pytz.utc.localize(orj_record_write_date):
                vals = dict(self._orj_values(gevent, default_reminders), need_sync=False)
                orj_record.with_context(dont_notify=True)._write_from_google(gevent, vals)
                synced_records |= orj_record

        return synced_records

    def _google_error_handling(self, http_error):
        # We only handle the most problematic errors of sync events.
        if http_error.response.status_code in (403, 400):
            response = http_error.response.json()
            if not self.exists():
                reason = "Google gave the following explanation: %s" % response['error'].get('message')
                error_log = "Error while syncing record. It does not exists anymore in the database. %s" % reason
                _logger.error(error_log)
                return

            if self._name == 'calendar.event':
                start = self.start and self.start.strftime('%Y-%m-%d at %H:%M') or _("undefined time")
                event_ids = self.id
                name = self.name
                error_log = "Error while syncing event: "
                event = self
            else:
                # calendar recurrence is triggering the error
                event = self.base_event_id or self._get_first_event(include_outliers=True)
                start = event.start and event.start.strftime('%Y-%m-%d at %H:%M') or _("undefined time")
                event_ids = _("%(id)s and %(length)s following", id=event.id, length=len(self.calendar_event_ids.ids))
                name = event.name
                # prevent to sync other events
                self.calendar_event_ids.need_sync = False
                error_log = "Error while syncing recurrence [{id} - {name} - {rrule}]: ".format(id=self.id, name=self.name, rrule=self.rrule)

            # We don't have right access on the event or the request paramaters were bad.
            # https://developers.google.com/calendar/v3/errors#403_forbidden_for_non-organizer
            if http_error.response.status_code == 403 and "forbiddenForNonOrganizer" in http_error.response.text:
                reason = _("you don't seem to have permission to modify this event on Google Calendar")
            else:
                reason = _("Google gave the following explanation: %s", response['error'].get('message'))

            error_log += "The event (%(id)s - %(name)s at %(start)s) could not be synced. It will not be synced while " \
                         "it is not updated. Reason: %(reason)s" % {'id': event_ids, 'start': start, 'name': name,
                                                                    'reason': reason}
            _logger.warning(error_log)

            body = _("The following event could not be synced with Google Calendar.") + Markup("<br/>") + \
                   _("It will not be synced as long at it is not updated.") + Markup("<br/>") + \
                   reason

            if event:
                event.message_post(
                    body=body,
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )

    @after_commit
    def _google_delete(self, google_service: GoogleCalendarService, google_id, timeout=TIMEOUT):
        with google_calendar_token(self.env.user.sudo()) as token:
            if token:
                is_recurrence = self._context.get('is_recurrence', False)
                google_service.google_service = google_service.google_service.with_context(is_recurrence=is_recurrence)
                google_service.delete(google_id, token=token, timeout=timeout)
                # When the record has been deleted on our side, we need to delete it on google but we don't want
                # to raise an error because the record don't exists anymore.
                self.exists().with_context(dont_notify=True).need_sync = False

    @after_commit
    def _google_patch(self, google_service: GoogleCalendarService, google_id, values, timeout=TIMEOUT):
        with google_calendar_token(self.env.user.sudo()) as token:
            if token:
                try:
                    google_service.patch(google_id, values, token=token, timeout=timeout)
                except HTTPError as e:
                    if e.response.status_code in (400, 403):
                        self._google_error_handling(e)
                if values:
                    self.exists().with_context(dont_notify=True).need_sync = False

    def _get_post_sync_values(self, request_values, google_values):
        """ Return the values to be written in the event right after its insertion in Google side. """
        writeable_values = {
            'google_id': request_values['id'],
            'need_sync': False,
        }
        return writeable_values

    def _need_video_call(self):
        """ Implement this method to return True if the event needs a video call
        :return: bool
        """
        self.ensure_one()
        return True

    @after_commit
    def _google_insert(self, google_service: GoogleCalendarService, values, timeout=TIMEOUT):
        if not values:
            return
        with google_calendar_token(self.env.user.sudo()) as token:
            if token:
                try:
                    send_updates = self._context.get('send_updates', True)
                    google_service.google_service = google_service.google_service.with_context(send_updates=send_updates)
                    google_values = google_service.insert(values, token=token, timeout=timeout, need_video_call=self._need_video_call())
                    self.with_context(dont_notify=True).write(self._get_post_sync_values(values, google_values))
                except HTTPError as e:
                    if e.response.status_code in (400, 403):
                        self._google_error_handling(e)
                        self.with_context(dont_notify=True).need_sync = False

    def _get_records_to_sync(self, full_sync=False):
        """Return records that should be synced from Orj to Google

        :param full_sync: If True, all events attended by the user are returned
        :return: events
        """
        domain = self._get_sync_domain()
        if not full_sync:
            is_active_clause = (self._active_name, '=', True) if self._active_name else expression.TRUE_LEAF
            domain = expression.AND([domain, [
                '|',
                    '&', ('google_id', '=', False), is_active_clause,
                    ('need_sync', '=', True),
            ]])
        # We want to limit to 200 event sync per transaction, it shouldn't be a problem for the day to day
        # but it allows to run the first synchro within an acceptable time without timeout.
        # If there is a lot of event to synchronize to google the first time,
        # they will be synchronized eventually with the cron running few times a day
        return self.with_context(active_test=False).search(domain, limit=200)

    def _check_any_records_to_sync(self):
        """ Returns True if there are pending records to be synchronized from Orj to Google, False otherwise. """
        is_active_clause = (self._active_name, '=', True) if self._active_name else expression.TRUE_LEAF
        domain = expression.AND([self._get_sync_domain(), [
            '|',
                '&', ('google_id', '=', False), is_active_clause,
                ('need_sync', '=', True),
        ]])
        return self.search_count(domain, limit=1) > 0

    def _write_from_google(self, gevent, vals):
        self.write(vals)

    @api.model
    def _create_from_google(self, gevents, vals_list):
        return self.create(vals_list)

    @api.model
    def _get_sync_partner(self, emails):
        normalized_emails = [email_normalize(contact) for contact in emails if email_normalize(contact)]
        user_partners = self.env['mail.thread']._mail_search_on_user(normalized_emails, extra_domain=[('share', '=', False)])
        partners = list(user_partners)
        remaining = [email for email in normalized_emails if
                     email not in [partner.email_normalized for partner in partners]]
        if remaining:
            partners += self.env['mail.thread']._mail_find_partner_from_emails(remaining, records=self, force_create=True)
        unsorted_partners = self.env['res.partner'].browse([p.id for p in partners if p.id])
        # partners needs to be sorted according to the emails order provided by google
        k = {value: idx for idx, value in enumerate(emails)}
        result = unsorted_partners.sorted(key=lambda p: k.get(p.email_normalized, -1))
        return result

    @api.model
    def _orj_values(self, google_event: GoogleEvent, default_reminders=()):
        """Implements this method to return a dict of Orj values corresponding
        to the Google event given as parameter
        :return: dict of Orj formatted values
        """
        raise NotImplementedError()

    def _google_values(self):
        """Implements this method to return a dict with values formatted
        according to the Google Calendar API
        :return: dict of Google formatted values
        """
        raise NotImplementedError()

    def _get_sync_domain(self):
        """Return a domain used to search records to synchronize.
        e.g. return a domain to synchronize records owned by the current user.
        """
        raise NotImplementedError()

    def _get_google_synced_fields(self):
        """Return a set of field names. Changing one of these fields
        marks the record to be re-synchronized.
        """
        raise NotImplementedError()

    @api.model
    def _restart_google_sync(self):
        """ Turns on the google synchronization for all the events of
        a given user.
        """
        raise NotImplementedError()

    def _get_event_user(self):
        """ Return the correct user to send the request to Google.
        It's possible that a user creates an event and sets another user as the organizer. Using self.env.user will
        cause some issues, and It might not be possible to use this user for sending the request, so this method gets
        the appropriate user accordingly.
        """
        raise NotImplementedError()

# Part of Orj. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from orj import fields, models, api, _
from orj.exceptions import UserError

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    l10n_fr_date_to_changed = fields.Boolean(export_string_translation=False)

    def _l10n_fr_leave_applies(self):
        # The french l10n is meant to be computed only in very specific cases:
        # - there is only one employee affected by the leave
        # - the company is french
        # - the leave_type is the reference leave_type of that company
        self.ensure_one()
        return self.employee_id and \
               self.company_id.country_id.code == 'FR' and \
               self.resource_calendar_id != self.company_id.resource_calendar_id and \
               self.holiday_status_id == self.company_id._get_fr_reference_leave_type()

    def _get_fr_date_from_to(self, date_from, date_to):
        self.ensure_one()
        # What we need to compute is how much we will need to push date_to in order to account for the lost days
        # This gets even more complicated in two_weeks_calendars

        # The following computation doesn't work for resource calendars in
        # which the employee works zero hours.
        if not (self.resource_calendar_id.attendance_ids):
            raise UserError(_("An employee can't take paid time off in a period without any work hours."))

        if not self.request_unit_hours:
            # Use company's working schedule hours for the leave to avoid duration calculation issues.
            def adjust_date_range(date_from, date_to, period, attendance_ids, employee_id):
                period_ids_from = attendance_ids.filtered(lambda a: a.day_period in period
                                                                    and int(a.dayofweek) == date_from.weekday()
                                                                    and (not a.two_weeks_calendar or int(a.week_type) == a.get_week_type(date_from)))
                period_ids_to = attendance_ids.filtered(lambda a: a.day_period in period
                                                                    and int(a.dayofweek) == date_to.weekday()
                                                                    and (not a.two_weeks_calendar or int(a.week_type) == a.get_week_type(date_to)))
                if period_ids_from:
                    min_hour = min(attendance.hour_from for attendance in period_ids_from)
                    date_from = self._to_utc(date_from, min_hour, employee_id)
                if period_ids_to:
                    max_hour = max(attendance.hour_to for attendance in period_ids_to)
                    date_to = self._to_utc(date_to, max_hour, employee_id)
                return date_from, date_to

            if self.request_unit_half:
                period = ['morning'] if self.request_date_from_period == 'am' else ['afternoon']
            else:
                period = ['morning', 'afternoon']
            attendance_ids = self.company_id.resource_calendar_id.attendance_ids
            date_from, date_to = adjust_date_range(date_from, date_to, period, attendance_ids, self.employee_id)

        if self.request_unit_half and self.request_date_from_period == 'am':
            # In normal workflows request_unit_half implies that date_from and date_to are the same
            # request_unit_half allows us to choose between `am` and `pm`
            # In a case where we work from mon-wed and request a half day in the morning
            # we do not want to push date_to since the next work attendance is actually in the afternoon
            date_from_weektype = str(self.env['resource.calendar.attendance'].get_week_type(date_from))
            date_from_dayofweek = str(date_from.weekday())
            # Fetch the attendances we care about
            attendance_ids = self.resource_calendar_id.attendance_ids.filtered(lambda a:
                a.dayofweek == date_from_dayofweek
                and a.day_period != "lunch"
                and (not self.resource_calendar_id.two_weeks_calendar or a.week_type == date_from_weektype))
            if len(attendance_ids) == 2:
                # The employee took the morning off on a day where he works the afternoon aswell
                return (date_from, date_to)

        # Check calendars for working days until we find the right target, start at date_to + 1 day
        # Postpone date_target until the next working day
        date_start = date_from
        date_target = date_to
        # It is necessary to move the start date up to the first work day of
        # the employee calendar as otherwise days worked on by the company
        # calendar before the actual start of the leave would be taken into
        # account.
        while not self.resource_calendar_id._works_on_date(date_start):
            date_start += relativedelta(days=1)
        while not self.resource_calendar_id._works_on_date(date_target + relativedelta(days=1)):
            date_target += relativedelta(days=1)

        # Undo the last day increment
        return (date_start, date_target)

    @api.depends('request_date_from_period', 'request_hour_from', 'request_hour_to', 'request_date_from', 'request_date_to',
                 'request_unit_half', 'request_unit_hours', 'employee_id')
    def _compute_date_from_to(self):
        super()._compute_date_from_to()
        for leave in self:
            if leave._l10n_fr_leave_applies():
                new_date_from, new_date_to = leave._get_fr_date_from_to(leave.date_from, leave.date_to)
                if new_date_from != leave.date_from:
                    leave.date_from = new_date_from
                if new_date_to != leave.date_to:
                    leave.date_to = new_date_to
                    leave.l10n_fr_date_to_changed = True
                else:
                    leave.l10n_fr_date_to_changed = False

    def _get_durations(self, check_leave_type=True, resource_calendar=None):
        """
        In french time off laws, if an employee has a part time contract, when taking time off
        before one of his off day (compared to the company's calendar) it should also count the time
        between the time off and the next calendar work day/company off day (weekends).

        For example take an employee working mon-wed in a company where the regular calendar is mon-fri.
        If the employee were to take a time off ending on wednesday, the legal duration would count until friday.
        """
        if not resource_calendar:
            fr_leaves = self.filtered(lambda leave: leave._l10n_fr_leave_applies())
            duration_by_leave_id = super(HrLeave, self - fr_leaves)._get_durations(resource_calendar=resource_calendar)
            fr_leaves_by_company = fr_leaves.grouped('company_id')
            for company, leaves in fr_leaves_by_company.items():
                duration_by_leave_id.update(leaves._get_durations(resource_calendar=company.resource_calendar_id))
            return duration_by_leave_id
        return super()._get_durations(resource_calendar=resource_calendar)

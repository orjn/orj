# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import datetime

from orj import api, fields, models


class EventMeetingRoom(models.Model):
    _name = "event.meeting.room"
    _description = "Event Meeting Room"
    _order = "is_pinned DESC, id"
    _inherit = [
        'chat.room.mixin',
        'website.published.mixin',
    ]

    _DELAY_CLEAN = datetime.timedelta(hours=4)

    name = fields.Char("Topic", required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    is_published = fields.Boolean(copy=True)  # make the inherited field copyable
    event_id = fields.Many2one("event.event", string="Event", required=True, ondelete="cascade")
    is_pinned = fields.Boolean("Is Pinned")
    chat_room_id = fields.Many2one("chat.room", required=True, ondelete="restrict")
    room_max_capacity = fields.Selection(default="8", copy=True)
    summary = fields.Char("Summary", translate=True)
    target_audience = fields.Char("Audience", translate=True)

    @api.depends('name', 'event_id.name')
    def _compute_website_url(self):
        super(EventMeetingRoom, self)._compute_website_url()
        for meeting_room in self:
            if meeting_room.id:
                base_url = meeting_room.event_id.get_base_url()
                meeting_room.website_url = '%s/event/%s/meeting_room/%s' % (base_url, self.env["ir.http"]._slug(meeting_room.event_id), self.env["ir.http"]._slug(meeting_room))

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            if not values.get("chat_room_id") and not values.get('room_name'):
                values['room_name'] = 'orj-room-%s' % (values['name'])
        return super(EventMeetingRoom, self).create(values_list)

    @api.autovacuum
    def _archive_meeting_rooms(self):
        """Archive all non-pinned room with 0 participant if nobody has joined it for a moment."""
        self.sudo().search([
            ("is_pinned", "=", False),
            ("active", "=", True),
            ("room_participant_count", "=", 0),
            ("room_last_activity", "<", fields.Datetime.now() - self._DELAY_CLEAN),
        ]).active = False

    def open_website_url(self):
        """ Overridden to use a relative URL instead of an absolute when website_id is False. """
        if self.event_id.website_id:
            return super().open_website_url()
        return self.env['website'].get_client_action(f'/event/{self.env["ir.http"]._slug(self.event_id)}/meeting_room/{self.env["ir.http"]._slug(self)}')

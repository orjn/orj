# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    visitor_sessions_count = fields.Integer('# Sessions', compute="_compute_visitor_sessions_count", groups="im_livechat.im_livechat_group_user")

    @api.depends('visitor_ids.discuss_channel_ids')
    def _compute_visitor_sessions_count(self):
        for lead in self:
            lead.visitor_sessions_count = len(lead.visitor_ids.discuss_channel_ids)

    def action_redirect_to_livechat_sessions(self):
        visitors = self.visitor_ids
        action = self.env["ir.actions.actions"]._for_xml_id("website_livechat.website_visitor_livechat_session_action")
        action['domain'] = [('livechat_visitor_id', 'in', visitors.ids), ('has_message', '=', True)]
        return action


# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import _, models


class ChatbotScriptStep(models.Model):
    _inherit = 'chatbot.script.step'

    def _chatbot_crm_prepare_lead_values(self, discuss_channel, description):
        values = super()._chatbot_crm_prepare_lead_values(discuss_channel, description)
        if discuss_channel.livechat_visitor_id:
            values['name'] = _("%s's New Lead", discuss_channel.livechat_visitor_id.display_name)
            values['visitor_ids'] = [(4, discuss_channel.livechat_visitor_id.id)]
        return values

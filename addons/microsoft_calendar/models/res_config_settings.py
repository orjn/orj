# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cal_microsoft_client_id = fields.Char("Microsoft Client_id", config_parameter='microsoft_calendar_client_id', default='')
    cal_microsoft_client_secret = fields.Char("Microsoft Client_key", config_parameter='microsoft_calendar_client_secret', default='')
    cal_microsoft_sync_paused = fields.Boolean("Microsoft Synchronization Paused", config_parameter='microsoft_calendar_sync_paused',
        help="Indicates if synchronization with Outlook Calendar is paused or not.")

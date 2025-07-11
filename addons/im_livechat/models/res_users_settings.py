# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResUsersSettings(models.Model):
    _inherit = 'res.users.settings'

    livechat_username = fields.Char("Livechat Username", help="This username will be used as your name in the livechat channels.")
    livechat_lang_ids = fields.Many2many(comodel_name='res.lang', string='Livechat languages',
                            help="These languages, in addition to your main language, will be used to assign you to Live Chat sessions.")

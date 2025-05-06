# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models


class MailTestCC(models.Model):
    _name = 'mail.test.cc'
    _description = "Test Email CC Thread"
    _inherit = ['mail.thread.cc']

    name = fields.Char()

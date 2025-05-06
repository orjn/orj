# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models, fields


class MailActivityType(models.Model):
    _inherit = "mail.activity.type"

    category = fields.Selection(selection_add=[('meeting', 'Meeting')])

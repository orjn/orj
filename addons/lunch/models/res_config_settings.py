# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    company_lunch_minimum_threshold = fields.Float(string="Maximum Allowed Overdraft", readonly=False, related='company_id.lunch_minimum_threshold')
    company_lunch_notify_message = fields.Html(string="Lunch notification message", readonly=False, related="company_id.lunch_notify_message")

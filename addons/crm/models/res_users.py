# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    target_sales_won = fields.Integer('Won in Opportunities Target')
    target_sales_done = fields.Integer('Activities Done Target')

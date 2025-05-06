# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import fields, models


class Resource(models.Model):
    _inherit = ['resource.resource']

    employee_skill_ids = fields.One2many(related='employee_id.employee_skill_ids')

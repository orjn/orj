# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models, fields


class User(models.Model):
    _inherit = ['res.users']

    employee_cars_count = fields.Integer(related='employee_id.employee_cars_count')

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['employee_cars_count']

    def action_open_employee_cars(self):
        return self.employee_id.action_open_employee_cars()

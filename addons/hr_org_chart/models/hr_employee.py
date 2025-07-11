# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class Employee(models.Model):
    _inherit = ["hr.employee"]

    subordinate_ids = fields.One2many('hr.employee', string='Subordinates', compute='_compute_subordinates', help="Direct and indirect subordinates",
                                      compute_sudo=True)
    is_subordinate = fields.Boolean(compute="_compute_is_subordinate", search="_search_is_subordinate")


class HrEmployeePublic(models.Model):
    _inherit = ["hr.employee.public"]

    subordinate_ids = fields.One2many('hr.employee.public', string='Subordinates', compute='_compute_subordinates', help="Direct and indirect subordinates",
                                      compute_sudo=True)
    is_subordinate = fields.Boolean(compute="_compute_is_subordinate", search="_search_is_subordinate")

# -*- coding: utf-8 -*-

from orj import models, fields, api
from orj.osv.expression import AND


class PosConfig(models.Model):
    _inherit = 'pos.config'

    basic_employee_ids = fields.Many2many(
        'hr.employee', 'pos_hr_basic_employee_hr_employee', string="Employees with basic access",
        help='If left empty, all employees can log in to PoS')
    advanced_employee_ids = fields.Many2many(
        'hr.employee', 'pos_hr_advanced_employee_hr_employee', string="Employees with manager access",
        help='If left empty, only Orj users have extended rights in PoS')

    def write(self, vals):
        if 'advanced_employee_ids' not in vals:
            vals['advanced_employee_ids'] = []
        vals['advanced_employee_ids'] += [(4, emp_id) for emp_id in self._get_group_pos_manager().users.employee_id.ids]
        return super().write(vals)

    @api.onchange('basic_employee_ids')
    def _onchange_basic_employee_ids(self):
        for employee in self.basic_employee_ids:
            if employee in self.advanced_employee_ids:
                if employee.user_id._has_group('point_of_sale.group_pos_manager'):
                    self.basic_employee_ids -= employee
                else:
                    self.advanced_employee_ids -= employee

    @api.onchange('advanced_employee_ids')
    def _onchange_advanced_employee_ids(self):
        for employee in self.advanced_employee_ids:
            if employee in self.basic_employee_ids:
                self.basic_employee_ids -= employee

    def _employee_domain(self, user_id):
        domain = self._check_company_domain(self.company_id)
        if len(self.basic_employee_ids) > 0:
            domain = AND([
                domain,
                ['|', ('user_id', '=', user_id), ('id', 'in', self.basic_employee_ids.ids + self.advanced_employee_ids.ids)]
            ])
        return domain

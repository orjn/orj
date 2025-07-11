# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models, _
from orj.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_hr_recruitment_new_colleagues = fields.Boolean('New Employees')
    kpi_hr_recruitment_new_colleagues_value = fields.Integer(compute='_compute_kpi_hr_recruitment_new_colleagues_value')

    def _compute_kpi_hr_recruitment_new_colleagues_value(self):
        if not self.env.user.has_group('hr_recruitment.group_hr_recruitment_user'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))

        self._calculate_company_based_kpi(
            'hr.employee',
            'kpi_hr_recruitment_new_colleagues_value',
        )

    def _compute_kpis_actions(self, company, user):
        res = super()._compute_kpis_actions(company, user)
        res['kpi_hr_recruitment_new_colleagues'] = f"hr.open_view_employee_list_my?menu_id={self.env.ref('hr.menu_hr_root').id}"
        return res

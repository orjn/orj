# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hourly_cost = fields.Monetary('Hourly Cost', currency_field='currency_id',
        groups="hr.group_hr_user", default=0.0)

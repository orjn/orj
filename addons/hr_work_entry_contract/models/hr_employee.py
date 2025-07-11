# -*- coding:utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def generate_work_entries(self, date_start, date_stop, force=False):
        date_start = fields.Date.to_date(date_start)
        date_stop = fields.Date.to_date(date_stop)

        if self:
            current_contracts = self._get_contracts(date_start, date_stop, states=['open', 'close'])
        else:
            current_contracts = self._get_all_contracts(date_start, date_stop, states=['open', 'close'])

        return current_contracts.generate_work_entries(date_start, date_stop, force=force)

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class StockRequestCount(models.TransientModel):
    _inherit = 'stock.request.count'

    accounting_date = fields.Date('Accounting Date')

    def _get_values_to_write(self):
        res = super()._get_values_to_write()
        if self.accounting_date:
            res['accounting_date'] = self.accounting_date
        return res

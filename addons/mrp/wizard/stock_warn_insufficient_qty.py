# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models


class StockWarnInsufficientQtyUnbuild(models.TransientModel):
    _name = 'stock.warn.insufficient.qty.unbuild'
    _inherit = 'stock.warn.insufficient.qty'
    _description = 'Warn Insufficient Unbuild Quantity'

    unbuild_id = fields.Many2one('mrp.unbuild', 'Unbuild')

    def _get_reference_document_company_id(self):
        return self.unbuild_id.company_id

    def action_done(self):
        self.ensure_one()
        return self.unbuild_id.action_unbuild()

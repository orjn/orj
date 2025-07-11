# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, models


class ReportStockRule(models.AbstractModel):
    _inherit = 'report.stock.report_stock_rule'

    @api.model
    def _get_routes(self, data):
        res = super(ReportStockRule, self)._get_routes(data)
        if data.get('so_route_ids'):
            res = self.env['stock.route'].browse(data['so_route_ids']) | res
        return res

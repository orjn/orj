# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom):
        res = super()._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom)
        if values.get('project_id'):
            res['project_id'] = values['project_id']
        return res

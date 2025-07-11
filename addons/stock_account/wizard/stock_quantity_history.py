# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models
from orj.tools.misc import format_datetime


class StockQuantityHistory(models.TransientModel):
    _inherit = 'stock.quantity.history'

    def open_at_date(self):
        active_model = self.env.context.get('active_model')
        if active_model == 'stock.valuation.layer':
            action = self.env["ir.actions.actions"]._for_xml_id("stock_account.stock_valuation_layer_action")
            action['views'] = [(self.env.ref('stock_account.stock_valuation_layer_valuation_at_date_tree_inherited').id, 'list'),
                               (self.env.ref('stock_account.stock_valuation_layer_form').id, 'form'),
                               (self.env.ref('stock_account.stock_valuation_layer_pivot').id, 'pivot'),
                               (self.env.ref('stock_account.stock_valuation_layer_graph').id, 'graph')]
            action['domain'] = [('create_date', '<=', self.inventory_datetime), ('product_id.is_storable', '=', True)]
            action['display_name'] = format_datetime(self.env, self.inventory_datetime)
            action['context'] = "{}"
            return action

        return super(StockQuantityHistory, self).open_at_date()

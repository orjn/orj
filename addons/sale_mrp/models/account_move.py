# -*- coding: utf-8 -*-

from orj import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _stock_account_get_anglo_saxon_price_unit(self):
        price_unit = super(AccountMoveLine, self)._stock_account_get_anglo_saxon_price_unit()

        so_line = self.sale_line_ids and self.sale_line_ids[-1] or False
        if so_line:
            # We give preference to the bom in the stock moves for the sale order lines
            # If there are changes in BOMs between the stock moves creation and the
            # invoice validation a wrong price will be taken
            boms = so_line.move_ids.filtered(lambda m: m.state != 'cancel').mapped('bom_line_id.bom_id').filtered(lambda b: b.type == 'phantom')
            if boms:
                bom = boms.filtered(lambda b: b.product_id == so_line.product_id or b.product_tmpl_id == so_line.product_id.product_tmpl_id)
                if not bom:
                    # In the case where the product has no direct component in its bom, it won't be present in the stock moves boms.
                    # We then take the first bom of the product.
                    bom = self.env['mrp.bom']._bom_find(products=so_line.product_id, company_id=so_line.company_id.id, bom_type='phantom')[so_line.product_id]
                is_line_reversing = self.move_id.move_type == 'out_refund'
                qty_to_invoice = self.product_uom_id._compute_quantity(self.quantity, self.product_id.uom_id)
                account_moves = so_line.invoice_lines.move_id.filtered(lambda m: m.state == 'posted' and bool(m.reversed_entry_id) == is_line_reversing)
                posted_invoice_lines = account_moves.line_ids.filtered(lambda l: l.display_type == 'cogs' and l.product_id == self.product_id and l.balance > 0)
                qty_invoiced = sum([x.product_uom_id._compute_quantity(x.quantity, x.product_id.uom_id) for x in posted_invoice_lines])
                reversal_cogs = posted_invoice_lines.move_id.reversal_move_ids.line_ids.filtered(lambda l: l.display_type == 'cogs' and l.product_id == self.product_id and l.balance > 0)
                qty_invoiced -= sum([line.product_uom_id._compute_quantity(line.quantity, line.product_id.uom_id) for line in reversal_cogs])

                moves = so_line.move_ids
                average_price_unit = 0
                components_qty = so_line._get_bom_component_qty(bom)
                storable_components = self.env['product.product'].search([('id', 'in', list(components_qty.keys())), ('is_storable', '=', True)])
                for product in storable_components:
                    factor = components_qty[product.id]['qty']
                    prod_moves = moves.filtered(lambda m: m.product_id == product)
                    prod_qty_invoiced = factor * qty_invoiced
                    prod_qty_to_invoice = factor * qty_to_invoice
                    product = product.with_company(self.company_id)
                    average_price_unit += factor * product._compute_average_price(prod_qty_invoiced, prod_qty_to_invoice, prod_moves, is_returned=is_line_reversing)
                price_unit = average_price_unit / bom.product_qty or price_unit
                price_unit = self.product_id.uom_id._compute_price(price_unit, self.product_uom_id)
        return price_unit

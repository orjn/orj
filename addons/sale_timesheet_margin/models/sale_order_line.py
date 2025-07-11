# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import api, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('analytic_line_ids.amount', 'qty_delivered_method')
    def _compute_purchase_price(self):
        timesheet_sols = self.filtered(
            lambda sol: sol.qty_delivered_method == 'timesheet' and not sol.product_id.standard_price
        )
        super(SaleOrderLine, self - timesheet_sols)._compute_purchase_price()
        if timesheet_sols:
            group_amount = self.env['account.analytic.line']._read_group(
                [('so_line', 'in', timesheet_sols.ids), ('project_id', '!=', False)],
                ['so_line'],
                ['amount:sum', 'unit_amount:sum'])
            mapped_sol_timesheet_amount = {
                so_line.id: - amount_sum / unit_amount_sum if unit_amount_sum else 0.0
                for so_line, amount_sum, unit_amount_sum in group_amount
            }
            for line in timesheet_sols:
                line = line.with_company(line.company_id)
                product_cost = mapped_sol_timesheet_amount.get(line.id, line.product_id.standard_price)
                product_uom = line.product_uom or line.product_id.uom_id
                if (
                    product_uom != line.company_id.project_time_mode_id
                    and product_uom.category_id.id == line.company_id.project_time_mode_id.category_id.id
                ):
                    product_cost = product_uom._compute_quantity(
                        product_cost,
                        line.company_id.project_time_mode_id
                    )

                line.purchase_price = line._convert_to_sol_currency(
                    product_cost, line.product_id.cost_currency_id)

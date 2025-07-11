# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.fields import Command
from orj.tests import tagged

from orj.addons.sale_loyalty.tests.common import TestSaleCouponCommon


@tagged('post_install', '-at_install')
class TestSaleAutoInvoice(TestSaleCouponCommon):

    def test_automatic_invoice_on_zero_amount_order(self):
        self.env['ir.config_parameter'].sudo().set_param('sale.automatic_invoice', 'True')
        # Create a loyalty program with 100% discount
        self.env['loyalty.program'].sudo().create({
            'name': '100discount',
            'program_type': 'promo_code',
            'rule_ids': [
                Command.create({
                    'code': "100dis",
                    'minimum_amount': 0,
                })
            ],
            'reward_ids': [
                Command.create({
                    'discount': 100,
                }),
            ],
        })
        # Add order line to order
        self.env["sale.order.line"].create({
            'order_id': self.empty_order.id,
            'product_id': self.product_A.id,
            'product_uom_qty': 1,
            'price_unit': 200,
        })
        # Apply discount
        self._apply_promo_code(self.empty_order, '100dis')
        self.empty_order._validate_order()
        self.assertTrue(
            self.empty_order.invoice_ids,
            "Invoices should be generated for orders with zero total amount",
        )

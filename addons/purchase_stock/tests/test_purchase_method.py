# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj.tests.common import TransactionCase, tagged

@tagged('-at_install', 'post_install')
class TestPurchaseMethod(TransactionCase):
    def test_product_purchase_method_with_receive_as_default_purchase_method(self):
        self.env['ir.default'].set('product.template', 'purchase_method', 'receive', company_id=True)

        product = self.env['product.product'].create({'name': 'product_test'})
        self.assertEqual(product.purchase_method, 'receive')

        product.write({'type': 'service'})
        self.assertEqual(product.purchase_method, 'purchase')

        product.write({'type': 'consu'})
        self.assertEqual(product.purchase_method, 'receive')

    def test_product_purchase_method_with_purchase_as_default_purchase_method(self):
        self.env['ir.default'].set('product.template', 'purchase_method', 'purchase', company_id=True)

        product = self.env['product.product'].create({'name': 'product_test'})
        self.assertEqual(product.purchase_method, 'purchase')

        product.write({'type': 'service'})
        self.assertEqual(product.purchase_method, 'purchase')

        product.write({'type': 'consu'})
        self.assertEqual(product.purchase_method, 'purchase')

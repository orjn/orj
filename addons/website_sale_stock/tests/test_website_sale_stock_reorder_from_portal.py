# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import Command
from orj.tests import tagged
from orj.tests.common import HttpCase

from orj.addons.website_sale_stock.tests.common import WebsiteSaleStockCommon


@tagged('post_install', '-at_install')
class TestWebsiteSaleStockReorderFromPortal(HttpCase, WebsiteSaleStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['website'].get_current_website().enabled_portal_reorder_button = True

        cls.available_product = cls._create_product(name='available_product')
        cls.unavailable_product = cls._create_product(name='unavailable_product')
        cls.partially_available_product = cls._create_product(
            name='partially_available_product'
        )
        user_admin = cls.env.ref('base.user_admin')
        order = cls.env['sale.order'].create({
            'partner_id': user_admin.partner_id.id,
            'state': 'sale',
            'order_line': [
                Command.create({
                    'product_id': cls.available_product.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_id': cls.unavailable_product.id,
                    'product_uom_qty': 1,
                }),
                Command.create({
                    'product_id': cls.partially_available_product.id,
                    'product_uom_qty': 2,
                })
            ]
        })
        order.message_subscribe(user_admin.partner_id.ids)

        cls._add_product_qty_to_wh(cls.available_product.id, 10, 8)
        cls._add_product_qty_to_wh(cls.partially_available_product.id, 1.0, 8)

    def test_website_sale_stock_reorder_from_portal_stock(self):
        self.start_tour("/", 'website_sale_stock_reorder_from_portal', login='admin')

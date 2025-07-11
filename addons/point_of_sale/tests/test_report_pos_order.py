# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
import orj

from orj.addons.point_of_sale.tests.common import TestPoSCommon

@orj.tests.tagged('post_install', '-at_install')
class TestReportPoSOrder(TestPoSCommon):

    def setUp(self):
        super(TestReportPoSOrder, self).setUp()
        self.config = self.basic_config

    def test_report_pos_order_0(self):
        """Test the margin and price_total of a PoS Order with no taxes."""
        product1 = self.create_product('Product 1', self.categ_basic, 150)
        self.categ_all = self.env['pos.category'].search([])
        product1.write({'pos_categ_ids': [orj.Command.set(self.categ_all.ids)]})

        self.open_new_session()
        session = self.pos_session
        self.env['pos.order'].create({
            'session_id': session.id,
            'lines': [
                (0, 0, {
                    'name': "OL/0001",
                    'product_id': product1.id,
                    'price_unit': 150,
                    'discount': 0,
                    'qty': 1.0,
                    'price_subtotal': 150,
                    'price_subtotal_incl': 150,
                })
            ],
            'amount_total': 150.0,
            'amount_tax': 0.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
        })
        # PoS Orders have negative IDs to avoid conflict, so reports[0] will correspond to the newest order
        reports = self.env['report.pos.order'].sudo().search([('product_id', '=', product1.id)], order='id')

        self.assertEqual(len(reports.ids), 1)
        self.assertEqual(reports[0].margin, 150)
        self.assertEqual(reports[0].price_total, 150)

    def test_report_pos_order_1(self):
        """Test the margin and price_total of a PoS Order with taxes."""

        product1 = self.create_product('Product 1', self.categ_basic, 150, self.taxes['tax10'].id)

        self.open_new_session()
        session = self.pos_session

        self.env['pos.order'].create({
            'session_id': session.id,
            'lines': [(0, 0, {
                'name': "OL/0001",
                'product_id': product1.id,
                'price_unit': 150,
                'discount': 0,
                'qty': 1.0,
                'price_subtotal': 150,
                'price_subtotal_incl': 165,
            }),],
            'amount_total': 165.0,
            'amount_tax': 15.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
        })

        # PoS Orders have negative IDs to avoid conflict, so reports[0] will correspond to the newest order
        reports = self.env['report.pos.order'].sudo().search([('product_id', '=', product1.id)], order='id')

        self.assertEqual(reports[0].margin, 150)
        self.assertEqual(reports[0].price_total, 165)

    def test_report_pos_order_2(self):
        """Test the margin and price_total of a PoS Order with discount and no taxes"""

        product1 = self.create_product('Product 1', self.categ_basic, 150)

        self.open_new_session()
        session = self.pos_session

        self.env['pos.order'].create({
            'session_id': session.id,
            'lines': [
                (0, 0, {
                    'name': "OL/0001",
                    'product_id': product1.id,
                    'price_unit': 150,
                    'discount': 10,
                    'qty': 1.0,
                    'price_subtotal': 135,
                    'price_subtotal_incl': 135,
                })
            ],
            'amount_total': 135.0,
            'amount_tax': 0.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
        })

        # PoS Orders have negative IDs to avoid conflict, so reports[0] will correspond to the newest order
        reports = self.env['report.pos.order'].sudo().search([('product_id', '=', product1.id)], order='id')

        self.assertEqual(reports[0].margin, 135)
        self.assertEqual(reports[0].price_total, 135)

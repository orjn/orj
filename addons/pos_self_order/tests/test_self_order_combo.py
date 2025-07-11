# Part of Orj. See LICENSE file for full copyright and licensing details.

import orj.tests
from orj.addons.pos_self_order.tests.self_order_common_test import SelfOrderCommonTest
from orj.addons.point_of_sale.tests.common_setup_methods import setup_product_combo_items
from orj.fields import Command


@orj.tests.tagged("post_install", "-at_install")
class TestSelfOrderCombo(SelfOrderCommonTest):
    def test_self_order_combo(self):
        setup_product_combo_items(self)
        self.env["product.combo.item"].create(
            {
                "product_id": self.desk_organizer.id,
                "extra_price": 0,
                "combo_id": self.desk_accessories_combo.id,
            }
        )
        self.pos_config.write({
            'self_ordering_default_user_id': self.pos_admin.id,
            'self_ordering_takeaway': False,
            'self_ordering_mode': 'mobile',
            'self_ordering_pay_after': 'each',
            'self_ordering_service_mode': 'counter',
        })
        self.pos_admin.groups_id += self.env.ref('account.group_account_invoice')
        self.pos_config.with_user(self.pos_user).open_ui()
        self.pos_config.current_session_id.set_opening_control(0, "")
        self_route = self.pos_config._get_self_order_route()

        self.start_tour(self_route, "self_combo_selector")
        order = self.env['pos.order'].search([], order='id desc', limit=1)
        self.assertEqual(len(order.lines), 4, "There should be 4 order lines - 1 combo parent and 3 combo lines")
        # check that the combo lines are correctly linked to each other
        parent_line_id = self.env['pos.order.line'].search([('product_id.name', '=', 'Office Combo'), ('order_id', '=', order.id)])
        combo_line_ids = self.env['pos.order.line'].search([('product_id.name', '!=', 'Office Combo'), ('order_id', '=', order.id)])
        self.assertEqual(parent_line_id.combo_line_ids, combo_line_ids, "The combo parent should have 3 combo lines")
        self.assertEqual(parent_line_id.qty, 2, "There should be 2 combo products")
        self.assertEqual(parent_line_id.qty, combo_line_ids[0].qty, "The quantities should match with the parent")

    def test_self_order_combo_categories(self):
        setup_product_combo_items(self)
        category = self.env['pos.category'].create({'name': 'Test Category'})
        self.env["product.product"].create(
            {
                "available_in_pos": True,
                "list_price": 10,
                "name": "Test Combo",
                "type": "combo",
                'pos_categ_ids': category.ids,
                "combo_ids": self.desks_combo,
            }
        )

        self.pos_config.write({
            'self_ordering_default_user_id': self.pos_admin.id,
            'self_ordering_takeaway': False,
            'self_ordering_mode': 'mobile',
            'limit_categories': True,
            'iface_available_categ_ids': category.ids,
        })
        self.pos_config.with_user(self.pos_user).open_ui()
        self.pos_config.current_session_id.set_opening_control(0, "")
        self_route = self.pos_config._get_self_order_route()

        self.start_tour(self_route, "self_combo_selector_category")

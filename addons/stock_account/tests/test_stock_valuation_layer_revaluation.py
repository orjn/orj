# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.exceptions import UserError
from orj.tests import Form
from orj.addons.stock_account.tests.test_stockvaluation import _create_accounting_data
from orj.addons.stock_account.tests.test_stockvaluationlayer import TestStockValuationCommon


class TestStockValuationLayerRevaluation(TestStockValuationCommon):
    @classmethod
    def setUpClass(cls):
        super(TestStockValuationLayerRevaluation, cls).setUpClass()
        cls.stock_input_account, cls.stock_output_account, cls.stock_valuation_account, cls.expense_account, cls.stock_journal = _create_accounting_data(cls.env)
        cls.product1.write({
            'property_account_expense_id': cls.expense_account.id,
        })
        cls.product1.categ_id.write({
            'property_valuation': 'real_time',
            'property_stock_account_input_categ_id': cls.stock_input_account.id,
            'property_stock_account_output_categ_id': cls.stock_output_account.id,
            'property_stock_valuation_account_id': cls.stock_valuation_account.id,
            'property_stock_journal': cls.stock_journal.id,
        })

        cls.product1.categ_id.property_valuation = 'real_time'

    def test_stock_valuation_layer_revaluation_avco(self):
        self.product1.categ_id.property_cost_method = 'average'
        context = {
            'default_product_id': self.product1.id,
            'default_company_id': self.env.company.id,
            'default_added_value': 0.0
        }
        # Quantity of product1 is zero, raise
        with self.assertRaises(UserError):
            Form(self.env['stock.valuation.layer.revaluation'].with_context(context)).save()

        self._make_in_move(self.product1, 10, unit_cost=2)
        self._make_in_move(self.product1, 10, unit_cost=4)

        self.assertEqual(self.product1.standard_price, 3)
        self.assertEqual(self.product1.quantity_svl, 20)

        old_layers = self.env['stock.valuation.layer'].search([('product_id', '=', self.product1.id)], order="create_date desc, id desc")

        self.assertEqual(len(old_layers), 2)
        self.assertEqual(old_layers[0].remaining_value, 40)

        revaluation_wizard = Form(self.env['stock.valuation.layer.revaluation'].with_context(context))
        revaluation_wizard.added_value = 20
        revaluation_wizard.account_id = self.stock_valuation_account
        revaluation_wizard.save().action_validate_revaluation()

        # Check standard price change
        self.assertEqual(self.product1.standard_price, 4)
        self.assertEqual(self.product1.quantity_svl, 20)

        # Check the creation of stock.valuation.layer
        new_layer = self.env['stock.valuation.layer'].search([('product_id', '=', self.product1.id)], order="create_date desc, id desc", limit=1)
        self.assertEqual(new_layer.value, 20)

        # Check the remaing value of current layers
        self.assertEqual(old_layers[0].remaining_value, 50)
        self.assertEqual(sum(slv.remaining_value for slv in old_layers), 80)

        # Check account move
        self.assertTrue(bool(new_layer.account_move_id))
        self.assertEqual(len(new_layer.account_move_id.line_ids), 2)

        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("debit")), 20)
        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("credit")), 20)

        credit_lines = [l for l in new_layer.account_move_id.line_ids if l.credit > 0]
        self.assertEqual(len(credit_lines), 1)
        self.assertEqual(credit_lines[0].account_id.id, self.stock_valuation_account.id)

    def test_stock_valuation_layer_revaluation_avco_rounding(self):
        self.product1.categ_id.property_cost_method = 'average'
        context = {
            'default_product_id': self.product1.id,
            'default_company_id': self.env.company.id,
            'default_added_value': 0.0
        }
        # Quantity of product1 is zero, raise
        with self.assertRaises(UserError):
            Form(self.env['stock.valuation.layer.revaluation'].with_context(context)).save()

        self._make_in_move(self.product1, 1, unit_cost=1)
        self._make_in_move(self.product1, 1, unit_cost=1)
        self._make_in_move(self.product1, 1, unit_cost=1)

        self.assertEqual(self.product1.standard_price, 1)
        self.assertEqual(self.product1.quantity_svl, 3)

        old_layers = self.env['stock.valuation.layer'].search([('product_id', '=', self.product1.id)], order="create_date desc, id desc")

        self.assertEqual(len(old_layers), 3)
        self.assertEqual(old_layers[0].remaining_value, 1)

        revaluation_wizard = Form(self.env['stock.valuation.layer.revaluation'].with_context(context))
        revaluation_wizard.added_value = 1
        revaluation_wizard.account_id = self.stock_valuation_account
        revaluation_wizard.save().action_validate_revaluation()

        # Check standard price change
        self.assertEqual(self.product1.standard_price, 1.33)
        self.assertEqual(self.product1.quantity_svl, 3)

        # Check the creation of stock.valuation.layer
        new_layer = self.env['stock.valuation.layer'].search([('product_id', '=', self.product1.id)], order="create_date desc, id desc", limit=1)
        self.assertEqual(new_layer.value, 1)

        # Check the remaing value of current layers
        self.assertEqual(sum(slv.remaining_value for slv in old_layers), 4)
        self.assertTrue(1.34 in old_layers.mapped("remaining_value"))

        # Check account move
        self.assertTrue(bool(new_layer.account_move_id))
        self.assertEqual(len(new_layer.account_move_id.line_ids), 2)

        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("debit")), 1)
        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("credit")), 1)

        credit_lines = [l for l in new_layer.account_move_id.line_ids if l.credit > 0]
        self.assertEqual(len(credit_lines), 1)
        self.assertEqual(credit_lines[0].account_id.id, self.stock_valuation_account.id)

    def test_stock_valuation_layer_revaluation_avco_rounding_2_digits(self):
        """
        Check that the rounding of the new price (cost) is equivalent to the rounding of the standard price (cost)
        The check is done indirectly via the layers valuations.
        If correct => rounding method is correct too
        """
        self.product1.categ_id.property_cost_method = 'average'

        self.env['decimal.precision'].search([
            ('name', '=', 'Product Price'),
        ]).digits = 2
        self.product1.write({'standard_price': 0})

        # First Move
        self.product1.write({'standard_price': 0.022})
        self._make_in_move(self.product1, 10000)

        self.assertEqual(self.product1.standard_price, 0.02)
        self.assertEqual(self.product1.quantity_svl, 10000)

        layer = self.product1.stock_valuation_layer_ids
        self.assertEqual(layer.value, 200)

        # Second Move
        self.product1.write({'standard_price': 0.053})

        self.assertEqual(self.product1.standard_price, 0.05)
        self.assertEqual(self.product1.quantity_svl, 10000)

        layers = self.product1.stock_valuation_layer_ids
        self.assertEqual(layers[0].value, 200)
        self.assertEqual(layers[1].value, 300)

    def test_stock_valuation_layer_revaluation_avco_rounding_5_digits(self):
        """
        Check that the rounding of the new price (cost) is equivalent to the rounding of the standard price (cost)
        The check is done indirectly via the layers valuations.
        If correct => rounding method is correct too
        """
        self.product1.categ_id.property_cost_method = 'average'

        self.env['decimal.precision'].search([
            ('name', '=', 'Product Price'),
        ]).digits = 5

        # First Move
        self.product1.write({'standard_price': 0.00875})
        self._make_in_move(self.product1, 10000)

        self.assertEqual(self.product1.standard_price, 0.00875)
        self.assertEqual(self.product1.quantity_svl, 10000)

        layer = self.product1.stock_valuation_layer_ids
        self.assertEqual(layer.value, 87.5)

        # Second Move
        self.product1.write({'standard_price': 0.00975})

        self.assertEqual(self.product1.standard_price, 0.00975)
        self.assertEqual(self.product1.quantity_svl, 10000)

        layers = self.product1.stock_valuation_layer_ids
        self.assertEqual(layers[0].value, 87.5)
        self.assertEqual(layers[1].value, 10)

    def test_stock_valuation_layer_revaluation_fifo(self):
        self.product1.categ_id.property_cost_method = 'fifo'
        context = {
            'default_product_id': self.product1.id,
            'default_company_id': self.env.company.id,
            'default_added_value': 0.0
        }
        # Quantity of product1 is zero, raise
        with self.assertRaises(UserError):
            Form(self.env['stock.valuation.layer.revaluation'].with_context(context)).save()

        self._make_in_move(self.product1, 10, unit_cost=2)
        self._make_in_move(self.product1, 10, unit_cost=4)

        self.assertEqual(self.product1.standard_price, 3)
        self.assertEqual(self.product1.quantity_svl, 20)

        old_layers = self.env['stock.valuation.layer'].search([('product_id', '=', self.product1.id)], order="create_date desc, id desc")

        self.assertEqual(len(old_layers), 2)
        self.assertEqual(old_layers[0].remaining_value, 40)

        revaluation_wizard = Form(self.env['stock.valuation.layer.revaluation'].with_context(context))
        revaluation_wizard.added_value = 20
        revaluation_wizard.account_id = self.stock_valuation_account
        revaluation_wizard.save().action_validate_revaluation()

        self.assertEqual(self.product1.standard_price, 4)

        # Check the creation of stock.valuation.layer
        new_layer = self.env['stock.valuation.layer'].search([('product_id', '=', self.product1.id)], order="create_date desc, id desc", limit=1)
        self.assertEqual(new_layer.value, 20)

        # Check the remaing value of current layers
        self.assertEqual(old_layers[0].remaining_value, 50)
        self.assertEqual(sum(slv.remaining_value for slv in old_layers), 80)

        # Check account move
        self.assertTrue(bool(new_layer.account_move_id))
        self.assertTrue(len(new_layer.account_move_id.line_ids), 2)

        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("debit")), 20)
        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("credit")), 20)

        credit_lines = [l for l in new_layer.account_move_id.line_ids if l.credit > 0]
        self.assertEqual(len(credit_lines), 1)

    def test_stock_valuation_layer_revaluation_partial(self):
        """ Only adjust the valuation on some of the layers for a product """
        self.product1.categ_id.property_cost_method = 'fifo'

        product2 = self.env['product.product'].create({
            'name': 'product2',
            'is_storable': True,
            'categ_id': self.env.ref('product.product_category_all').id,
        })

        self._make_in_move(self.product1, 5, unit_cost=4)
        self._make_in_move(self.product1, 10, unit_cost=4)
        self._make_in_move(self.product1, 5, unit_cost=8)
        self._make_in_move(product2, 10, unit_cost=4)

        self.assertEqual(self.product1.standard_price, 5)
        self.assertEqual(self.product1.quantity_svl, 20)

        old_layers = self.env['stock.valuation.layer'].search([('product_id', '=', self.product1.id)], order="create_date desc, id desc")

        self.assertEqual(len(old_layers), 3)
        self.assertEqual(old_layers.mapped("remaining_value"), [40, 40, 20])

        # Adjusting layers for multiple products at once: raise
        with self.assertRaises(UserError):
            Form(self.env['stock.valuation.layer.revaluation'].with_context({
                'active_ids': self.env['stock.valuation.layer'].search([]).mapped("id"),
                'active_model': 'stock.valuation.layer'
            })).save()

        revaluation_wizard = Form(self.env['stock.valuation.layer.revaluation'].with_context({
            'active_ids': old_layers[0:2].ids,
            'active_model': 'stock.valuation.layer'
        }))
        revaluation_wizard.added_value = 30
        revaluation_wizard.account_id = self.stock_valuation_account
        revaluation_wizard.save().action_validate_revaluation()

        # Check standard price change
        self.assertEqual(self.product1.standard_price, 6.5)
        self.assertEqual(self.product1.quantity_svl, 20)

        # Check the creation of stock.valuation.layer
        new_layer = self.env['stock.valuation.layer'].search([('product_id', '=', self.product1.id)], order="create_date desc, id desc", limit=1)
        self.assertEqual(new_layer.value, 30)

        # Check the remaing value of current layers: only the adjusted layers should have changed
        # the added value should be impacted proportionally to the qty of each layer (+10 and +20)
        self.assertEqual(old_layers.mapped("remaining_value"), [50, 60, 20])

        # Check account move
        self.assertTrue(bool(new_layer.account_move_id))
        self.assertEqual(len(new_layer.account_move_id.line_ids), 2)

        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("debit")), 30)
        self.assertEqual(sum(new_layer.account_move_id.line_ids.mapped("credit")), 30)

        credit_lines = [l for l in new_layer.account_move_id.line_ids if l.credit > 0]
        self.assertEqual(len(credit_lines), 1)
        self.assertEqual(credit_lines[0].account_id.id, self.stock_valuation_account.id)

        self.assertIn(
            f"Affected valuation layers: {old_layers[1].reference} (id: {old_layers[1].id}) and {old_layers[0].reference} (id: {old_layers[0].id})",
            new_layer.account_move_id.line_ids[0].name
        )

        # Adjusting an adjustment layer: raise
        with self.assertRaises(UserError):
            Form(self.env['stock.valuation.layer.revaluation'].with_context({
                'active_ids': [new_layer.id],
                'active_model': 'stock.valuation.layer'
            })).save()

        # remove all products from the oldest layer
        self._make_out_move(self.product1, 5)
        self.assertEqual(old_layers[2].remaining_qty, 0)

        # Adjusting a layer with no remaining quantity: raise
        with self.assertRaises(UserError):
            Form(self.env['stock.valuation.layer.revaluation'].with_context({
                'active_ids': [old_layers[2].id],
                'active_model': 'stock.valuation.layer'
            })).save()

# -*- coding: utf-8 -*-
# pylint: disable=C0326
from orj import Command
from orj.addons.account.tests.common import AccountTestInvoicingCommon
from orj.tests import tagged, Form


@tagged('post_install', '-at_install')
class TestInvoiceTaxes(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_currency = cls.setup_other_currency('HRK')

        cls.percent_tax_1 = cls.env['account.tax'].create({
            'name': '21%',
            'amount_type': 'percent',
            'amount': 21,
            'sequence': 10,
        })
        cls.percent_tax_1_incl = cls.env['account.tax'].create({
            'name': '21% incl',
            'amount_type': 'percent',
            'amount': 21,
            'price_include_override': 'tax_included',
            'include_base_amount': True,
            'sequence': 20,
        })
        cls.percent_tax_2 = cls.env['account.tax'].create({
            'name': '12%',
            'amount_type': 'percent',
            'amount': 12,
            'sequence': 30,
        })
        cls.percent_tax_3_incl = cls.env['account.tax'].create({
            'name': '5% incl',
            'amount_type': 'percent',
            'amount': 5,
            'price_include_override': 'tax_included',
            'include_base_amount': True,
            'sequence': 40,
        })
        cls.group_tax = cls.env['account.tax'].create({
            'name': 'group 12% + 21%',
            'amount_type': 'group',
            'amount': 21,
            'children_tax_ids': [
                (4, cls.percent_tax_1_incl.id),
                (4, cls.percent_tax_2.id)
            ],
            'sequence': 40,
        })

        tax_report = cls.env['account.report'].create({
            'name': "Tax report",
            'country_id': cls.company_data['company'].country_id.id,
            'column_ids': [
                Command.create({
                    'name': "Balance",
                    'expression_label': 'balance',
                }),
            ],
        })

        tax_report_line = cls.env['account.report.line'].create({
            'name': 'test_tax_report_line',
            'report_id': tax_report.id,
            'sequence': 10,
            'expression_ids': [
                Command.create({
                    'label': 'balance',
                    'engine': 'tax_tags',
                    'formula': 'test_tax_report_line',
                }),
            ],
        })
        tax_tags = tax_report_line.expression_ids._get_matching_tags()
        cls.tax_tag_pos, cls.tax_tag_neg = tax_tags.sorted('tax_negate')

        base_report_line = cls.env['account.report.line'].create({
            'name': 'base_test_tax_report_line',
            'report_id': tax_report.id,
            'sequence': 10,
            'expression_ids': [
                Command.create({
                    'label': 'balance',
                    'engine': 'tax_tags',
                    'formula': 'base_test_tax_report_line',
                }),
            ],
        })
        base_tags = base_report_line.expression_ids._get_matching_tags()
        cls.base_tag_pos, cls.base_tag_neg = base_tags.sorted('tax_negate')

    def _create_invoice(self, taxes_per_line, inv_type='out_invoice', currency_id=False, invoice_payment_term_id=False):
        ''' Create an invoice on the fly.

        :param taxes_per_line: A list of tuple (price_unit, account.tax recordset)
        '''
        vals = {
            'move_type': inv_type,
            'partner_id': self.partner_a.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'xxxx',
                'quantity': 1,
                'price_unit': amount,
                'tax_ids': [(6, 0, taxes.ids)],
            }) for amount, taxes in taxes_per_line],
        }
        if currency_id:
            vals['currency_id'] = currency_id.id
        if invoice_payment_term_id:
            vals['invoice_payment_term_id'] = invoice_payment_term_id.id
        return self.env['account.move'].create(vals)

    def test_setting_tax_separately(self):
        ''' Test:
        price_unit | Taxes
        ------------------
        100        | 21%
        Expected:
        Tax         | Taxes     | Base      | Amount
        --------------------------------------------
        21%         | /         | 100       | 21
        '''
        invoice = self._create_invoice([(100, self.env['account.tax'])])
        invoice.invoice_line_ids[0].tax_ids = self.percent_tax_1
        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'), [
            {'name': self.percent_tax_1.name, 'tax_base_amount': 100, 'balance': -21, 'tax_ids': []},
        ])

    def test_one_tax_per_line(self):
        ''' Test:
        price_unit | Taxes
        ------------------
        100        | 21%
        121        | 21% incl
        100        | 12%

        Expected:
        Tax         | Taxes     | Base      | Amount
        --------------------------------------------
        21%         | /         | 100       | 21
        21% incl    | /         | 100       | 21
        12%         | /         | 100       | 12
        '''
        invoice = self._create_invoice([
            (100, self.percent_tax_1),
            (121, self.percent_tax_1_incl),
            (100, self.percent_tax_2),
        ])
        invoice.action_post()
        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id').sorted(lambda x: x.name), [
            {'name': self.percent_tax_2.name,       'tax_base_amount': 100, 'balance': -12, 'tax_ids': []},
            {'name': self.percent_tax_1.name,       'tax_base_amount': 100, 'balance': -21, 'tax_ids': []},
            {'name': self.percent_tax_1_incl.name,  'tax_base_amount': 100, 'balance': -21, 'tax_ids': []},
        ])

    def test_affecting_base_amount(self):
        ''' Test:
        price_unit | Taxes
        ------------------
        121        | 21% incl, 12%
        100        | 12%

        Expected:
        Tax         | Taxes     | Base      | Amount
        --------------------------------------------
        21% incl    | 12%       | 100       | 21
        12%         | /         | 121       | 14.52
        12%         | /         | 100       | 12
        '''
        invoice = self._create_invoice([
            (121, self.percent_tax_1_incl + self.percent_tax_2),
            (100, self.percent_tax_2),
        ])
        invoice.action_post()
        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id').sorted(lambda x: -x.balance), [
            {'name': self.percent_tax_1_incl.name,      'tax_base_amount': 100, 'balance': -21,      'tax_ids': [self.percent_tax_2.id]},
            {'name': self.percent_tax_2.name,           'tax_base_amount': 221, 'balance': -26.52,   'tax_ids': []},
        ])

    def test_group_of_taxes(self):
        ''' Test:
        price_unit | Taxes
        ------------------
        121        | 21% incl + 12%
        100        | 12%

        Expected:
        Tax         | Taxes     | Base      | Amount
        --------------------------------------------
        21% incl    | /         | 100       | 21
        12%         | 21% incl  | 121       | 14.52
        12%         | /         | 100       | 12
        '''
        invoice = self._create_invoice([
            (121, self.group_tax),
            (100, self.percent_tax_2),
        ])
        invoice.action_post()
        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id').sorted('balance'), [
            {'name': self.percent_tax_1_incl.name,      'tax_base_amount': 100.0,   'balance': -21.0,   'tax_ids': [self.percent_tax_2.id]},
            {'name': self.percent_tax_2.name,           'tax_base_amount': 121.0,   'balance': -14.52,  'tax_ids': []},
            {'name': self.percent_tax_2.name,           'tax_base_amount': 100.0,   'balance': -12.0,   'tax_ids': []},
        ])

    def _create_tax_tag(self, tag_name):
        return self.env['account.account.tag'].create({
            'name': tag_name,
            'applicability': 'taxes',
            'country_id': self.env.company.country_id.id,
        })

    def test_tax_repartition(self):
        inv_base_tag = self._create_tax_tag('invoice_base')
        inv_tax_tag_10 = self._create_tax_tag('invoice_tax_10')
        inv_tax_tag_90 = self._create_tax_tag('invoice_tax_90')
        ref_base_tag = self._create_tax_tag('refund_base')
        ref_tax_tag = self._create_tax_tag('refund_tax')

        account_1 = self.env['account.account'].create({'name': 'test1', 'code': 'test1', 'account_type': 'asset_current'})
        account_2 = self.env['account.account'].create({'name': 'test2', 'code': 'test2', 'account_type': 'asset_current'})

        tax = self.env['account.tax'].create({
            'name': "Tax with account",
            'amount_type': 'fixed',
            'type_tax_use': 'sale',
            'amount': 42,
            'invoice_repartition_line_ids': [
                (0,0, {
                    'repartition_type': 'base',
                    'tag_ids': [(4, inv_base_tag.id, 0)],
                }),

                (0,0, {
                    'factor_percent': 10,
                    'repartition_type': 'tax',
                    'account_id': account_1.id,
                    'tag_ids': [(4, inv_tax_tag_10.id, 0)],
                }),

                (0,0, {
                    'factor_percent': 90,
                    'repartition_type': 'tax',
                    'account_id': account_2.id,
                    'tag_ids': [(4, inv_tax_tag_90.id, 0)],
                }),
            ],
            'refund_repartition_line_ids': [
                (0,0, {
                    'repartition_type': 'base',
                    'tag_ids': [(4, ref_base_tag.id, 0)],
                }),

                (0,0, {
                    'factor_percent': 10,
                    'repartition_type': 'tax',
                    'tag_ids': [(4, ref_tax_tag.id, 0)],
                }),

                (0,0, {
                    'factor_percent': 90,
                    'repartition_type': 'tax',
                    'account_id': account_1.id,
                    'tag_ids': [(4, ref_tax_tag.id, 0)],
                }),
            ],
        })

        # Test invoice repartition
        invoice = self._create_invoice([(100, tax)], inv_type='out_invoice')
        invoice.action_post()

        self.assertEqual(len(invoice.line_ids), 4, "There should be 4 account move lines created for the invoice: payable, base and 2 tax lines")
        inv_base_line = invoice.line_ids.filtered(lambda x: not x.tax_repartition_line_id and x.account_id.account_type != 'asset_receivable')
        self.assertEqual(len(inv_base_line), 1, "There should be only one base line generated")
        self.assertEqual(abs(inv_base_line.balance), 100, "Base amount should be 100")
        self.assertEqual(inv_base_line.tax_tag_ids, inv_base_tag, "Base line should have received base tag")
        inv_tax_lines = invoice.line_ids.filtered(lambda x: x.tax_repartition_line_id.repartition_type == 'tax')
        self.assertEqual(len(inv_tax_lines), 2, "There should be two tax lines, one for each repartition line.")
        self.assertEqual(abs(inv_tax_lines.filtered(lambda x: x.account_id == account_1).balance), 4.2, "Tax line on account 1 should amount to 4.2 (10% of 42)")
        self.assertEqual(inv_tax_lines.filtered(lambda x: x.account_id == account_1).tax_tag_ids, inv_tax_tag_10, "Tax line on account 1 should have 10% tag")
        self.assertAlmostEqual(abs(inv_tax_lines.filtered(lambda x: x.account_id == account_2).balance), 37.8, 2, "Tax line on account 2 should amount to 37.8 (90% of 42)")
        self.assertEqual(inv_tax_lines.filtered(lambda x: x.account_id == account_2).tax_tag_ids, inv_tax_tag_90, "Tax line on account 2 should have 90% tag")

        # Test refund repartition
        refund = self._create_invoice([(100, tax)], inv_type='out_refund')
        refund.action_post()

        self.assertEqual(len(refund.line_ids), 4, "There should be 4 account move lines created for the refund: payable, base and 2 tax lines")
        ref_base_line = refund.line_ids.filtered(lambda x: not x.tax_repartition_line_id and x.account_id.account_type != 'asset_receivable')
        self.assertEqual(len(ref_base_line), 1, "There should be only one base line generated")
        self.assertEqual(abs(ref_base_line.balance), 100, "Base amount should be 100")
        self.assertEqual(ref_base_line.tax_tag_ids, ref_base_tag, "Base line should have received base tag")
        ref_tax_lines = refund.line_ids.filtered(lambda x: x.tax_repartition_line_id.repartition_type == 'tax')
        self.assertEqual(len(ref_tax_lines), 2, "There should be two refund tax lines")
        self.assertEqual(abs(ref_tax_lines.filtered(lambda x: x.account_id == ref_base_line.account_id).balance), 4.2, "Refund tax line on base account should amount to 4.2 (10% of 42)")
        self.assertAlmostEqual(abs(ref_tax_lines.filtered(lambda x: x.account_id == account_1).balance), 37.8, 2, "Refund tax line on account 1 should amount to 37.8 (90% of 42)")
        self.assertEqual(ref_tax_lines.mapped('tax_tag_ids'), ref_tax_tag, "Refund tax lines should have the right tag")

    def test_division_tax(self):
        '''
        Test that when using division tax, with percentage amount
        100% any change on price unit is correctly reflected on
        the whole move.

        Complete scenario:
            - Create a division tax, 100% amount, included in price.
            - Create an invoice, with only the mentioned tax
            - Change price_unit of the aml
            - Total price of the move should change as well
        '''

        sale_tax = self.env['account.tax'].create({
            'name': 'tax',
            'type_tax_use': 'sale',
            'amount_type': 'division',
            'amount': 100,
            'price_include_override': 'tax_included',
            'include_base_amount': True,
        })
        invoice = self._create_invoice([(100, sale_tax)])
        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'), [{
            'name': sale_tax.name,
            'tax_base_amount': 0.0,
            'balance': -100,
        }])
        # change price unit, everything should change as well
        with Form(invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line_edit:
                line_edit.price_unit = 200

        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'), [{
            'name': sale_tax.name,
            'tax_base_amount': 0.0,
            'balance': -200,
        }])

    def test_misc_journal_entry_tax_tags_sale(self):
        sale_tax = self.env['account.tax'].create({
            'name': 'tax',
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'amount': 10,
            'invoice_repartition_line_ids': [
                (0, 0, {
                    'repartition_type': 'base',
                    'tag_ids': [(6, 0, self.base_tag_pos.ids)],
                }),
                (0, 0, {
                    'repartition_type': 'tax',
                    'tag_ids': [(6, 0, self.tax_tag_pos.ids)],
                }),
            ],
            'refund_repartition_line_ids': [
                (0, 0, {
                    'repartition_type': 'base',
                    'tag_ids': [(6, 0, self.base_tag_neg.ids)],
                }),
                (0, 0, {
                    'repartition_type': 'tax',
                    'tag_ids': [(6, 0, self.tax_tag_neg.ids)],
                }),
            ],
        })

        inv_tax_rep_ln = sale_tax.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax')
        ref_tax_rep_ln = sale_tax.refund_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax')

        # === Tax in debit ===

        move_form = Form(self.env['account.move'], view='account.view_move_form')
        move_form.ref = 'azerty'

        # Debit base tax line.
        with move_form.line_ids.new() as credit_line:
            credit_line.name = 'debit_line_1'
            credit_line.account_id = self.company_data['default_account_revenue']
            credit_line.debit = 1000.0
            credit_line.tax_ids.clear()
            credit_line.tax_ids.add(sale_tax)


        # Balance the journal entry.
        with move_form.line_ids.new() as credit_line:
            credit_line.name = 'balance'
            credit_line.account_id = self.company_data['default_account_revenue']
            credit_line.credit = 1100.0

        move = move_form.save()

        self.assertRecordValues(move.line_ids.sorted('balance'), [
            {'balance': -1100.0,    'tax_ids': [],              'tax_tag_ids': [],                      'tax_base_amount': 0,       'tax_repartition_line_id': False,               'tax_tag_invert': False},
            {'balance': 100.0,      'tax_ids': [],              'tax_tag_ids': self.tax_tag_neg.ids,    'tax_base_amount': 1000,    'tax_repartition_line_id': ref_tax_rep_ln.id,   'tax_tag_invert': False},
            {'balance': 1000.0,     'tax_ids': sale_tax.ids,    'tax_tag_ids': self.base_tag_neg.ids,   'tax_base_amount': 0,       'tax_repartition_line_id': False,               'tax_tag_invert': False},
        ])

        # === Tax in credit ===

        move_form = Form(self.env['account.move'], view='account.view_move_form')
        move_form.ref = 'azerty'

        # Debit base tax line.
        with move_form.line_ids.new() as credit_line:
            credit_line.name = 'debit_line_1'
            credit_line.account_id = self.company_data['default_account_revenue']
            credit_line.credit = 1000.0
            credit_line.tax_ids.clear()
            credit_line.tax_ids.add(sale_tax)

        # Balance the journal entry.
        with move_form.line_ids.new() as debit_line:
            debit_line.name = 'balance'
            debit_line.account_id = self.company_data['default_account_revenue']
            debit_line.debit = 1100.0

        move = move_form.save()

        self.assertRecordValues(move.line_ids.sorted('balance'), [
            {'balance': -1000.0,    'tax_ids': sale_tax.ids,    'tax_tag_ids': self.base_tag_pos.ids,   'tax_base_amount': 0,       'tax_repartition_line_id': False,                'tax_tag_invert': True},
            {'balance': -100.0,     'tax_ids': [],              'tax_tag_ids': self.tax_tag_pos.ids,    'tax_base_amount': 1000,    'tax_repartition_line_id': inv_tax_rep_ln.id,    'tax_tag_invert': True},
            {'balance': 1100.0,     'tax_ids': [],              'tax_tag_ids': [],                      'tax_base_amount': 0,       'tax_repartition_line_id': False,                'tax_tag_invert': False},
        ])

    def test_misc_journal_entry_tax_tags_purchase(self):
        purch_tax = self.env['account.tax'].create({
            'name': 'tax',
            'type_tax_use': 'purchase',
            'amount_type': 'percent',
            'amount': 10,
            'invoice_repartition_line_ids': [
                (0, 0, {
                    'repartition_type': 'base',
                    'tag_ids': [(6, 0, self.base_tag_pos.ids)],
                }),
                (0, 0, {
                    'repartition_type': 'tax',
                    'tag_ids': [(6, 0, self.tax_tag_pos.ids)],
                }),
            ],
            'refund_repartition_line_ids': [
                (0, 0, {
                    'repartition_type': 'base',
                    'tag_ids': [(6, 0, self.base_tag_neg.ids)],
                }),
                (0, 0, {
                    'repartition_type': 'tax',
                    'tag_ids': [(6, 0, self.tax_tag_neg.ids)],
                }),
            ],
        })

        inv_tax_rep_ln = purch_tax.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax')
        ref_tax_rep_ln = purch_tax.refund_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax')

        # === Tax in debit ===

        move_form = Form(self.env['account.move'])
        move_form.ref = 'azerty'

        # Debit base tax line.
        with move_form.line_ids.new() as credit_line:
            credit_line.name = 'debit_line_1'
            credit_line.account_id = self.company_data['default_account_revenue']
            credit_line.debit = 1000.0
            credit_line.tax_ids.clear()
            credit_line.tax_ids.add(purch_tax)

        # Balance the journal entry.
        with move_form.line_ids.new() as credit_line:
            credit_line.name = 'balance'
            credit_line.account_id = self.company_data['default_account_revenue']
            credit_line.credit = 1100.0

        move = move_form.save()

        self.assertRecordValues(move.line_ids.sorted('balance'), [
            {'balance': -1100.0,    'tax_ids': [],              'tax_tag_ids': [],                      'tax_base_amount': 0,       'tax_repartition_line_id': False,                'tax_tag_invert': False},
            {'balance': 100.0,      'tax_ids': [],              'tax_tag_ids': self.tax_tag_pos.ids,    'tax_base_amount': 1000,    'tax_repartition_line_id': inv_tax_rep_ln.id,    'tax_tag_invert': False},
            {'balance': 1000.0,     'tax_ids': purch_tax.ids,   'tax_tag_ids': self.base_tag_pos.ids,   'tax_base_amount': 0,       'tax_repartition_line_id': False,                'tax_tag_invert': False},
        ])

        # === Tax in credit ===

        move_form = Form(self.env['account.move'])
        move_form.ref = 'azerty'

        # Debit base tax line.
        with move_form.line_ids.new() as credit_line:
            credit_line.name = 'debit_line_1'
            credit_line.account_id = self.company_data['default_account_revenue']
            credit_line.credit = 1000.0
            credit_line.tax_ids.clear()
            credit_line.tax_ids.add(purch_tax)

        # Balance the journal entry.
        with move_form.line_ids.new() as debit_line:
            debit_line.name = 'balance'
            debit_line.account_id = self.company_data['default_account_revenue']
            debit_line.debit = 1100.0

        move = move_form.save()

        self.assertRecordValues(move.line_ids.sorted('balance'), [
            {'balance': -1000.0,    'tax_ids': purch_tax.ids,   'tax_tag_ids': self.base_tag_neg.ids,   'tax_base_amount': 0,       'tax_repartition_line_id': False,                'tax_tag_invert': True},
            {'balance': -100.0,     'tax_ids': [],              'tax_tag_ids': self.tax_tag_neg.ids,    'tax_base_amount': 1000,    'tax_repartition_line_id': ref_tax_rep_ln.id,    'tax_tag_invert': True},
            {'balance': 1100.0,     'tax_ids': [],              'tax_tag_ids': [],                      'tax_base_amount': 0,       'tax_repartition_line_id': False,                'tax_tag_invert': False},
        ])

    def test_misc_entry_tax_group_signs(self):
        """ Tests sign inversion of the tags on misc operations made with tax
        groups.
        """
        def _create_group_of_taxes(tax_type):
            # We use asymmetric tags between the child taxes to avoid shadowing errors
            child1_sale_tax = self.env['account.tax'].create({
                'sequence': 1,
                'name': 'child1_%s' % tax_type,
                'type_tax_use': 'none',
                'amount_type': 'percent',
                'amount': 5,
                'invoice_repartition_line_ids': [
                    (0, 0, {
                        'repartition_type': 'base',
                        'tag_ids': [(6, 0, self.base_tag_pos.ids)],
                    }),
                    (0, 0, {
                        'repartition_type': 'tax',
                        'tag_ids': [(6, 0, self.tax_tag_pos.ids)],
                    }),
                ],
                'refund_repartition_line_ids': [
                    (0, 0, {'repartition_type': 'base'}),
                    (0, 0, {'repartition_type': 'tax'}),
                ],
            })
            child2_sale_tax = self.env['account.tax'].create({
                'sequence': 2,
                'name': 'child2_%s' % tax_type,
                'type_tax_use': 'none',
                'amount_type': 'percent',
                'amount': 10,
                'invoice_repartition_line_ids': [
                    (0, 0, {'repartition_type': 'base'}),
                    (0, 0, {'repartition_type': 'tax'}),
                ],
                'refund_repartition_line_ids': [
                    (0, 0, {
                        'repartition_type': 'base',
                        'tag_ids': [(6, 0, self.base_tag_neg.ids)],
                    }),
                    (0, 0, {
                        'repartition_type': 'tax',
                        'tag_ids': [(6, 0, self.tax_tag_neg.ids)],
                    }),
                ],
            })
            return self.env['account.tax'].create({
                'name': 'group_%s' % tax_type,
                'type_tax_use': tax_type,
                'amount_type': 'group',
                'amount': 10,
                'children_tax_ids':[(6,0,[child1_sale_tax.id, child2_sale_tax.id])]
            })

        def _create_misc_operation(tax, tax_field):
            with Form(self.env['account.move'], view='account.view_move_form') as move_form:
                for line_field in ('debit', 'credit'):
                    line_amount = tax_field == line_field and 1000 or 1150
                    with move_form.line_ids.new() as line_form:
                        line_form.name = '%s_line' % line_field
                        line_form.account_id = self.company_data['default_account_revenue']
                        line_form.debit = line_field == 'debit' and line_amount or 0
                        line_form.credit = line_field == 'credit' and line_amount or 0

                        if tax_field == line_field:
                            line_form.tax_ids.clear()
                            line_form.tax_ids.add(tax)

            return move_form.save()

        sale_group = _create_group_of_taxes('sale')
        purchase_group = _create_group_of_taxes('purchase')

        # Sale tax on debit: use refund repartition
        debit_sale_move = _create_misc_operation(sale_group, 'debit')
        self.assertRecordValues(debit_sale_move.line_ids.sorted('balance'), [
            {'balance': -1150.0,    'tax_ids': [],                  'tax_tag_ids': [],                      'tax_base_amount': 0},
            {'balance': 50.0,       'tax_ids': [],                  'tax_tag_ids': [],                      'tax_base_amount': 1000},
            {'balance': 100.0,      'tax_ids': [],                  'tax_tag_ids': self.tax_tag_neg.ids,    'tax_base_amount': 1000},
            {'balance': 1000.0,     'tax_ids': sale_group.ids,      'tax_tag_ids': self.base_tag_neg.ids,   'tax_base_amount': 0},
        ])

        # Sale tax on credit: use invoice repartition
        credit_sale_move = _create_misc_operation(sale_group, 'credit')
        self.assertRecordValues(credit_sale_move.line_ids.sorted('balance'), [
            {'balance': -1000.0,    'tax_ids': sale_group.ids,      'tax_tag_ids': self.base_tag_pos.ids,   'tax_base_amount': 0},
            {'balance': -100.0,     'tax_ids': [],                  'tax_tag_ids': [],                      'tax_base_amount': 1000},
            {'balance': -50.0,      'tax_ids': [],                  'tax_tag_ids': self.tax_tag_pos.ids,    'tax_base_amount': 1000},
            {'balance': 1150.0,     'tax_ids': [],                  'tax_tag_ids': [],                      'tax_base_amount': 0},
        ])

        # Purchase tax on debit: use invoice repartition
        debit_purchase_move = _create_misc_operation(purchase_group, 'debit')
        self.assertRecordValues(debit_purchase_move.line_ids.sorted('balance'), [
            {'balance': -1150.0,    'tax_ids': [],                  'tax_tag_ids': [],                      'tax_base_amount': 0},
            {'balance': 50.0,       'tax_ids': [],                  'tax_tag_ids': self.tax_tag_pos.ids,    'tax_base_amount': 1000},
            {'balance': 100.0,      'tax_ids': [],                  'tax_tag_ids': [],                      'tax_base_amount': 1000},
            {'balance': 1000.0,     'tax_ids': purchase_group.ids,  'tax_tag_ids': self.base_tag_pos.ids,   'tax_base_amount': 0},
        ])

        # Purchase tax on credit: use refund repartition
        credit_purchase_move = _create_misc_operation(purchase_group, 'credit')
        self.assertRecordValues(credit_purchase_move.line_ids.sorted('balance'), [
            {'balance': -1000.0,    'tax_ids': purchase_group.ids,  'tax_tag_ids': self.base_tag_neg.ids,   'tax_base_amount': 0},
            {'balance': -100.0,     'tax_ids': [],                  'tax_tag_ids': self.tax_tag_neg.ids,    'tax_base_amount': 1000},
            {'balance': -50.0,      'tax_ids': [],                  'tax_tag_ids': [],                      'tax_base_amount': 1000},
            {'balance': 1150.0,     'tax_ids': [],                  'tax_tag_ids': [],                      'tax_base_amount': 0},
        ])

    def test_tax_calculation_foreign_currency_large_quantity(self):
        ''' Test:
        Foreign currency with rate of 1.1726 and tax of 21%
        price_unit | Quantity  | Taxes
        ------------------
        2.82       | 20000     | 21% not incl
        '''
        self.env['res.currency.rate'].create({
            'name': '2018-01-01',
            'rate': 1.1726,
            'currency_id': self.other_currency.id,
            'company_id': self.env.company.id,
        })
        self.other_currency.rounding = 0.05

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_a.id,
            'currency_id': self.other_currency.id,
            'invoice_date': '2018-01-01',
            'date': '2018-01-01',
            'invoice_line_ids': [(0, 0, {
                'name': 'xxxx',
                'quantity': 20000,
                'price_unit': 2.82,
                'tax_ids': [(6, 0, self.percent_tax_1.ids)],
            })]
        })

        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'), [{
            'tax_base_amount': 48098.24,    # 20000 * 2.82 / 1.1726
            'credit': 10100.63,             # tax_base_amount * 0.21
        }])

    def test_ensure_no_unbalanced_entry(self):
        ''' Ensure to not create an unbalanced journal entry when saving. '''
        self.env['res.currency.rate'].create({
            'name': '2018-01-01',
            'rate': 0.654065014,
            'currency_id': self.other_currency.id,
            'company_id': self.env.company.id,
        })
        self.other_currency.rounding = 0.05

        invoice = self._create_invoice([
            (5, self.percent_tax_3_incl),
            (10, self.percent_tax_3_incl),
            (50, self.percent_tax_3_incl),
        ], currency_id=self.other_currency, invoice_payment_term_id=self.pay_terms_a)
        invoice.action_post()

    def test_tax_calculation_multi_currency(self):
        self.env['res.currency.rate'].create({
            'name': '2018-01-01',
            'rate': 0.273748,
            'currency_id': self.other_currency.id,
            'company_id': self.env.company.id,
        })
        self.other_currency.rounding = 0.01

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_a.id,
            'currency_id': self.other_currency.id,
            'invoice_date': '2018-01-01',
            'date': '2018-01-01',
            'invoice_line_ids': [(0, 0, {
                'name': 'xxxx',
                'quantity': 1,
                'price_unit': 155.32,
                'tax_ids': [(6, 0, self.percent_tax_1.ids)],
            })]
        })

        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'), [{
            'tax_base_amount': 567.38,      # 155.32 * 1 / (1 / 0.273748)
            'balance': -119.16,             # tax_base_amount * 0.21
        }])

        self.assertRecordValues(invoice.line_ids.filtered(lambda l: not l.name), [{
            'balance': 686.54,
        }])

        with Form(invoice) as invoice_form:
            invoice_form.currency_id = self.other_currency

        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'), [{
            'tax_base_amount': 567.38,
            'balance': -119.16,
        }])

        self.assertRecordValues(invoice.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_receivable'), [{
            'balance': 686.54,
        }])

    def test_fixed_tax_with_zero_price(self):
        fixed_tax = self.env['account.tax'].create({
            'name': 'Test 5 fixed',
            'amount_type': 'fixed',
            'amount': 5,
        })
        invoice = self._create_invoice([
            (0, fixed_tax),
        ])
        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'), [{
            'credit': 5.0,
            'debit': 0,
        }])
        invoice.invoice_line_ids.quantity = 2
        self.assertRecordValues(invoice.line_ids.filtered('tax_line_id'), [{
            'credit': 10.0,
            'debit': 0,
        }])

    def test_tax_repartition_lines_dispatch_amount_1(self):
        """ Ensure the tax amount is well dispatched to the repartition lines and the rounding errors are well managed.
        The 5% tax is applied on 1 so the total tax amount should be 0.05.
        However, there are 10 tax repartition lines of 0.05 * 0.1 = 0.005 that will be rounded to 0.01.
        The test checks the tax amount doesn't become 10 * 0.01 = 0.1 instead of 0.05.
        """
        base_tax_rep = Command.create({'repartition_type': 'base', 'factor_percent': 100.0})
        tax_reps = [Command.create({'repartition_type': 'tax', 'factor_percent': 10.0})] * 10
        tax = self.env['account.tax'].create({
            'name': "test_tax_repartition_lines_dispatch_amount_1",
            'amount_type': 'percent',
            'amount': 5.0,
            'invoice_repartition_line_ids': [base_tax_rep] + tax_reps,
            'refund_repartition_line_ids': [base_tax_rep] + tax_reps,
        })
        invoice = self._create_invoice([(1, tax)])
        self.assertRecordValues(invoice, [{
            'amount_untaxed': 1.0,
            'amount_tax': 0.05,
            'amount_total': 1.05,
        }])
        self.assertRecordValues(
            invoice.line_ids.filtered('tax_line_id').sorted('balance'),
            [{'balance': -0.01}] * 5,
        )

    def test_tax_repartition_lines_dispatch_amount_2(self):
        """ Ensure the tax amount is well dispatched to the repartition lines and the rounding errors are well managed.
        The 5% tax is applied on 1 so the total tax amount should be 0.05 but the distribution is 100 - 100 = 0%.
        So at the end, the tax amount is 0.
        However, there are 10 positive tax repartition lines of 0.05 * 0.1 = 0.005 that will be rounded to 0.01
        and one negative repartition line of 50% and 2 of 25% that will give respectively 0.025 ~= 0.03 and 0.0125 ~= 0.01.
        The test checks the tax amount is still zero at the end.
        """
        base_tax_rep = Command.create({'repartition_type': 'base', 'factor_percent': 100.0})
        plus_tax_reps = [Command.create({'repartition_type': 'tax', 'factor_percent': 10.0})] * 10
        neg_tax_reps = [
            Command.create({'repartition_type': 'tax', 'factor_percent': percent})
            for percent in (-50, -25, -25)
        ]
        tax = self.env['account.tax'].create({
            'name': "test_tax_repartition_lines_dispatch_amount_2",
            'amount_type': 'percent',
            'amount': 5.0,
            'invoice_repartition_line_ids': [base_tax_rep] + plus_tax_reps + neg_tax_reps,
            'refund_repartition_line_ids': [base_tax_rep] + plus_tax_reps + neg_tax_reps,
        })
        invoice = self._create_invoice([(1, tax)], inv_type='out_refund')
        self.assertRecordValues(invoice, [{
            'amount_untaxed': 1.0,
            'amount_tax': 0.0,
            'amount_total': 1.0,
        }])
        self.assertRecordValues(
            invoice.line_ids.filtered('tax_line_id').sorted('balance'),
            [{'balance': -0.03}] + [{'balance': -0.01}] * 2 + [{'balance': 0.01}] * 5,
        )

    def test_tax_line_amount_currency_modification_auto_balancing(self):
        date = '2017-01-01'
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'date': date,
            'partner_id': self.partner_a.id,
            'invoice_date': date,
            'currency_id': self.other_currency.id,
            'invoice_payment_term_id': self.pay_terms_a.id,
            'invoice_line_ids': [
                Command.create({
                    'name': self.product_a.name,
                    'product_id': self.product_a.id,
                    'product_uom_id': self.product_a.uom_id.id,
                    'quantity': 1.0,
                    'price_unit': 1000,
                    'tax_ids': self.product_a.taxes_id.ids,
                }),
                Command.create({
                    'name': self.product_b.name,
                    'product_id': self.product_b.id,
                    'product_uom_id': self.product_b.uom_id.id,
                    'quantity': 1.0,
                    'price_unit': 200,
                    'tax_ids': self.product_b.taxes_id.ids,
                }),
            ]
        })
        receivable_line = move.line_ids.filtered(lambda line: line.display_type == 'payment_term')
        self.assertRecordValues(receivable_line, [
            {'amount_currency': 1410.00, 'balance': 705.00},
        ])

        # Modify the tax lines
        tax_lines = move.line_ids.filtered(lambda line: line.display_type == 'tax').sorted('amount_currency')
        self.assertRecordValues(tax_lines, [
            {'amount_currency': -180.00, 'balance': -90.00},
            {'amount_currency': -30.00, 'balance': -15.00},
        ])
        tax_lines[0].amount_currency = -180.03
        # The following line should not cause the move to become unbalanced; i.e. there should be no error
        tax_lines[1].amount_currency = -29.99

        self.assertRecordValues(receivable_line, [
            {'amount_currency': 1410.02, 'balance': 705.02},
        ])

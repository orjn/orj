# -*- coding: utf-8 -*-
from orj.addons.account.tests.common import AccountTestInvoicingCommon
from orj.tests import tagged
from orj import fields


@tagged('post_install', '-at_install')
class TestAccountDebitNote(AccountTestInvoicingCommon):

    def test_00_debit_note_out_invoice(self):
        """ Debit Note of a regular Customer Invoice"""
        invoice = self.init_invoice('out_invoice', products=self.product_a+self.product_b)
        invoice.action_post()
        move_debit_note_wiz = self.env['account.debit.note'].with_context(active_model="account.move",
                                                                       active_ids=invoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'no reason',
            'copy_lines': True,
        })
        move_debit_note_wiz.create_debit()

        # Search for the original invoice
        debit_note = self.env['account.move'].search([('debit_origin_id', '=', invoice.id)])
        debit_note.ensure_one()
        self.assertEqual(len(debit_note.invoice_line_ids), 2, "Should have copied the invoice lines")
        self.assertEqual(debit_note.move_type, 'out_invoice', 'Type of debit note should be the same as the original invoice')
        self.assertEqual(debit_note.state, 'draft', 'We should create debit notes in draft state')

    def test_10_debit_note_in_refund(self):
        """ Debit Note of a vendor refund (is a regular vendor bill) """
        invoice = self.init_invoice('in_refund', products=self.product_a+self.product_b)
        invoice.action_post()
        move_debit_note_wiz = self.env['account.debit.note'].with_context(active_model="account.move",
                                                                          active_ids=invoice.ids).create({
            'date': fields.Date.from_string('2019-02-01'),
            'reason': 'in order to cancel refund',
        })
        move_debit_note_wiz.create_debit()

        # Search for the original invoice
        debit_note = self.env['account.move'].search([('debit_origin_id', '=', invoice.id)])
        debit_note.ensure_one()

        self.assertFalse(debit_note.invoice_line_ids, 'We should not copy lines by default on debit notes')
        self.assertEqual(debit_note.move_type, 'in_invoice', 'Type of debit note should not be refund anymore')
        self.assertEqual(debit_note.state, 'draft', 'We should create debit notes in draft state')

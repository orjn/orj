# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from orj import fields
from orj.tests import tagged

from .common import TestEsEdiTbaiCommon


@tagged('external_l10n', 'post_install', '-at_install', '-standard', 'external')
class TestEdiTbaiWebServices(TestEsEdiTbaiCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Invoice name are tracked by the web-services so this constant tries to get a new unique invoice name at each
        # execution.
        cls.today = datetime.now()
        cls.time_name = cls.today.strftime('%H%M%S')

        cls.out_invoice = cls.env['account.move'].create({
            'name': f'INV/{cls.time_name}',
            'move_type': 'out_invoice',
            'partner_id': cls.partner_a.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': cls.product_a.id,
                'price_unit': 1000.0,
                'quantity': 5,
                'discount': 20.0,
                'tax_ids': [(6, 0, cls._get_tax_by_xml_id('s_iva21b').ids)],
            })],
        })
        cls.out_invoice.action_post()

        cls.in_invoice = cls.env['account.move'].create({
            'name': f'BILL{cls.time_name}',
            'ref': f'REFBILL{cls.time_name}',
            'move_type': 'in_invoice',
            'partner_id': cls.partner_a.id,
            'invoice_date': fields.Date.to_string(cls.today.date()),
            'invoice_line_ids': [(0, 0, {
                'product_id': cls.product_a.id,
                'price_unit': 1000.0,
                'quantity': 5,
                'discount': 20.0,
                'tax_ids': [(6, 0, cls._get_tax_by_xml_id('p_iva10_bc').ids)],
            })],
        })
        cls.in_invoice.action_post()

        cls.moves = cls.out_invoice + cls.in_invoice

    def test_edi_gipuzkoa(self):
        self._set_tax_agency('gipuzkoa')

        self._get_invoice_send_wizard(self.out_invoice).action_send_and_print()
        self.assertEqual(self.out_invoice.l10n_es_tbai_state, 'sent')
        self.assertTrue(self.out_invoice.l10n_es_tbai_post_document_id.xml_attachment_id)

        self.in_invoice.l10n_es_tbai_send_bill()
        self.assertEqual(self.in_invoice.l10n_es_tbai_state, 'sent')
        self.assertTrue(self.in_invoice.l10n_es_tbai_post_document_id.xml_attachment_id)

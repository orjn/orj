# -*- coding: utf-8 -*-

from orj.addons.l10n_account_edi_ubl_cii_tests.tests.common import TestUBLCommon
from orj.tests import tagged

@tagged('post_install_l10n', 'post_install', '-at_install')
class TestCIIUS(TestUBLCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_1 = cls.env['res.partner'].create({
            'name': "partner_1",
            'country_id': cls.env.ref('base.us').id,
        })

        cls.partner_2 = cls.env['res.partner'].create({
            'name': "partner_2",
            'country_id': cls.env.ref('base.us').id,
        })

        cls.tax_0 = cls.env['account.tax'].create({
            'name': "Tax 0%",
            'type_tax_use': 'purchase',
            'amount': 0,
        })

    def test_print_pdf_us_company(self):
        """ Even for a US company, a printed PDF should contain a Factur-X xml
        """
        invoice = self._generate_move(
            self.partner_1,
            self.partner_2,
            move_type='out_invoice',
            invoice_line_ids=[
                {
                    'product_id': self.product_a.id,
                    'quantity': 2.0,
                    'price_unit': 990.0,
                },
            ],
        )

        # Default XML acting as the default EDI
        edi_attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', invoice.id)
        ])
        self.assertEqual(edi_attachment.name, "factur-x.xml")

    def test_import_facturx_us_company(self):
        """ Even for a US company, importing a PDF containing a Factur-X xml
        should create the correct invoice
        """
        self._assert_imported_invoice_from_file(
            subfolder='tests/test_files/from_factur-x_doc',
            filename='facturx_invoice_negative_amounts.xml',
            invoice_vals={
                'amount_total': 100,
                'amount_tax': 0,
                'invoice_lines': [{'price_subtotal': x} for x in (-5, 10, 60, 30, 5)],
            },
            move_type='in_refund'
        )

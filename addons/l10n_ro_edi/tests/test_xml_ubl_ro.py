from orj import Command
from orj.addons.l10n_account_edi_ubl_cii_tests.tests.common import TestUBLCommon
from orj.exceptions import UserError
from orj.tests import tagged


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestUBLRO(TestUBLCommon):

    @classmethod
    @TestUBLCommon.setup_country('ro')
    def setUpClass(cls):
        super().setUpClass()
        cls.company_data['company'].write({
            'country_id': cls.env.ref('base.ro').id,  # needed to compute peppol_endpoint based on VAT
            'state_id': cls.env.ref('base.RO_B').id,
            'name': 'Hudson Construction',
            'city': 'SECTOR1',
            'zip': '010101',
            'vat': 'RO1234567897',
            'phone': '+40 123 456 789',
            'street': "Strada Kunst, 3",
        })

        cls.env['res.partner.bank'].create({
            'acc_type': 'iban',
            'partner_id': cls.company_data['company'].partner_id.id,
            'acc_number': 'RO98RNCB1234567890123456',
        })

        cls.partner_a = cls.env['res.partner'].create({
            'country_id': cls.env.ref('base.ro').id,
            'state_id': cls.env.ref('base.RO_B').id,
            'name': 'Roasted Romanian Roller',
            'city': 'SECTOR3',
            'zip': '010101',
            'vat': 'RO1234567897',
            'phone': '+40 123 456 780',
            'street': "Rolling Roast, 88",
            'bank_ids': [(0, 0, {'acc_number': 'RO98RNCB1234567890123456'})],
            'ref': 'ref_partner_a',
            'invoice_edi_format': 'ciusro',
        })

        cls.tax_19 = cls.env['account.tax'].create({
            'name': 'tax_19',
            'amount_type': 'percent',
            'amount': 19,
            'type_tax_use': 'sale',
            'country_id': cls.env.ref('base.ro').id,
        })

    ####################################################
    # Test export - import
    ####################################################

    def create_move(self, move_type, send=True, **kwargs):
        return self._generate_move(
            self.env.company.partner_id,
            self.partner_a,
            send=send,
            move_type=move_type,
            invoice_line_ids=[
                {
                    'name': 'Test Product A',
                    'product_id': self.product_a.id,
                    'price_unit': 500.0,
                    'tax_ids': [Command.set(self.tax_19.ids)],
                },
                {
                    'name': 'Test Product B',
                    'product_id': self.product_b.id,
                    'price_unit': 1000.0,
                    'tax_ids': [Command.set(self.tax_19.ids)],
                },
            ],
            **kwargs
        )

    def get_attachment(self, move):
        self.assertTrue(move.ubl_cii_xml_id)
        self.assertEqual(move.ubl_cii_xml_id.name[-11:], "cius_ro.xml")
        return move.ubl_cii_xml_id

    def test_export_invoice(self):
        invoice = self.create_move("out_invoice", currency_id=self.company.currency_id.id)
        attachment = self.get_attachment(invoice)
        self._assert_invoice_attachment(attachment, xpaths=None, expected_file_path='from_orj/ciusro_out_invoice.xml')

    def test_export_credit_note(self):
        refund = self.create_move("out_refund", currency_id=self.company.currency_id.id)
        attachment = self.get_attachment(refund)
        self._assert_invoice_attachment(attachment, xpaths=None, expected_file_path='from_orj/ciusro_out_refund.xml')

    def test_export_invoice_different_currency(self):
        invoice = self.create_move("out_invoice")
        attachment = self.get_attachment(invoice)
        self._assert_invoice_attachment(attachment, xpaths=None, expected_file_path='from_orj/ciusro_out_invoice_different_currency.xml')

    def test_export_invoice_without_country_code_prefix_in_vat(self):
        self.company_data['company'].write({'vat': '1234567897'})
        self.partner_a.write({'vat': False})
        invoice = self.create_move("out_invoice", currency_id=self.company.currency_id.id)
        attachment = self.get_attachment(invoice)
        self._assert_invoice_attachment(attachment, xpaths=None, expected_file_path='from_orj/ciusro_out_invoice_no_prefix_vat.xml')

    def test_export_no_vat_but_have_company_registry(self):
        self.company_data['company'].write({'vat': False, 'company_registry': 'RO1234567897'})
        invoice = self.create_move("out_invoice", currency_id=self.company.currency_id.id)
        attachment = self.get_attachment(invoice)
        self._assert_invoice_attachment(attachment, xpaths=None, expected_file_path='from_orj/ciusro_out_invoice.xml')

    def test_export_no_vat_but_have_company_registry_without_prefix(self):
        self.company_data['company'].write({'vat': False, 'company_registry': '1234567897'})
        self.partner_a.write({'vat': False})
        invoice = self.create_move("out_invoice", currency_id=self.company.currency_id.id)
        attachment = self.get_attachment(invoice)
        self._assert_invoice_attachment(attachment, xpaths=None, expected_file_path='from_orj/ciusro_out_invoice_no_prefix_vat.xml')

    def test_export_no_vat_and_no_company_registry_raises_error(self):
        self.company_data['company'].write({'vat': False, 'company_registry': False})
        invoice = self.create_move("out_invoice", send=False)
        with self.assertRaisesRegex(UserError, "doesn't have a VAT nor Company ID"):
            invoice._generate_and_send(allow_fallback_pdf=False, mail_template_id=self.move_template.id)

    def test_export_constraints(self):
        self.company_data['company'].company_registry = False
        for required_field in ('city', 'street', 'state_id', 'vat'):
            prev_val = self.company_data["company"][required_field]
            self.company_data["company"][required_field] = False
            invoice = self.create_move("out_invoice", send=False)
            with self.assertRaisesRegex(UserError, "required"):
                invoice._generate_and_send(allow_fallback_pdf=False, mail_template_id=self.move_template.id)
            self.company_data["company"][required_field] = prev_val

        self.company_data["company"].city = "Bucharest"
        invoice = self.create_move("out_invoice", send=False)
        with self.assertRaisesRegex(UserError, "city name must be 'SECTORX'"):
            invoice._generate_and_send(allow_fallback_pdf=False, mail_template_id=self.move_template.id)

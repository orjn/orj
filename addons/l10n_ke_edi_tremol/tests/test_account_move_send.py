from datetime import timedelta

from orj import fields
from orj.exceptions import UserError
from orj.tests import tagged
from orj.addons.account.tests.test_account_move_send import TestAccountMoveSendCommon


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestKEAccountMoveSend(TestAccountMoveSendCommon):

    @classmethod
    @TestAccountMoveSendCommon.setup_country('ke')
    def setUpClass(cls):
        super().setUpClass()

    def test_sent_to_fiscal_device(self):
        invoice = self.init_invoice("out_invoice", amounts=[1000], post=True, partner=self.partner_a)
        # Write data as if the invoice was successfully sent to fiscal device
        invoice.write({
            'l10n_ke_cu_invoice_number': 'test_ke_invoice_number',
            'l10n_ke_cu_serial_number': 'test_ke_serial_number',
            'l10n_ke_cu_qrcode': 'test_ke_qrcode',
            'l10n_ke_cu_datetime': fields.Datetime.now() - timedelta(days=1),
        })

        wizard = self.create_send_and_print(invoice)
        self.assertFalse(wizard.alerts)
        wizard.action_send_and_print()

        self.assertTrue(invoice.invoice_pdf_report_id)

    def test_not_sent_to_fiscal_device_but_allow_fallback(self):
        invoice = self.init_invoice("out_invoice", amounts=[1000], post=True, partner=self.partner_a)
        wizard = self.create_send_and_print(invoice)
        self.assertTrue('l10n_ke_edi_tremol_warning_moves' in wizard.alerts)
        wizard.action_send_and_print(allow_fallback_pdf=True)

        # The PDF is not generated but a proforma.
        self.assertFalse(invoice.invoice_pdf_report_id)
        self.assertTrue(self.env['ir.attachment'].search([
            ('name', '=', invoice._get_invoice_proforma_pdf_report_filename()),
        ]))

    def test_not_sent_to_fiscal_device_raises(self):
        invoice = self.init_invoice("out_invoice", amounts=[1000], post=True, partner=self.partner_a)
        wizard = self.create_send_and_print(invoice)
        self.assertTrue('l10n_ke_edi_tremol_warning_moves' in wizard.alerts)
        with self.assertRaisesRegex(UserError, wizard._get_l10n_ke_edi_tremol_warning_message(invoice)):
            wizard.action_send_and_print()

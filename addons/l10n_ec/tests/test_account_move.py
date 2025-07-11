# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields
from orj.addons.account_edi.tests.common import AccountEdiTestCommon
from orj.exceptions import UserError
from orj.tests import tagged, Form

from orj.addons.account.tests.common import AccountTestInvoicingCommon


@tagged('post_install_l10n', 'post_install', '-at_install')
class TestEcAccountMove(AccountTestInvoicingCommon):

    @classmethod
    @AccountEdiTestCommon.setup_country('ec')
    def setUpClass(cls):
        super().setUpClass()

    def test_document_number_credit_note(self):
        """
        Test that when creating a Credit Note in the Purchase journal with a partner not from Ecuador a document number can be anything
        If the partner is from Ecuador, an error should be raised
        """
        self.partner_a.country_id = self.env.ref('base.us')
        self.partner_b.country_id = self.env.ref('base.ec')

        document_credit_note = self.env['l10n_latam.document.type'].search([
            ('internal_type', '=', 'credit_note'),
            ('country_id', '=', self.env.ref('base.ec').id),
            ('l10n_ec_check_format', '=', True),
        ], limit=1)
        move_form = Form(self.env['account.move'].with_context(default_move_type='in_refund'))
        move_form.partner_id = self.partner_a
        move_form.l10n_latam_document_type_id = document_credit_note
        move_form.invoice_date = fields.Date.from_string('2024-08-08')
        move_form.l10n_latam_document_number = '123456'

        move_form.save()

        with self.assertRaises(UserError, msg="Ecuadorian Document (04) Nota de Crédito must be like 001-001-123456789"):
            move_form.partner_id = self.partner_b

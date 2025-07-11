# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj.tests import tagged
from orj.addons.account.tests.common import AccountTestInvoicingCommon
from orj.exceptions import UserError


@tagged('post_install_l10n', 'post_install', '-at_install')
class PaymentReferenceTest(AccountTestInvoicingCommon):
    """
    All references validated with the reference calculator by Nordea Bank
    http://www.nordea.fi/en/corporate-customers/payments/invoicing-and-payments/reference-number-calculator.html
    """

    @classmethod
    @AccountTestInvoicingCommon.setup_country('fi')
    def setUpClass(cls):
        super().setUpClass()

        cls.invoice = cls.init_invoice('out_invoice', products=cls.product_a+cls.product_b)

    def test_payment_reference_fi(self):

        compute = self.invoice.compute_payment_reference_finnish

        # Common
        self.assertEqual('1232', compute('INV123'))
        self.assertEqual('1326', compute('132'))
        self.assertEqual('1290', compute('ABC1B2B9C'))

        # Insufficient
        self.assertEqual('1119', compute('-1'))
        self.assertEqual('1106', compute('0'))
        self.assertEqual('1261', compute('26'))

        # Excess length
        self.assertEqual('12345678901234567894', compute('123456789012345678901234567890'))

        # Invalid
        with self.assertRaises(UserError):
            compute('QWERTY')

    def test_payment_reference_rf(self):

        compute = self.invoice.compute_payment_reference_finnish_rf

        # Common
        self.assertEqual('RF111232', compute('INV123'))
        self.assertEqual('RF921326', compute('132'))
        self.assertEqual('RF941290', compute('ABC1B2B9C'))

        # Insufficient
        self.assertEqual('RF551119', compute('-1'))
        self.assertEqual('RF181106', compute('0'))
        self.assertEqual('RF041261', compute('26'))

        # Excess length
        self.assertEqual('RF0912345678901234567894', compute('123456789012345678901234567890'))

        # Invalid
        with self.assertRaises(UserError):
            compute('QWERTY')

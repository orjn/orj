# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.tests import tagged

from orj.addons.payment_mercado_pago.tests.common import MercadoPagoCommon


@tagged('post_install', '-at_install')
class TestPaymentProvider(MercadoPagoCommon):

    def test_incompatible_with_unsupported_currencies(self):
        """ Test that Mercado Pago providers are filtered out from compatible providers when the
        currency is not supported. """
        compatible_providers = self.env['payment.provider']._get_compatible_providers(
            self.company_id, self.partner.id, self.amount, currency_id=self.env.ref('base.AFN').id
        )
        self.assertNotIn(self.provider, compatible_providers)

# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.addons.payment.tests.common import PaymentCommon


class PaymentDemoCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.provider = cls._prepare_provider(code='demo')

        cls.notification_data = {
            'reference': cls.reference,
            'payment_details': '1234',
            'simulated_state': 'done',
        }

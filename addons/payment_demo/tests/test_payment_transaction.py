# Part of Orj. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

from orj.tests import tagged
from orj.tools import mute_logger

from orj.addons.payment_demo.tests.common import PaymentDemoCommon
from orj.addons.payment.tests.http_common import PaymentHttpCommon


@tagged('-at_install', 'post_install')
class TestPaymentTransaction(PaymentDemoCommon, PaymentHttpCommon):

    def test_processing_notification_data_sets_transaction_pending(self):
        """ Test that the transaction state is set to 'pending' when the notification data indicate
        a pending payment. """
        tx = self._create_transaction('direct')
        tx._process_notification_data(dict(self.notification_data, simulated_state='pending'))
        self.assertEqual(tx.state, 'pending')

    def test_processing_notification_data_authorizes_transaction(self):
        """ Test that the transaction state is set to 'authorize' when the notification data
        indicate a successful payment and manual capture is enabled. """
        self.provider.capture_manually = True
        tx = self._create_transaction('direct')
        tx._process_notification_data(self.notification_data)
        self.assertEqual(tx.state, 'authorized')

    def test_processing_notification_data_confirms_transaction(self):
        """ Test that the transaction state is set to 'done' when the notification data indicate a
        successful payment. """
        tx = self._create_transaction('direct')
        tx._process_notification_data(self.notification_data)
        self.assertEqual(tx.state, 'done')

    def test_processing_notification_data_cancels_transaction(self):
        """ Test that the transaction state is set to 'cancel' when the notification data indicate
        an unsuccessful payment. """
        tx = self._create_transaction('direct')
        tx._process_notification_data(dict(self.notification_data, simulated_state='cancel'))
        self.assertEqual(tx.state, 'cancel')

    def test_processing_notification_data_sets_transaction_in_error(self):
        """ Test that the transaction state is set to 'error' when the notification data indicate
        an error during the payment. """
        tx = self._create_transaction('direct')
        tx._process_notification_data(dict(self.notification_data, simulated_state='error'))
        self.assertEqual(tx.state, 'error')

    def test_processing_notification_data_tokenizes_transaction(self):
        """ Test that the transaction is tokenized when it was requested and the notification data
        include token data. """
        tx = self._create_transaction('direct', tokenize=True)
        with patch(
            'orj.addons.payment_demo.models.payment_transaction.PaymentTransaction'
            '._demo_tokenize_from_notification_data'
        ) as tokenize_mock:
            tx._process_notification_data(self.notification_data)
        self.assertEqual(tokenize_mock.call_count, 1)

    @mute_logger('orj.addons.payment_demo.models.payment_transaction')
    def test_processing_notification_data_propagates_simulated_state_to_token(self):
        """ Test that the simulated state of the notification data is set on the token when
        processing notification data. """
        for counter, state in enumerate(['pending', 'done', 'cancel', 'error']):
            tx = self._create_transaction(
                'direct', reference=f'{self.reference}-{counter}', tokenize=True
            )
            tx._process_notification_data(dict(self.notification_data, simulated_state=state))
            self.assertEqual(tx.token_id.demo_simulated_state, state)

    def test_making_a_payment_request_propagates_token_simulated_state_to_transaction(self):
        """ Test that the simulated state of the token is set on the transaction when making a
        payment request. """
        for counter, state in enumerate(['pending', 'done', 'cancel', 'error']):
            tx = self._create_transaction(
                'direct', reference=f'{self.reference}-{counter}'
            )
            tx.token_id = self._create_token(demo_simulated_state=state)
            tx._send_payment_request()
            self.assertEqual(tx.state, tx.token_id.demo_simulated_state)

    def test_send_full_capture_request_does_not_create_capture_tx(self):
        self.provider.capture_manually = True
        source_tx = self._create_transaction(flow='direct', state='authorized')
        child_tx = source_tx._send_capture_request()
        self.assertFalse(
            child_tx, msg="Full capture should not create a child transaction."
        )

    def test_send_partial_capture_request_creates_capture_tx(self):
        self.provider.capture_manually = True
        source_tx = self._create_transaction(flow='direct', state='authorized')
        child_tx = source_tx._send_capture_request(amount_to_capture=10)
        self.assertTrue(
            source_tx.child_transaction_ids,
            msg="Partial capture should create a child transaction and linked it to the source tx.",
        )
        self.assertEqual(
            child_tx.amount, 10, msg="Child transaction should have the requested amount."
        )

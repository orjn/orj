# Part of Orj. See LICENSE file for full copyright and licensing details.

import hmac
import logging
import pprint

from werkzeug.exceptions import Forbidden

from orj import http
from orj.exceptions import ValidationError
from orj.http import request

from orj.addons.payment_razorpay.const import HANDLED_WEBHOOK_EVENTS


_logger = logging.getLogger(__name__)


class RazorpayController(http.Controller):
    _webhook_url = '/payment/razorpay/webhook'

    @http.route(_webhook_url, type='http', methods=['POST'], auth='public', csrf=False)
    def razorpay_webhook(self):
        """ Process the notification data sent by Razorpay to the webhook.

        :return: An empty string to acknowledge the notification.
        :rtype: str
        """
        data = request.get_json_data()
        _logger.info("Notification received from Razorpay with data:\n%s", pprint.pformat(data))

        event_type = data['event']
        if event_type in HANDLED_WEBHOOK_EVENTS:
            entity_type = 'payment' if 'payment' in event_type else 'refund'
            try:
                entity_data = data['payload'].get(entity_type, {}).get('entity', {})
                entity_data.update(entity_type=entity_type)

                # Check the integrity of the event.
                received_signature = request.httprequest.headers.get('X-Razorpay-Signature')
                tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
                    'razorpay', entity_data
                )
                self._verify_notification_signature(
                    request.httprequest.data, received_signature, tx_sudo
                )

                # Handle the notification data.
                tx_sudo._handle_notification_data('razorpay', entity_data)
            except ValidationError:  # Acknowledge the notification to avoid getting spammed.
                _logger.exception("Unable to handle the notification data; skipping to acknowledge")
        return request.make_json_response('')

    @staticmethod
    def _verify_notification_signature(notification_data, received_signature, tx_sudo):
        """ Check that the received signature matches the expected one.

        :param dict|bytes notification_data: The notification data.
        :param str received_signature: The signature to compare with the expected signature.
        :param recordset tx_sudo: The sudoed transaction referenced by the notification data, as a
                                  `payment.transaction` record
        :return: None
        :raise :class:`werkzeug.exceptions.Forbidden`: If the signatures don't match.
        """
        # Check for the received signature.
        if not received_signature:
            _logger.warning("Received notification with missing signature.")
            raise Forbidden()

        # Compare the received signature with the expected signature.
        expected_signature = tx_sudo.provider_id._razorpay_calculate_signature(notification_data)
        if (
            expected_signature is None
            or not hmac.compare_digest(received_signature, expected_signature)
        ):
            _logger.warning("Received notification with invalid signature.")
            raise Forbidden()

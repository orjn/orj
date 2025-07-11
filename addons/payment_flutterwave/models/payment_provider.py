# Part of Orj. See LICENSE file for full copyright and licensing details.

import logging
import pprint

import requests
from werkzeug.urls import url_join

from orj import _, api, fields, models
from orj.exceptions import ValidationError

from orj.addons.payment import utils as payment_utils
from orj.addons.payment.const import REPORT_REASONS_MAPPING
from orj.addons.payment_flutterwave import const


_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('flutterwave', "Flutterwave")], ondelete={'flutterwave': 'set default'}
    )
    flutterwave_public_key = fields.Char(
        string="Flutterwave Public Key",
        help="The key solely used to identify the account with Flutterwave.",
        required_if_provider='flutterwave',
    )
    flutterwave_secret_key = fields.Char(
        string="Flutterwave Secret Key",
        required_if_provider='flutterwave',
        groups='base.group_system',
    )
    flutterwave_webhook_secret = fields.Char(
        string="Flutterwave Webhook Secret",
        required_if_provider='flutterwave',
        groups='base.group_system',
    )

    #=== COMPUTE METHODS ===#

    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'flutterwave').update({
            'support_tokenization': True,
        })

    # === BUSINESS METHODS ===#

    @api.model
    def _get_compatible_providers(self, *args, is_validation=False, report=None, **kwargs):
        """ Override of `payment` to filter out Flutterwave providers for validation operations. """
        providers = super()._get_compatible_providers(
            *args, is_validation=is_validation, report=report, **kwargs
        )

        if is_validation:
            unfiltered_providers = providers
            providers = providers.filtered(lambda p: p.code != 'flutterwave')
            payment_utils.add_to_report(
                report,
                unfiltered_providers - providers,
                available=False,
                reason=REPORT_REASONS_MAPPING['validation_not_supported'],
            )

        return providers

    def _get_supported_currencies(self):
        """ Override of `payment` to return the supported currencies. """
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'flutterwave':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies

    def _flutterwave_make_request(self, endpoint, payload=None, method='POST'):
        """ Make a request to Flutterwave API at the specified endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request.
        :param dict payload: The payload of the request.
        :param str method: The HTTP method of the request.
        :return The JSON-formatted content of the response.
        :rtype: dict
        :raise ValidationError: If an HTTP error occurs.
        """
        self.ensure_one()

        url = url_join('https://api.flutterwave.com/v3/', endpoint)
        headers = {'Authorization': f'Bearer {self.flutterwave_secret_key}'}
        try:
            if method == 'GET':
                response = requests.get(url, params=payload, headers=headers, timeout=10)
            else:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                _logger.exception(
                    "Invalid API request at %s with data:\n%s", url, pprint.pformat(payload),
                )
                raise ValidationError("Flutterwave: " + _(
                    "The communication with the API failed. Flutterwave gave us the following "
                    "information: '%s'", response.json().get('message', '')
                ))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Unable to reach endpoint at %s", url)
            raise ValidationError(
                "Flutterwave: " + _("Could not establish the connection to the API.")
            )
        return response.json()

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'flutterwave':
            return default_codes
        return const.DEFAULT_PAYMENT_METHOD_CODES

# -*- coding: utf-8 -*-

from orj import models, fields, api, _
from orj.addons.account.tools import is_valid_structured_reference, sanitize_structured_reference


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    def _get_qr_vals(self, qr_method, amount, currency, debtor_partner, free_communication, structured_communication):
        if qr_method == 'sct_qr':
            if structured_communication and is_valid_structured_reference(structured_communication):
                structured_communication = sanitize_structured_reference(structured_communication)
                comment = ''
            else:
                structured_communication = ''
                comment = free_communication or ''

            qr_code_vals = [
                'BCD',                                                  # Service Tag
                '002',                                                  # Version
                '1',                                                    # Character Set
                'SCT',                                                  # Identification Code
                self.bank_bic or '',                                    # BIC of the Beneficiary Bank
                (self.acc_holder_name or self.partner_id.name)[:71],    # Name of the Beneficiary
                self.sanitized_acc_number,                              # Account Number of the Beneficiary
                currency.name + str(amount),                            # Currency + Amount of the Transfer in EUR
                '',                                                     # Purpose of the Transfer
                structured_communication,                               # Remittance Information (Structured)
                comment[:141],                                          # Remittance Information (Unstructured) (can't be set if there is a structured one)
                '',                                                     # Beneficiary to Originator Information
            ]
            return qr_code_vals
        return super()._get_qr_vals(qr_method, amount, currency, debtor_partner, free_communication, structured_communication)

    def _get_qr_code_generation_params(self, qr_method, amount, currency, debtor_partner, free_communication, structured_communication):
        if qr_method == 'sct_qr':
            return {
                'barcode_type': 'QR',
                'width': 128,
                'height': 128,
                'humanreadable': 1,
                'value': '\n'.join(self._get_qr_vals(qr_method, amount, currency, debtor_partner, free_communication, structured_communication)),
            }
        return super()._get_qr_code_generation_params(qr_method, amount, currency, debtor_partner, free_communication, structured_communication)

    def _get_error_messages_for_qr(self, qr_method, debtor_partner, currency):
        if qr_method == 'sct_qr':
            # Some countries share the same IBAN country code
            # (e.g. Åland Islands and Finland IBANs are 'FI', but Åland Islands' code is 'AX').
            sepa_country_codes = self.env.ref('base.sepa_zone').country_ids.mapped('code')
            non_iban_codes = {'AX', 'NC', 'YT', 'TF', 'BL', 'RE', 'MF', 'GP', 'PM', 'PF', 'GF', 'MQ', 'JE', 'GG', 'IM'}
            sepa_iban_codes = {code for code in sepa_country_codes if code not in non_iban_codes}
            error_messages = []
            if currency.name != 'EUR':
                error_messages.append(_("Can't generate a SEPA QR Code with the %s currency.", currency.name))
            if self.acc_type != 'iban':
                error_messages.append(_("Can't generate a SEPA QR code if the account type isn't IBAN."))
            if not (self.sanitized_acc_number and self.sanitized_acc_number[:2] in sepa_iban_codes):
                error_messages.append(_("Can't generate a SEPA QR code with a non SEPA iban."))
            if len(error_messages) > 0:
                return '\r\n'.join(error_messages)
            return None
        return super()._get_error_messages_for_qr(qr_method, debtor_partner, currency)

    def _check_for_qr_code_errors(self, qr_method, amount, currency, debtor_partner, free_communication, structured_communication):
        if qr_method == 'sct_qr':
            if not self.acc_holder_name and not self.partner_id.name:
                return _("The account receiving the payment must have an account holder name or partner name set.")

        return super()._check_for_qr_code_errors(qr_method, amount, currency, debtor_partner, free_communication, structured_communication)

    @api.model
    def _get_available_qr_methods(self):
        rslt = super()._get_available_qr_methods()
        rslt.append(('sct_qr', _("SEPA Credit Transfer QR"), 20))
        return rslt

from orj import models, Command, api, _
from orj.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @api.model
    def _get_third_party_checks_country_codes(self):
        """ Return the list of country codes for the countries where third party checks journals should be created
        when installing the COA"""
        return ["AR"]

    @template(model='account.journal')
    def _get_latam_check_account_journal(self, template_code):
        if self.env.company.country_id.code in self._get_third_party_checks_country_codes():
            return {
                "third_party_check": {
                    'name': _('Third Party Checks'),
                    'type': 'cash',
                    'outbound_payment_method_line_ids': [
                        Command.create({
                            'payment_method_id': self.env.ref('l10n_latam_check.account_payment_method_out_third_party_checks').id,
                            'payment_account_id': 'base_outstanding_payments',
                        }),
                    ],
                    'inbound_payment_method_line_ids': [
                        Command.create({
                            'payment_method_id': self.env.ref('l10n_latam_check.account_payment_method_new_third_party_checks').id,
                            'payment_account_id': 'base_outstanding_receipts',
                        }),
                        Command.create({
                            'payment_method_id': self.env.ref('l10n_latam_check.account_payment_method_in_third_party_checks').id,
                            'payment_account_id': 'base_outstanding_receipts',
                        }),
                    ],
                },
                "rejected_third_party_check": {
                    'name': _('Rejected Third Party Checks'),
                    'type': 'cash',
                    'outbound_payment_method_line_ids': [
                        Command.create({
                            'payment_method_id': self.env.ref('l10n_latam_check.account_payment_method_out_third_party_checks').id,
                            'payment_account_id': 'base_outstanding_payments',
                        }),
                    ],
                    'inbound_payment_method_line_ids': [
                        Command.create({
                            'payment_method_id': self.env.ref('l10n_latam_check.account_payment_method_new_third_party_checks').id,
                            'payment_account_id': 'base_outstanding_receipts',
                        }),
                        Command.create({
                            'payment_method_id': self.env.ref('l10n_latam_check.account_payment_method_in_third_party_checks').id,
                            'payment_account_id': 'base_outstanding_receipts',
                        }),
                    ],
                },
            }

    @template(model='account.account')
    def _get_latam_check_outstanding_account_account(self, template_code):
        if self.env.company.country_id.code in self._get_third_party_checks_country_codes():
            return {
                'base_outstanding_receipts': {
                    'name': _("Outstanding Receipts"),
                    'code': '1.1.1.02.003',
                    'reconcile': True,
                    'account_type': 'asset_current',
                },
                'base_outstanding_payments': {
                    'name': _("Outstanding Payments"),
                    'code': '1.1.1.02.004',
                    'reconcile': True,
                    'account_type': 'asset_current',
                },
            }

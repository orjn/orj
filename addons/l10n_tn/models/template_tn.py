# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models
from orj.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('tn')
    def _get_tn_template_data(self):
        return {
            'property_account_receivable_id': 'l10n_tn_4111',
            'property_account_payable_id': 'l10n_tn_4011',
            'property_account_expense_categ_id': 'l10n_tn_607',
            'property_account_income_categ_id': 'l10n_tn_707',
            'code_digits': '6',
        }

    @template('tn', 'res.company')
    def _get_tn_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.tn',
                'bank_account_code_prefix': '5321',
                'cash_account_code_prefix': '5411',
                'transfer_account_code_prefix': '58',
                'account_default_pos_receivable_account_id': 'l10n_tn_5411',
                'income_currency_exchange_account_id': 'l10n_tn_756',
                'expense_currency_exchange_account_id': 'l10n_tn_655',
                'account_journal_early_pay_discount_loss_account_id': 'l10n_tn_609',
                'account_journal_early_pay_discount_gain_account_id': 'l10n_tn_709',
                'default_cash_difference_income_account_id': 'l10n_tn_756',
                'default_cash_difference_expense_account_id': 'l10n_tn_655',
                'account_sale_tax_id': 'l10n_tn_tax_vat_sale_19',
                'account_purchase_tax_id': 'l10n_tn_tax_vat_purchase_19_other_local',
            },
        }

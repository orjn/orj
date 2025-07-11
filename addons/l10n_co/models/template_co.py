# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models
from orj.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('co')
    def _get_co_template_data(self):
        return {
            'property_account_receivable_id': 'co_puc_130500',
            'property_account_payable_id': 'co_puc_220500',
            'property_account_expense_categ_id': 'co_puc_610000',
            'property_account_income_categ_id': 'co_puc_417500',
        }

    @template('co', 'res.company')
    def _get_co_res_company(self):
        return {
            self.env.company.id: {
                'anglo_saxon_accounting': True,
                'account_fiscal_country_id': 'base.co',
                'bank_account_code_prefix': '1110',
                'cash_account_code_prefix': '1105',
                'transfer_account_code_prefix': '1115',
                'account_default_pos_receivable_account_id': 'co_puc_130507',
                'income_currency_exchange_account_id': 'co_puc_421005',
                'expense_currency_exchange_account_id': 'co_puc_530505',
                'account_journal_early_pay_discount_loss_account_id': 'co_puc_530535',
                'account_journal_early_pay_discount_gain_account_id': 'co_puc_421040',
                'account_sale_tax_id': 'l10n_co_tax_8',
                'account_purchase_tax_id': 'l10n_co_tax_1',
                'default_cash_difference_income_account_id': 'co_puc_428000',
                'default_cash_difference_expense_account_id': 'co_puc_532000',
            },
        }

# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models
from orj.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('lt')
    def _get_lt_template_data(self):
        return {
            'property_account_receivable_id': 'account_account_template_2410',
            'property_account_payable_id': 'account_account_template_4430',
            'property_account_expense_categ_id': 'account_account_template_6000',
            'property_account_income_categ_id': 'account_account_template_5000',
            'property_stock_account_input_categ_id': 'account_account_template_2045',
            'property_stock_account_output_categ_id': 'account_account_template_2045',
            'property_stock_valuation_account_id': 'account_account_template_2040',
            'code_digits': '6',
        }

    @template('lt', 'res.company')
    def _get_lt_res_company(self):
        return {
            self.env.company.id: {
                'anglo_saxon_accounting': True,
                'account_fiscal_country_id': 'base.lt',
                'bank_account_code_prefix': '271',
                'cash_account_code_prefix': '272',
                'transfer_account_code_prefix': '273',
                'account_default_pos_receivable_account_id': 'account_account_template_2411',
                'income_currency_exchange_account_id': 'account_account_template_5803',
                'expense_currency_exchange_account_id': 'account_account_template_6803',
                'account_journal_early_pay_discount_loss_account_id': 'account_account_template_509',
                'account_journal_early_pay_discount_gain_account_id': 'account_account_template_6209',
                'account_sale_tax_id': 'account_tax_template_sales_21',
                'account_purchase_tax_id': 'account_tax_template_purchase_21',
            },
        }
    def _setup_utility_bank_accounts(self, template_code, company, template_data):
        super()._setup_utility_bank_accounts(template_code, company, template_data)
        if template_code == "lt":
            bank_tags = self.env.ref('l10n_lt.account_account_tag_b_4')
            company.account_journal_suspense_account_id.tag_ids |= bank_tags
            company.transfer_account_id.tag_ids |= bank_tags

            other_operating_results_tags = self.env.ref('l10n_lt.account_account_tag_6_other_operating_results')
            company.default_cash_difference_income_account_id.tag_ids |= other_operating_results_tags
            company.default_cash_difference_expense_account_id.tag_ids |= other_operating_results_tags

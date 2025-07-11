# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models
from orj.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('si')
    def _get_si_template_data(self):
        return {
            'property_account_receivable_id': 'gd_acc_120000',
            'property_account_payable_id': 'gd_acc_220000',
            'property_account_expense_categ_id': 'gd_acc_702000',
            'property_account_income_categ_id': 'gd_acc_762000',
            'code_digits': '6',
            'use_storno_accounting': True,
        }

    @template('si', 'res.company')
    def _get_si_res_company(self):
        return {
            self.env.company.id: {
                'account_fiscal_country_id': 'base.si',
                'bank_account_code_prefix': '110',
                'cash_account_code_prefix': '100',
                'transfer_account_code_prefix': '109',
                'account_default_pos_receivable_account_id': 'gd_acc_125000',
                'income_currency_exchange_account_id': 'gd_acc_777000',
                'expense_currency_exchange_account_id': 'gd_acc_484000',
                'account_sale_tax_id': 'gd_taxr_3',
                'account_purchase_tax_id': 'gd_taxp_3',
            },
        }

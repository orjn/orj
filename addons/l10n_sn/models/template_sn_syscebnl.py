from orj import models, _
from orj.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('sn_syscebnl')
    def _get_sn_syscebnl_template_data(self):
        return {
            'name': _('SYSCEBNL for Associations'),
            'parent': 'syscebnl',
            'code_digits': '6',
        }

    @template('sn_syscebnl', 'res.company')
    def _get_sn_syscebnl_res_company(self):
        company_values = super()._get_syscebnl_res_company()
        company_values[self.env.company.id].update(
            {
                'account_fiscal_country_id': 'base.sn',
                'account_sale_tax_id': 'syscebnl_tva_sale_18',
                'account_purchase_tax_id': 'syscebnl_tva_purchase_18',
            }
        )
        return company_values

    @template('sn_syscebnl', 'account.account')
    def _get_sn_syscebnl_account_account(self):
        return self._parse_csv('sn_syscebnl', 'account.account', module='l10n_syscohada')

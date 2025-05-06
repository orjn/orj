# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models
from orj.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('mc')
    def _get_mc_template_data(self):
        return {
            'code_digits': '6',
            'parent': 'fr',
        }

    def _deref_account_tags(self, template_code, tax_data):
        if template_code == 'mc':
            template_code = 'fr'
        return super()._deref_account_tags(template_code, tax_data)

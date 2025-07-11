# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import _, fields, models
from orj.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_website_sale_total = fields.Boolean(string="eCommerce Sales")
    kpi_website_sale_total_value = fields.Monetary(compute='_compute_kpi_website_sale_total_value')

    def _compute_kpi_website_sale_total_value(self):
        if not self.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))

        self._calculate_company_based_kpi(
            'sale.report',
            'kpi_website_sale_total_value',
            date_field='date',
            additional_domain=[('state', 'not in', ['draft', 'cancel', 'sent']), ('website_id', '!=', False)],
            sum_field='price_subtotal',
        )

    def _compute_kpis_actions(self, company, user):
        res = super()._compute_kpis_actions(company, user)
        res['kpi_website_sale_total'] = 'website.backend_dashboard?menu_id=%s' % self.env.ref('website.menu_website_configuration').id
        return res

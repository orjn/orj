# Part of Orj. See LICENSE file for full copyright and licensing details.

from . import models
from orj import api, SUPERUSER_ID


def post_init_hook(env):
    companies = env['res.company'].search([('account_fiscal_country_id.code', '=', 'EC'), ('chart_template', '!=', False)])
    env['account.chart.template']._l10n_ec_setup_location_accounts(companies)

# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class AccountAnalyticApplicability(models.Model):
    _inherit = 'account.analytic.applicability'
    _description = "Analytic Plan's Applicabilities"

    business_domain = fields.Selection(
        selection_add=[
            ('timesheet', 'Timesheet'),
        ],
        ondelete={'timesheet': 'cascade'},
    )

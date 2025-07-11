# Part of Orj. See LICENSE file for full copyright and licensing details.


from orj import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_ke_oscu_is_active = fields.Boolean(
        string="Is OSCU active?",
        help="Whether this company is set up for OSCU flows.",
        compute='_compute_l10n_ke_oscu_is_active',
    )

    def _compute_l10n_ke_oscu_is_active(self):
        """ Overridden in ore when the OSCU module is used in the company"""
        self.l10n_ke_oscu_is_active = False

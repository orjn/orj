# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_th_branch_name = fields.Char(compute="_compute_l10n_th_branch_name")

    def _compute_l10n_th_branch_name(self):
        for partner in self:
            if not partner.is_company or partner.country_code != 'TH':
                partner.l10n_th_branch_name = ""
            else:
                code = partner.company_registry
                partner.l10n_th_branch_name = f"Branch {code}" if code else "Headquarter"

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import fields, models


class ResPartner(models.Model):
    _name = 'res.country'
    _inherit = 'res.country'

    l10n_cl_customs_code = fields.Char('Customs Code')
    l10n_cl_customs_name = fields.Char('Customs Name')
    l10n_cl_customs_abbreviation = fields.Char('Customs Abbreviation')

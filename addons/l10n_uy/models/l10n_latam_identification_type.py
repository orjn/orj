# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models, fields


class L10nLatamIdentificationType(models.Model):

    _inherit = "l10n_latam.identification.type"

    l10n_uy_dgi_code = fields.Char('DGI Code')

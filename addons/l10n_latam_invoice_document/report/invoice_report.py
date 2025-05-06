# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models, fields
from orj.tools import SQL


class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', 'Document Type', index=True)
    _depends = {'account.move': ['l10n_latam_document_type_id'],}

    def _select(self) -> SQL:
        return SQL("%s, move.l10n_latam_document_type_id as l10n_latam_document_type_id",
                   super()._select())

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models, api, _
from orj.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_reference_model = fields.Selection(selection_add=[('se_ocr2', 'Sweden OCR Level 1 & 2'), ('se_ocr3', 'Sweden OCR Level 3'), ('se_ocr4', 'Sweden OCR Level 4')], ondelete={'se_ocr2': 'set default', 'se_ocr3': 'set default', 'se_ocr4': 'set default'})
    l10n_se_invoice_ocr_length = fields.Integer(string='OCR Number Length', help="Total length of OCR Reference Number including checksum.", default=6)

    @api.constrains('l10n_se_invoice_ocr_length')
    def _check_l10n_se_invoice_ocr_length(self):
        for journal in self:
            if journal.l10n_se_invoice_ocr_length < 6:
                raise ValidationError(_('OCR Reference Number length need to be greater than 5. Please correct settings under invoice journal settings.'))

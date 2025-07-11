from orj import api, models


class AccountMoveSend(models.AbstractModel):
    _inherit = 'account.move.send'

    @api.model
    def _get_mail_attachment_from_doc(self, doc):
        attachment_sudo = doc.sudo().attachment_id
        if attachment_sudo.res_model and attachment_sudo.res_id:
            return attachment_sudo
        return self.env['ir.attachment']

    def _get_invoice_extra_attachments(self, move):
        # EXTENDS 'account'
        result = super()._get_invoice_extra_attachments(move)
        for doc in move.edi_document_ids:
            result += self._get_mail_attachment_from_doc(doc)
        return result

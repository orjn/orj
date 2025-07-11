# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _message_set_main_attachment_id(self, attachments, force=False, filter_xml=True):
        if self.message_main_attachment_id.mimetype == "application/pkcs7-mime":
            force = True
        super()._message_set_main_attachment_id(attachments, force, filter_xml)

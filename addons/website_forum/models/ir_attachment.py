# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class Attachment(models.Model):

    _inherit = "ir.attachment"

    def _can_bypass_rights_on_media_dialog(self, **attachment_data):
        # Bypass the attachment create ACL and let the user create the image
        # attachment if they have write access to the model (the image attachment
        # will be bound to this model's record).
        res_model = attachment_data['res_model']
        res_id = attachment_data.get('res_id')
        if (
            res_model == 'forum.post' and res_id
            and self.env['forum.post'].browse(res_id).can_use_full_editor
        ):
            return True

        return super()._can_bypass_rights_on_media_dialog(**attachment_data)

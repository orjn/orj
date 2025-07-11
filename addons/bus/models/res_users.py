# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResUsers(models.Model):
    _name = "res.users"
    _inherit = ["res.users", "bus.listener.mixin"]

    im_status = fields.Char("IM Status", compute="_compute_im_status")

    def _compute_im_status(self):
        """Compute the im_status of the users"""
        presence_by_user = {
            presence.user_id: presence.status
            for presence in self.env["bus.presence"].search([("user_id", "in", self.ids)])
        }
        for user in self:
            user.im_status = presence_by_user.get(user, "offline")

    def _bus_channel(self):
        return self.partner_id._bus_channel()

    def _is_user_available(self):
        return self.im_status == 'online'

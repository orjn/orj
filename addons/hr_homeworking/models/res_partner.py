# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _compute_im_status(self):
        super()._compute_im_status()
        for user in self.user_ids:
            dayfield = self.env['hr.employee']._get_current_day_location_field()
            location_type = user[dayfield].location_type
            if not location_type:
                continue
            im_status = user.partner_id.im_status
            if im_status == "online" or im_status == "away" or im_status == "offline":
                user.partner_id.im_status = location_type + "_" + im_status


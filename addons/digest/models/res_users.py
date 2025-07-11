# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        """ Automatically subscribe employee users to default digest if activated """
        users = super(ResUsers, self).create(vals_list)
        default_digest_emails = self.env['ir.config_parameter'].sudo().get_param('digest.default_digest_emails')
        default_digest_id = self.env['ir.config_parameter'].sudo().get_param('digest.default_digest_id')
        users_to_subscribe = users.filtered_domain([('share', '=', False)])
        if default_digest_emails and default_digest_id and users_to_subscribe:
            digest = self.env['digest.digest'].sudo().browse(int(default_digest_id)).exists()
            digest.user_ids |= users_to_subscribe
        return users

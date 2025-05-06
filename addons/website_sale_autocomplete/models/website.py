# -*- encoding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models, fields


class Website(models.Model):
    _inherit = 'website'

    google_places_api_key = fields.Char(
        string='Google Places API Key',
        groups="base.group_system")

    def has_google_places_api_key(self):
        return bool(self.sudo().google_places_api_key)

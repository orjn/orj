# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_maintenance_worksheet = fields.Boolean(string="Custom Maintenance Worksheets")

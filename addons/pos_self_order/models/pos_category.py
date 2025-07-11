# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.exceptions import ValidationError
from orj import models, fields, api, _


class PosCategory(models.Model):
    _inherit = "pos.category"


    hour_until = fields.Float(string='Availability Until', default=24.0, help="The product will be available until this hour.")
    hour_after = fields.Float(string='Availability After', default=0.0, help="The product will be available after this hour.")

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += ['hour_until', 'hour_after']
        return fields

    @api.constrains('hour_until', 'hour_after')
    def _check_hour(self):
        for category in self:
            if category.hour_until and not (0.0 <= category.hour_until <= 24.0):
                raise ValidationError(_('The Availability Until must be set between 00:00 and 24:00'))
            if category.hour_after and not (0.0 <= category.hour_after <= 24.0):
                raise ValidationError(_('The Availability After must be set between 00:00 and 24:00'))
            if category.hour_until and category.hour_after and category.hour_until < category.hour_after:
                raise ValidationError(_('The Availability Until must be greater than Availability After.'))

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_product_types_allow_zero_price(self):
        return super()._get_product_types_allow_zero_price() + ["event_booth"]

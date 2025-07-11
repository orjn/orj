# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_expiry_date_on_delivery_slip = fields.Boolean("Display Expiration Dates on Delivery Slips",
        implied_group='product_expiry.group_expiry_date_on_delivery_slip')

    @api.onchange('group_lot_on_delivery_slip')
    def _onchange_group_lot_on_delivery_slip(self):
        if not self.group_lot_on_delivery_slip:
            self.group_expiry_date_on_delivery_slip = False

    @api.onchange('group_stock_production_lot')
    def _onchange_group_stock_production_lot(self):
        super()._onchange_group_stock_production_lot()
        if self.group_stock_production_lot:
            self.module_product_expiry = True

    @api.onchange('module_product_expiry')
    def _onchange_module_product_expiry(self):
        if not self.module_product_expiry:
            self.group_expiry_date_on_delivery_slip = False

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import fields, models, api


class ProductWishlist(models.Model):
    _inherit = "product.wishlist"

    stock_notification = fields.Boolean(compute='_compute_stock_notification', default=False, required=True)

    @api.depends("product_id", "partner_id")
    def _compute_stock_notification(self):
        for record in self:
            record.stock_notification = record.product_id._has_stock_notification(record.partner_id)

    def _inverse_stock_notification(self):
        for record in self:
            if record.stock_notification:
                record.product_id.stock_notification_partner_ids += record.partner_id

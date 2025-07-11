# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import _, api, models
from orj.exceptions import UserError, ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def write(self, vals):
        if not vals.get('active', True) and any(product.active for product in self):
            # Prevent archiving products used for giving rewards
            rewards = self.env['loyalty.reward'].sudo().search([
                ('active', '=', True),
                '|',
                ('discount_line_product_id', 'in', self.ids),
                ('discount_product_ids', 'in', self.ids),
            ], limit=1)
            if rewards:
                raise ValidationError(_("This product may not be archived. It is being used for an active promotion program."))
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_loyalty_products(self):
        product_data = [
            self.env.ref('loyalty.gift_card_product_50', False),
            self.env.ref('loyalty.ewallet_product_50', False),
        ]
        for product in self.filtered(lambda p: p in product_data):
            raise UserError(_(
                "You cannot delete %(name)s as it is used in 'Coupons & Loyalty'."
                " Please archive it instead.",
                name=product.with_context(display_default_code=False).display_name
            ))

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import _, fields, models


class Product(models.Model):
    _inherit = "product.product"

    channel_ids = fields.One2many('slide.channel', 'product_id', string='Courses')

    def _is_add_to_cart_allowed(self):
        """Override to allow published course related products to the cart regardless of product's rules."""
        self.ensure_one()
        res = super()._is_add_to_cart_allowed()
        return res or bool(self.env['slide.channel'].sudo().search_count([
            ('product_id', '=', self.id),
            ('website_published', '=', True),
        ], limit=1))

    def get_product_multiline_description_sale(self):
        payment_channels = self.channel_ids.filtered(lambda course: course.enroll == 'payment')

        if not payment_channels:
            return super(Product, self).get_product_multiline_description_sale()

        new_line = '' if len(payment_channels) == 1 else '\n'
        return _('Access to: %(new_line)s%(channel_list)s', new_line=new_line, channel_list='\n'.join(payment_channels.mapped('name')))

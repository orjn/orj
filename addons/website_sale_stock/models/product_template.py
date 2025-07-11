# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models
from orj.http import request
from orj.tools.translate import html_translate

from orj.addons.website.models import ir_http


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allow_out_of_stock_order = fields.Boolean(string='Continue selling when out-of-stock', default=True)

    available_threshold = fields.Float(string='Show Threshold', default=5.0)
    show_availability = fields.Boolean(string='Show availability Qty', default=False)
    out_of_stock_message = fields.Html(string="Out-of-Stock Message", translate=html_translate)

    def _is_sold_out(self):
        return self.is_storable and self.product_variant_id._is_sold_out()

    def _website_show_quick_add(self):
        return (self.allow_out_of_stock_order or not self._is_sold_out()) and super()._website_show_quick_add()

    def _get_additionnal_combination_info(self, product_or_template, quantity, date, website):
        res = super()._get_additionnal_combination_info(product_or_template, quantity, date, website)

        product_or_template = product_or_template.sudo()
        res.update({
            'product_type': product_or_template.type,
            'allow_out_of_stock_order': product_or_template.allow_out_of_stock_order,
            'available_threshold': product_or_template.available_threshold,
        })
        if product_or_template.is_product_variant:
            product = product_or_template
            free_qty = website._get_product_available_qty(product)
            has_stock_notification = (
                product._has_stock_notification(self.env.user.partner_id)
                or request and product.id in request.session.get(
                    'product_with_stock_notification_enabled', set())
            )
            stock_notification_email = request and request.session.get('stock_notification_email', '')
            res.update({
                'free_qty': free_qty,
                'cart_qty': product._get_cart_qty(website),
                'uom_name': product.uom_id.name,
                'uom_rounding': product.uom_id.rounding,
                'show_availability': product_or_template.show_availability,
                'out_of_stock_message': product_or_template.out_of_stock_message,
                'has_stock_notification': has_stock_notification,
                'stock_notification_email': stock_notification_email,
            })
        else:
            res.update({
                'free_qty': 0,
                'cart_qty': 0,
            })
        if product_or_template.type == 'combo':
            # The max quantity of a combo product is the max quantity of its combo with the lowest
            # max quantity. If none of the combos has a max quantity, then the combo product also
            # has no max quantity.
            max_quantities = [
                max_quantity for combo in product_or_template.combo_ids.sudo()
                if (max_quantity := combo._get_max_quantity(website)) is not None
            ]
            if max_quantities:
                res['max_combo_quantity'] = min(max_quantities)

        return res

    @api.model
    def _get_additional_configurator_data(
        self, product_or_template, date, currency, pricelist, **kwargs
    ):
        """ Override of `website_sale` to append stock data.

        :param product.product|product.template product_or_template: The product for which to get
            additional data.
        :param datetime date: The date to use to compute prices.
        :param res.currency currency: The currency to use to compute prices.
        :param product.pricelist pricelist: The pricelist to use to compute prices.
        :param dict kwargs: Locally unused data passed to `super` and `_get_max_quantity`.
        :rtype: dict
        :return: A dict containing additional data about the specified product.
        """
        data = super()._get_additional_configurator_data(
            product_or_template, date, currency, pricelist, **kwargs
        )

        if (website := ir_http.get_request_website()) and product_or_template.is_product_variant:
            max_quantity = product_or_template._get_max_quantity(website, **kwargs)
            if max_quantity is not None:
                data['free_qty'] = max_quantity
        return data

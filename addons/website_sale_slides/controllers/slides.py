# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.addons.website_slides.controllers.main import WebsiteSlides
from orj.http import request, route
from orj.tools import format_amount


class WebsiteSaleSlides(WebsiteSlides):

    @route('/slides/get_course_products', type='json', auth='user')
    def get_course_products(self):
        """Return a list of the course products values with formatted price."""
        products = request.env['product.product'].search([('service_tracking', '=', 'course')])

        return [{
            'id': product.id,
            'name': f'{product.name} ({format_amount(request.env, product.list_price, product.currency_id)})',
        } for product in products]

    def _prepare_additional_channel_values(self, values, **kwargs):
        values = super(WebsiteSaleSlides, self)._prepare_additional_channel_values(values, **kwargs)
        channel = values['channel']
        if channel.enroll == 'payment':
            # search the product to apply ACLs, notably on published status, to avoid access errors
            product = request.env['product.product'].search([('id', '=', channel.product_id.id)]) if channel.product_id else request.env['product.product']
            if product:
                values['product_info'] = product._get_combination_info_variant()
            else:
                values['product_info'] = False
        return values

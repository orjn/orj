# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.addons.website_sale.controllers.main import WebsiteSale
from orj.http import request


class WebsiteEventSale(WebsiteSale):

    def _prepare_shop_payment_confirmation_values(self, order):
        values = super(WebsiteEventSale,
                       self)._prepare_shop_payment_confirmation_values(order)
        values['events'] = order.order_line.event_id
        attendee_per_event_read_group = request.env['event.registration'].sudo()._read_group(
            [('sale_order_id', '=', order.id), ('state', 'in', ['open', 'done'])],
            groupby=['event_id'],
            aggregates=['id:recordset'],
        )
        values['attendee_ids_per_event'] = dict(attendee_per_event_read_group)
        values['urls_per_event'] = {
            event.id: event._get_event_resource_urls()
            for event in values['events']
        }

        return values

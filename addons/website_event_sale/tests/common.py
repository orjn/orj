# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from orj.fields import Datetime
from orj.tests.common import TransactionCase


class TestWebsiteEventSaleCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWebsiteEventSaleCommon, cls).setUpClass()

        cls.env.company.country_id = cls.env.ref('base.us')
        cls.currency_test = cls.env['res.currency'].create({
            'name': 'eventX',
            'rounding': 0.01,
            'symbol': 'EX',
        })
        cls.partner = cls.env['res.partner'].create({'name': 'test'})
        cls.env['res.currency.rate'].search([]).unlink()
        cls.rate = cls.env['res.currency.rate'].create({
            'company_id': cls.env.company.id,
            'currency_id': cls.currency_test.id,
            'name': '2022-01-01',
            'rate': 10,
        })
        cls.zero_tax = cls.env['account.tax'].sudo().create({
            'name': 'Tax 0',
            'amount': 0,
            'tax_group_id': cls.env['account.tax.group'].create({
                'name': 'Text Tax Group',
                'company_id': cls.env.company.id,
            }).id
        })
        cls.product_event = cls.env['product.product'].create({
            'type': 'service',
            'service_tracking': 'event',
            'list_price': 100,
            'name': 'Event Registration No Company Assigned',
            'taxes_id': [(6, 0, cls.zero_tax.ids)],
        })

        cls.event, cls.event_2 = cls.env['event.event'].create([
            {
                'date_begin': (Datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d 07:00:00'),
                'date_end': (Datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d 16:30:00'),
                'name': 'Pycon',
                'user_id': cls.env.ref('base.user_admin').id,
                'website_published': True,
            },
            {
                'date_begin': (Datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d 07:00:00'),
                'date_end': (Datetime.today() + timedelta(days=5)).strftime('%Y-%m-%d 16:30:00'),
                'name': 'Conference for Architects TEST',
                'user_id': cls.env.ref('base.user_admin').id,
                'website_published': True,
            }
        ])
        cls.ticket, cls.ticket_2 = cls.env['event.event.ticket'].create([
            {
                'event_id': cls.event.id,
                'name': 'Standard',
                'product_id': cls.product_event.id,
                'price': 100,
            },
            {
                'event_id': cls.event_2.id,
                'name': 'Standard',
                'product_id': cls.product_event.id,
                'price': 1000,
            }
        ])

        cls.current_website = cls.env['website'].get_current_website()
        cls.pricelist = cls.env['product.pricelist'].create({'name': 'Base Pricelist'})

        cls.so = cls.env['sale.order'].create({
            'company_id': cls.env.company.id,
            'partner_id': cls.partner.id,
            'pricelist_id': cls.pricelist.id,
        })

        def create_pricelist(currency, name):
            return cls.env['product.pricelist'].create({
                'currency_id': currency.id,
                'item_ids': [(5, 0, 0), (0, 0, {
                    'applied_on': '3_global',
                    'compute_price': 'percentage',
                    'percent_price': 10,
                })],
                'name': name,
                'selectable': True,
            })

        cls.pricelist_without_discount = create_pricelist(currency=cls.env.company.currency_id, name='EUR Without Discount Included')
        cls.ex_pricelist_without_discount = create_pricelist(currency=cls.currency_test, name='EX Without Discount Included')

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Purchase',
    'summary': 'Sale based on service outsourcing.',
    'description': """
Allows the outsourcing of services. This module allows one to sell services provided
by external providers and will automatically generate purchase orders directed to the service seller.
    """,
    'version': '1.0',
    'website': 'https://www.orj.net/',
    'category': 'Hidden',
    'depends': [
        'sale',
        'purchase',
    ],
    'data': [
        'data/mail_templates.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'wizards/sale_order_cancel_views.xml',
    ],
    'auto_install': True,
    'license': 'LGPL-3',
}

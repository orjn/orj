# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.


{
    'name': 'Point of Sale online payment',
    'depends': ['point_of_sale', 'account_payment'],
    'data': [
        'views/payment_transaction_views.xml',
        'views/pos_payment_views.xml',
        'views/pos_payment_method_views.xml',
        'views/payment_portal_templates.xml',
        'views/account_payment_views.xml',
    ],
    'auto_install': True,
    'installable': True,
    'assets': {
        'point_of_sale.assets_prod': [
            'pos_online_payment/static/src/app/**/*',
            'pos_online_payment/static/src/overrides/pos_overrides/**/*',
        ],
        'point_of_sale.customer_display_assets': [
            'pos_online_payment/static/src/app/online_payment_popup/**/*',
            'pos_online_payment/static/src/overrides/customer_display_overrides/**/*',
        ],
        'point_of_sale.customer_display_assets_test': [
            'pos_online_payment/static/tests/tours/**/*',
        ],
        'web.assets_tests': [
            'pos_online_payment/static/tests/tours/**/*',
        ],
    },
    'license': 'LGPL-3',
}

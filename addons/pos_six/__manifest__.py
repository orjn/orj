# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Six',
    'version': '1.0',
    'category': 'Sales/Point Of Sale',
    'sequence': 6,
    'summary': 'Integrate your POS with a Six payment terminal',
    'data': [
        'views/pos_payment_method_views.xml',
    ],
    'depends': ['point_of_sale'],
    'installable': True,
    'license': 'LGPL-3',
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_six/static/lib/six_timapi/timapi.js',
            'pos_six/static/src/**/*',
        ],
    }
}

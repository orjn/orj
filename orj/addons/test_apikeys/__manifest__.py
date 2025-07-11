# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Tests flow of API keys',
    'category': 'Tools',
    'depends': ['web_tour', 'auth_totp'],
    'assets': {
        'web.assets_tests': [
            # inside .
            'test_apikeys/static/tests/apikey_flow.js',
        ],
    },
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'OrjBot',
    'version': '1.2',
    'category': 'Productivity/Discuss',
    'summary': 'Add OrjBot in discussions',
    'website': 'https://www.orj.net/app/discuss',
    'depends': ['mail'],
    'auto_install': True,
    'installable': True,
    'data': [
        'views/res_users_views.xml',
        'data/mailbot_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mail_bot/static/src/scss/orjbot_style.scss',
        ],
    },
    'license': 'LGPL-3',
}

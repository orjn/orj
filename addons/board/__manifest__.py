# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'Dashboards',
    'version': '1.0',
    'category': 'Productivity',
    'sequence': 225,
    'summary': 'Build your own dashboards',
    'description': """
Lets the user create a custom dashboard.
========================================

Allows users to create custom dashboard.
    """,
    'depends': ['spreadsheet_dashboard'],
    'data': [
        'security/ir.model.access.csv',
        'views/board_views.xml',
        ],
    'assets': {
        'web.assets_backend': [
            'board/static/src/**/*.scss',
            'board/static/src/**/*.js',
            'board/static/src/**/*.xml',
        ],
        'web.assets_unit_tests': [
            'board/static/tests/**/*.test.js',
        ],
    },
    'license': 'LGPL-3',
}

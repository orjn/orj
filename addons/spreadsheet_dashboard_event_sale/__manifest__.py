# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': "Spreadsheet dashboard for events",
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Spreadsheet',
    'description': 'Spreadsheet',
    'depends': ['spreadsheet_dashboard', 'event_sale'],
    'data': [
        "data/dashboards.xml",
    ],
    'installable': True,
    'auto_install': ['event_sale'],
    'license': 'LGPL-3',
}

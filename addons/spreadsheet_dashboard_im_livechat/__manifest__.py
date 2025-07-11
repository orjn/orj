# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': "Spreadsheet dashboard for live chat",
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Spreadsheet',
    'description': 'Spreadsheet',
    'depends': ['spreadsheet_dashboard', 'im_livechat'],
    'data': [
        "data/dashboards.xml",
    ],
    'installable': True,
    'auto_install': ['im_livechat'],
    'license': 'LGPL-3',
}

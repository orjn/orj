# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'Indian - Stock Report(GST)',
    'version': '1.0',
    'description': """GST Stock Report""",
    'category': 'Accounting/Localizations',
    'depends': [
        'l10n_in',
        'stock',
    ],
    'data': [
        'views/report_stockpicking_operations.xml',
    ],
    'demo': [
        'data/product_demo.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

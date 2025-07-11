# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.


{
    'name': 'Mrp Repairs',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'depends': ['repair', 'mrp'],
    'data': [
        'views/production_views.xml',
        'views/repair_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

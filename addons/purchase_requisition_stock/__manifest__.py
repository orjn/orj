# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Requisition Stock',
    'version': '1.2',
    'category': 'Inventory/Purchase',
    'sequence': 70,
    'depends': ['purchase_requisition', 'purchase_stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/purchase_requisition_stock_data.xml',
        'views/purchase_views.xml',
        'views/purchase_requisition_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

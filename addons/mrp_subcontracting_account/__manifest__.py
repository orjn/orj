# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'Subcontracting Management with Stock Valuation',
    'version': '0.1',
    'category': 'Hidden',
    'description': """
This bridge module allows to manage subcontracting with valuation.
    """,
    'depends': ['mrp_subcontracting', 'mrp_account'],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
    'data': [
        'security/mrp_subcontracting_account_security.xml',
        'security/ir.model.access.csv',
    ],
}

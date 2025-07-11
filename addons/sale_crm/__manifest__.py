# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'Opportunity to Quotation',
    'version': '1.0',
    'category': 'Hidden',
    'description': """
This module adds a shortcut on one or several opportunity cases in the CRM.
===========================================================================

This shortcut allows you to generate a sales order based on the selected case.
If different cases are open (a list), it generates one sales order by case.
The case is then closed and linked to the generated sales order.

We suggest you to install this module, if you installed both the sale and the crm
modules.
    """,
    'depends': ['sale', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_lead_merge_template.xml',
        'views/partner_views.xml',
        'views/sale_order_views.xml',
        'views/crm_lead_views.xml',
        'views/crm_team_views.xml',
        'wizard/crm_opportunity_to_quotation_views.xml'
    ],
    'auto_install': True,
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}

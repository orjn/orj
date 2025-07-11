# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.


{
    'name': 'Project Expenses',
    'version': '1.0',
    'category': 'Services/expenses',
    'summary': 'Project expenses',
    'description': 'Bridge created to add the number of expenses linked to an AA to a project form',
    'depends': ['project_account', 'hr_expense'],
    'data': [
        'views/project_project_views.xml',
    ],
    'demo': [
        'data/project_hr_expense_demo.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

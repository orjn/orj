# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.


{
    'name': 'Time Off in Payslips',
    'version': '1.0',
    'category': 'Human Resources/Payroll',
    'sequence': 95,
    'summary': 'Manage Time Off in Payslips',
    'description': """
Manage Time Off in Payslips
============================

This application allows you to integrate time off in payslips.
    """,
    'depends': ['hr_holidays', 'hr_holidays_contract', 'hr_work_entry_contract'],
    'data': [
        'data/hr_payroll_holidays_data.xml',
        'views/hr_leave_views.xml',
        'views/hr_leave_type_views.xml',
    ],
    'demo': ['data/hr_payroll_holidays_demo.xml'],
    'installable': True,
    'auto_install': True,
    'post_init_hook': '_validate_existing_work_entry',
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': "Timesheets/attendances reporting",
    'description': """
    Module linking the attendance module to the timesheet app.
    """,
    'category': 'Hidden',
    'version': '1.1',

    'depends': ['hr_timesheet', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_timesheet_attendance_report_security.xml',
        'report/hr_timesheet_attendance_report_view.xml',
    ],
    'auto_install': True,
    'license': 'LGPL-3',
}

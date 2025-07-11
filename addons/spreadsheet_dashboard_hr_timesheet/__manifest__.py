# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': "Spreadsheet dashboard for time sheets",
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Spreadsheet',
    'description': 'Spreadsheet',
    'depends': ['spreadsheet_dashboard', 'hr_timesheet'],
    'data': [
        "data/dashboards.xml",
    ],
    'installable': True,
    'auto_install': ['hr_timesheet'],
    'license': 'LGPL-3',
}

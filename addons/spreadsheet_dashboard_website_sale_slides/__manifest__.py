# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': "Spreadsheet dashboard for eLearning",
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Spreadsheet',
    'description': 'Spreadsheet',
    'depends': ['spreadsheet_dashboard', 'website_sale_slides'],
    'data': [
        "data/dashboards.xml",
    ],
    'installable': True,
    'auto_install': ['website_sale_slides'],
    'license': 'LGPL-3',
}

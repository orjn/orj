# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Portugal - Accounting',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations.html',
    'icon': '/account/static/description/l10n.png',
    'countries': ['pt'],
    'version': '1.0',
    'author': 'Orj',
    'category': 'Accounting/Localizations/Account Charts',
    'description': 'Portugal - Accounting',
    'depends': [
        'base',
        'account',
        'base_vat',
    ],
    'auto_install': ['account'],
    'data': [
        'data/account_tax_report.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}

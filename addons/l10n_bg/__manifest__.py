# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Bulgaria - Accounting',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations.html',
    'icon': '/account/static/description/l10n.png',
    'countries': ['bg'],
    'version': '1.0',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
Chart accounting and taxes for Bulgaria
    """,
    'depends': [
        'account',
        'base_vat',
    ],
    'auto_install': ['account'],
    'data': [
        'data/tax_report.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}

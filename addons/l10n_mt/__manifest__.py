# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Malta - Accounting',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations.html',
    'icon': '/account/static/description/l10n.png',
    'countries': ['mt'],
    'description': """
Malta basic package that contains the chart of accounts, the taxes, tax reports, etc.
    """,
    'version': '1.0',
    'category': 'Accounting/Localizations/Account Charts',
    'depends': [
        'account',
        'base_vat',
    ],
    'auto_install': ['account'],
    'data': [
        'data/menuitem_data.xml',
        'data/account_tax_report_data.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}

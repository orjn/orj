# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Ethiopia - Accounting',
    'icon': '/account/static/description/l10n.png',
    'countries': ['et'],
    'version': '2.0',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
Base Module for Ethiopian Localization
======================================

This is the latest Ethiopian Orj localization and consists of:
    - Chart of Accounts
    - VAT tax structure
    - Withholding tax structure
    - Regional State listings
    """,
    'author': 'Michael Telahun Makonnen <mmakonnen@gmail.com>',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations.html',
    'depends': [
        'account',
    ],
    'auto_install': ['account'],
    'data': [
        'data/account_tax_report_data.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}

# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Türkiye - Accounting',
    'icon': '/account/static/description/l10n.png',
    'countries': ['tr'],
    'version': '1.3',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
This is the base module to manage the accounting chart for Türkiye in Orj
==========================================================================

Türkiye accounting basic charts and localizations
-------------------------------------------------
Activates:

- Chart of Accounts
- Taxes
- Tax Report
    """,
    'author': 'Orj S.A., Drysharks Consulting and Trading Ltd.',
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

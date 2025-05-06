# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Bangladesh - Accounting',
    'website': 'https://www.orj.net/documentation/18.0/applications/finance/fiscal_localizations.html',
    'icon': '/account/static/description/l10n.png',
    'countries': ['bd'],
    'version': '1.0',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
This is the base module to manage the accounting chart for Bangladesh in Orj
==============================================================================

Bangladesh accounting basic charts and localization.

Activates:

- Chart of accounts
- Taxes
- Tax report
""",
    'depends': [
        'account',
    ],
    'auto_install': ['account'],
    'data': [
        'data/account.account.tag.csv',
        'data/res.country.state.csv',
        'data/account_tax_report_data.xml',
        'views/menu_items.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}

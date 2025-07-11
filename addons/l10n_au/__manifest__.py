# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'Australia - Accounting',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations/australia.html',
    'icon': '/account/static/description/l10n.png',
    'countries': ['au'],
    'version': '1.1',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
Australian Accounting Module
============================

Australian accounting basic charts and localizations.

Also:
    - activates a number of regional currencies.
    - sets up Australian taxes.
    """,
    'depends': ['account'],
    'auto_install': ['account'],
    'data': [
        'data/account_tax_report_data.xml',
        'data/account_tax_template_data.xml',
        'data/res_currency_data.xml',
        'data/account.account.tag.csv',
        'views/menuitems.xml',
        'views/report_invoice.xml',
        'views/res_company_views.xml',
        'views/res_partner_bank_views.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}

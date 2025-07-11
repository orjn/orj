# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Kenya - Accounting',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations/kenya.html',
    'icon': '/account/static/description/l10n.png',
    'countries': ['ke'],
    'version': '1.0',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
This provides a base chart of accounts and taxes template for use in Orj.
    """,
    'depends': [
        'account',
    ],
    'auto_install': ['account'],
    'data': [
        'views/account_move_views.xml',
        'views/account_tax_views.xml',
        'views/l10n_ke_item_code_views.xml',
        'data/l10n_ke.item.code.csv',
        'data/account_tax_report_data.xml',
        'data/account_wh_tax_report_data.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}

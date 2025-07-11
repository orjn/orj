# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Mozambique - Accounting',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations.html',
    'description': """
Mozambican Accounting localization
    """,
    'version': '1.0',
    'icon': '/account/static/description/l10n.png',
    'countries': ['mz'],
    'category': 'Accounting/Localizations/Account Charts',
    'depends': [
        'base',
        'account',
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

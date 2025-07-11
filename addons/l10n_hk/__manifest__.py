# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Hong Kong - Accounting',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations/hong_kong.html',
    'icon': '/account/static/description/l10n.png',
    'countries': ['hk'],
    'version': '1.0',
    'category': 'Accounting/Localizations/Account Charts',
    'description': ' This is the base module to manage chart of accounting and localization for Hong Kong ',
    'depends': [
        'account_qr_code_emv',
        'account',
    ],
    'auto_install': ['account'],
    'data': [
        'data/account_chart_template_data.xml',
        'views/res_bank_views.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}

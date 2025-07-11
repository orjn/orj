# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Algeria - Accounting',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations.html',
    'icon': '/account/static/description/l10n.png',
    'countries': ['dz'],
    'version': '1.0',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
This is the module to manage the accounting chart for Algeria in Orj.
======================================================================
This module applies to companies based in Algeria.
""",
    'author': 'Osis',
    'depends': [
        'base_vat',
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

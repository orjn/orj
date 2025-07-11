# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    "name": "Ireland - Accounting",
    "version": "2.0",
    'countries': ['ie'],
    "icon": '/account/static/description/l10n.png',
    "category": "Accounting/Localizations/Account Charts",
    "description": """
This is the base module to manage the accounting chart for Republic of Ireland in Orj.
    """,
    "author": "Orj SA",
    "depends": [
        "account",
        "base_iban",
        "base_vat",
    ],
    'auto_install': ['account'],
    "data": [
        "data/tax_report-ie.xml",
    ],
    "demo": [
        "demo/demo_company.xml",
    ],
    "license": "LGPL-3",
}

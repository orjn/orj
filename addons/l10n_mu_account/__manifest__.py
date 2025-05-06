# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    "name": "Mauritius - Accounting",
    "version": "1.0",
    'countries': ['mu'],
    "category": "Accounting/Localizations/Account Charts",
    "description": """
This is the base module to manage the accounting chart for the Republic of Mauritius in Orj.
==============================================================================================
    - Chart of accounts
    - Taxes
    - Fiscal positions
    - Default settings
    """,
    "author": "Orj SA",
    "depends": [
        "account",
    ],
    "data": [
        "data/tax_report-mu.xml",
        "views/report_invoice.xml",
    ],
    "demo": [
        "demo/demo_company.xml",
    ],
    "license": "LGPL-3",
}

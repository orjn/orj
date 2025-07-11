# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Venezuela - Accounting',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations.html',
    'icon': '/account/static/description/l10n.png',
    'countries': ['ve'],
    'author': 'Orj S.A., Vauxoo',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
Chart of Account for Venezuela.
===============================

Venezuela doesn't have any chart of account by law, but the default
proposed in Orj should comply with some Accepted best practices in Venezuela,
this plan comply with this practices.

This module has been tested as base for more of 1000 companies, because
it is based in a mixtures of most common software in the Venezuelan
market what will allow for sure to accountants feel them first steps with
Orj more comfortable.

This module doesn't pretend be the total localization for Venezuela,
but it will help you to start really quickly with Orj in this country.

This module give you.
---------------------

- Basic taxes for Venezuela.
- Have basic data to run tests with community localization.
- Start a company from 0 if your needs are basic from an accounting PoV.

We recomend use of account_anglo_saxon if you want valued your
stocks as Venezuela does with out invoices.

If you install this module, and select Custom chart a basic chart will be proposed,
but you will need set manually account defaults for taxes.
""",
    'depends': [
        'account',
    ],
    'auto_install': ['account'],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}

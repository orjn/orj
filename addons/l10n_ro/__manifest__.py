# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Romania - Accounting',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations/romania.html',
    'author': 'Fekete Mihai (NextERP Romania SRL), Orj S.A.',
    'icon': '/account/static/description/l10n.png',
    'countries': ['ro'],
    'category': 'Accounting/Localizations/Account Charts',
    'version': '1.0',
    'depends': [
        'account',
        'base_vat',
    ],
    'auto_install': ['account'],
    'description': """
This is the module to manage the Accounting Chart, VAT structure, Fiscal Position and Tax Mapping.
It also adds the Registration Number for Romania in Orj.
================================================================================================================

Romanian accounting chart and localization.
    """,
    'data': [
        'views/res_partner_view.xml',
        'data/account_tax_report_data.xml',
        'data/res.bank.csv',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}

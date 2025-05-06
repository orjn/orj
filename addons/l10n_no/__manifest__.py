# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Norway - Accounting',
    'website': 'https://www.orj.net/documentation/master/applications/finance/fiscal_localizations.html',
    'icon': '/account/static/description/l10n.png',
    'countries': ['no'],
    'version': '2.1',
    'author': 'Rolv Råen',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """This is the module to manage the accounting chart for Norway in Orj.

Updated for Orj 9 by Bringsvor Consulting AS <www.bringsvor.com>
""",
    'depends': [
        'base_iban',
        'base_vat',
        'account',
    ],
    'auto_install': ['account'],
    'data': [
        'data/account_tax_report_data.xml',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'post_init_hook': '_preserve_tag_on_taxes',
    'license': 'LGPL-3',
}

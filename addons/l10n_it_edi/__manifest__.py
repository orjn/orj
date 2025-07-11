# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'Italy - E-invoicing',
    'version': '0.4',
    'depends': [
        'l10n_it',
        'account_edi_proxy_client',
    ],
    'auto_install': ['l10n_it'],
    'description': """
E-invoice implementation
    """,
    'category': 'Accounting/Localizations/EDI',
    'website': 'http://www.orj.net/',
    'data': [
        'security/ir.model.access.csv',
        'data/invoice_it_template.xml',
        'data/invoice_it_simplified_template.xml',
        'data/ir_cron.xml',
        'data/account.account.tag.csv',
        'views/res_config_settings_views.xml',
        'views/l10n_it_view.xml',
        'views/report_invoice.xml',
    ],
    'demo': [
        'data/account_invoice_demo.xml',
    ],
    'license': 'LGPL-3',
}

# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': "Payment - Account",
    'category': 'Accounting/Accounting',
    'summary': "Enable customers to pay invoices on the portal and post payments when transactions are processed.",
    'version': '2.0',
    'depends': ['account', 'payment'],
    'auto_install': ['account'],
    'data': [
        'data/ir_config_parameter.xml',
        'data/onboarding_data.xml',

        'security/ir.model.access.csv',
        'security/ir_rules.xml',

        'views/account_payment_menus.xml',
        'views/account_portal_templates.xml',
        'views/account_move_views.xml',
        'views/account_journal_views.xml',
        'views/account_payment_views.xml',
        'views/payment_form_templates.xml',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',

        'wizards/account_payment_register_views.xml',
        'wizards/payment_link_wizard_views.xml',
        'wizards/payment_refund_wizard_views.xml',
        'wizards/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'account_payment/static/src/js/payment_form.js',
            'account_payment/static/src/js/portal_invoice_page_payment.js',
            'account_payment/static/src/js/portal_my_invoices_payment.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}

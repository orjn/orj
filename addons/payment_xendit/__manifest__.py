# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': "Payment Provider: Xendit",
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "A payment provider for Indonesian and the Philippines.",
    'description': " ",  # Non-empty string to avoid loading the README file.
    'depends': ['payment'],
    'data': [
        'views/payment_provider_views.xml',
        'views/payment_xendit_templates.xml',

        'data/payment_provider_data.xml',  # Depends on payment_xendit_templates.xml
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'payment_xendit/static/src/**/*',
        ]
    },
    'license': 'LGPL-3',
}

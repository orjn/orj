{
    'name': 'Orj 18 Recurring Payment',
    'author': 'Orj',
    'category': 'Accounting',
    'version': '1.0.0',
    'description': """Orj 18 Recurring Payment, Recurring Payment In Orj, Orj 18 Accounting""",
    'summary': 'Use recurring payments to handle periodically repeated payments',
    'sequence': 11,
    'website': 'https://www.orjmates.tech',
    'depends': ['account'],
    'license': 'LGPL-3',
    'data': [
        'data/sequence.xml',
        'data/recurring_cron.xml',
        'security/ir.model.access.csv',
        'views/recurring_template_view.xml',
        'views/recurring_payment_view.xml'
    ],
    'images': ['static/description/banner.png'],
}

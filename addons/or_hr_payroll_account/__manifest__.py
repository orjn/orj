{
    'name': 'Orj 18 HR Payroll Accounting',
    'category': 'Generic Modules/Human Resources',
    'author': 'Orj, Orj SA',
    'version': '1.0.0',
    'sequence': 1,
    'website': 'https://www.orjmates.tech',
    'license': 'LGPL-3',
    'live_test_url': 'https://www.youtube.com/watch?v=0kaHMTtn7oY',
    'summary': 'Generic Payroll system Integrated with Accounting',
    'description': """Generic Payroll system Integrated with Accounting.""",
    'depends': [
        'or_hr_payroll',
        'account'
    ],
    'data': [
        'views/hr_payroll_account_views.xml'
    ],
    'images': ['static/description/banner.png'],
    'application': True,
}

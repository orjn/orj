{
    'name': 'Orj 18 Accounting Community',
    'version': '1.0.3',
    'category': 'Accounting',
    'summary': 'Accounting Reports, Asset Management and Budget, Recurring Payments, '
               'Lock Dates, Fiscal Year, Accounting Dashboard, Financial Reports, '
               'Customer Follow up Management, Bank Statement Import',
    'description': 'Orj 18 Financial Reports, Asset Management and '
                   'Budget, Financial Reports, Recurring Payments, '
                   'Bank Statement Import, Customer Follow Up Management,'
                   'Account Lock Date, Accounting Dashboard',
    'live_test_url': 'https://www.youtube.com/c/OrjMates',
    'sequence': '1',
    'sequence': '1',
    'website': 'https://www.walnutit.com',
    'author': 'Orj, Walnut Software Solutions, Orj SA',
    'maintainer': 'Orj, Walnut Software Solutions',
    'license': 'LGPL-3',
    'support': 'orjmates@gmail.com',
    'depends': [
        'accounting_pdf_reports',
        'or_account_asset',
        'or_account_budget',
        'or_fiscal_year',
        'or_recurring_payments',
        'or_account_daily_reports',
        'or_account_followup',
    ],
    'data': [
        'security/group.xml',
        'views/menu.xml',
        'views/settings.xml',
        'views/account_group.xml',
        'views/account_tag.xml',
        'views/res_partner.xml',
        'views/account_bank_statement.xml',
        'views/payment_method.xml',
        'views/reconciliation.xml',
        'views/account_journal.xml',
    ],
    'application': True,
    'images': ['static/description/banner.gif'],
}


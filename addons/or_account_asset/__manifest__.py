{
    'name': 'Orj 18 Assets Management',
    'version': '1.0.0',
    'author': 'Orj, Orj SA',
    'depends': ['account'],
    'description': """Manage assets owned by a company or a person. 
        Keeps track of depreciation's, and creates corresponding journal entries""",
    'summary': 'Orj 18 Assets Management',
    'category': 'Accounting',
    'sequence': 10,
    'website': 'https://www.orjmates.tech',
    'license': 'LGPL-3',
    'images': ['static/description/assets.gif'],
    'data': [
        'data/account_asset_data.xml',
        'security/account_asset_security.xml',
        'security/ir.model.access.csv',
        'wizard/asset_depreciation_confirmation_wizard_views.xml',
        'wizard/asset_modify_views.xml',
        'views/account_asset_views.xml',
        'views/account_move_views.xml',
        'views/account_asset_templates.xml',
        'views/asset_category_views.xml',
        'views/product_views.xml',
        'report/account_asset_report_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'or_account_asset/static/src/scss/account_asset.scss',
        ],
    },
}

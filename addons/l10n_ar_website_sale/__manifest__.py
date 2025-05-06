# Part of Orj. See LICENSE file for full copyright and licensing details.
{
    'name': 'Argentinean eCommerce',
    'version': '1.0',
    'category': 'Accounting/Localizations/Website',
    'sequence': 14,
    'author': 'Orj S.A., ADHOC SA',
    'description': """Be able to see Identification Type and AFIP Responsibility in ecommerce checkout form.""",
    'depends': [
        'website_sale',
        'l10n_ar',
    ],
    'data': [
        'data/ir_model_fields.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/website_demo.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}

{
    'name': 'OrLMS Theme',
    'summary': 'OrLMS Theme',
    'website' : 'https://orl.org/',
    'category': 'Theme',
    'version': '18.0.1.0',
    'author': 'OrLMS',
    'depends': [
        'website',
        'theme_default',
    ],
    'data': [
        'views/homepage.xml',

    ],
    'assets': {
        'web._assets_primary_variables': [
            '/theme_web_orl/static/src/scss/primary_variables.scss',
        ],
        'web.assets_frontend': [
            '/theme_web_orl/static/src/scss/style.scss',
            '/theme_web_orl/static/src/js/home.js',
        ],
    },
    'images': [

        'static/description/theme_web_orl_cover.jpg',

        'static/description/theme_web_orl_screenshot.jpg',

    ],

    'license': 'LGPL-3',
    'application': True,
    'installable': True,
}
##############################################################################

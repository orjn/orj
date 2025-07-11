# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'IoT Box Homepage',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'website': 'https://www.orj.net/app/point-of-sale-hardware',
    'summary': 'A homepage for the IoT Box',
    'description': """
IoT Box Homepage
================

This module overrides Orj web interface to display a simple
Homepage that explains what's the iotbox and shows the status,
and where to find documentation.

If you activate this module, you won't be able to access the 
regular Orj interface anymore.

""",
    'assets': {
        'web.assets_backend': [
            'hw_posbox_homepage/static/**/*',
        ],
    },
    'installable': False,
    'license': 'LGPL-3',
}

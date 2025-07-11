# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'Test - Base Automation',
    'version': '1.0',
    'category': 'Hidden',
    'sequence': 9877,
    'summary': 'Base Automation Tests: Ensure Flow Robustness',
    'description': """This module contains tests related to base automation. Those are
present in a separate module as it contains models used only to perform
tests independently to functional aspects of other models.""",
    'depends': ['base_automation'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_tests': [
            'test_base_automation/static/tests/**/*',
        ],
    },
    'installable': True,
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from orj.addons.crm.tests.common import TestCrmCommon
from orj.addons.crm_iap_mine.tests.common import MockIAPReveal  # MockIAPEnrich
from orj.addons.website.tests.test_website_visitor import MockVisitor


class TestCrmFullCommon(TestCrmCommon, MockIAPReveal, MockVisitor):

    @classmethod
    def setUpClass(cls):
        super(TestCrmFullCommon, cls).setUpClass()
        cls._activate_multi_company()

        # Context data: dates
        # ------------------------------------------------------------

        # Mock dates to have reproducible computed fields based on time
        cls.reference_now = datetime(2022, 1, 1, 10, 0, 0)
        cls.reference_today = datetime(2022, 1, 1)

        # Customers
        # ------------------------------------------------------------

        country_be = cls.env.ref('base.be')
        cls.env['res.lang']._activate_lang('fr_BE')

        cls.partners = cls.env['res.partner'].create([
            {'country_id': country_be.id,
             'email': 'partner.email.%02d@test.example.com' % idx,
             'function': 'Noisy Customer',
             'lang': 'fr_BE',
             'mobile': '04569999%02d' % idx,
             'name': 'PartnerCustomer',
             'phone': '04560000%02d' % idx,
             'street': 'Super Street, %092d' % idx,
             'zip': '1400',
            } for idx in range(0, 10)
        ])

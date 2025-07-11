# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta

from orj.addons.account.tests.common import AccountTestInvoicingCommon


class TestMembershipCommon(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Test memberships
        cls.membership_1 = cls.env['product.product'].create({
            'membership': True,
            'membership_date_from': datetime.date.today() + relativedelta(days=-2),
            'membership_date_to': datetime.date.today() + relativedelta(months=1),
            'name': 'Basic Limited',
            'type': 'service',
            'list_price': 100.00,
        })

        # Test people
        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Ignasse Reblochon',
        })
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Martine Poulichette',
            'free_member': True,
        })

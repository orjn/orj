# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.addons.utm.tests.common import TestUTMCommon
from orj.exceptions import UserError
from orj.tests.common import tagged, users


@tagged('post_install', '-at_install', 'utm', 'utm_consistency')
class TestUTMConsistency(TestUTMCommon):

    @users('__system__')
    def test_utm_consistency(self):
        """ You are not supposed to delete the 'utm_medium_email' record as it is hardcoded in
        some functional flows, notably in HR and Mass Mailing. """

        with self.assertRaises(UserError):
            self.env.ref('utm.utm_medium_email').unlink()

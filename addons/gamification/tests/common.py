# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.addons.base.tests.common import HttpCaseWithUserDemo, TransactionCaseWithUserDemo


class HttpCaseGamification(HttpCaseWithUserDemo):

    def setUp(self):
        super().setUp()
        if not self.user_demo.karma:
            self.user_demo.karma = 2500


class TransactionCaseGamification(TransactionCaseWithUserDemo):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not cls.user_demo.karma:
            cls.user_demo.karma = 2500

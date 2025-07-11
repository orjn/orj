# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import Command
from orj.tests.common import TransactionCase, new_test_user

class DashboardTestCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = cls.env["res.groups"].create({"name": "test group"})
        cls.user = new_test_user(cls.env, login="Raoul")
        cls.user.groups_id |= cls.group

    def create_dashboard(self, group=None):
        dashboard_group = group or self.env["spreadsheet.dashboard.group"].create({
            "name": "Dashboard group"
        })
        dashboard = self.env["spreadsheet.dashboard"].create(
            {
                "name": "a dashboard",
                "group_ids": [Command.set(self.group.ids)],
                "dashboard_group_id": dashboard_group.id,
            }
        )
        return dashboard

    def share_dashboard(self, dashboard):
        share = self.env["spreadsheet.dashboard.share"].create(
            {
                "dashboard_id": dashboard.id,
                "spreadsheet_data": dashboard.spreadsheet_data,
            }
        )
        return share

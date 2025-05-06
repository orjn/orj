# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestDiscussAction(HttpCase):
    def test_go_back_to_thread_from_breadcrumbs(self):
        self.start_tour(
            "/orj/discuss?active_id=mail.box_inbox",
            "discuss_go_back_to_thread_from_breadcrumbs.js",
            login="admin",
        )

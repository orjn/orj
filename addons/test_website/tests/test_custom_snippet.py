# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import orj.tests
from orj.tools import mute_logger


@orj.tests.common.tagged('post_install', '-at_install')
class TestCustomSnippet(orj.tests.HttpCase):

    @mute_logger('orj.addons.http_routing.models.ir_http', 'orj.http')
    def test_01_run_tour(self):
        self.start_tour(self.env['website'].get_client_action_url('/'), 'test_custom_snippet', login="admin")

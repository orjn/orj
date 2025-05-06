# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import orj.tests

@orj.tests.tagged("post_install", "-at_install")
class TestOrjEditor(orj.tests.HttpCase):

    def test_orj_editor_suite(self):
        self.browser_js('/web_editor/tests', "", "", login='admin', timeout=1800)

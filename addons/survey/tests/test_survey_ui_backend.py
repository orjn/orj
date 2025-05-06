# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestUi(HttpCase):

    def test_tour_test_survey_form_triggers(self):
        self.start_tour('/orj', 'survey_tour_test_survey_form_triggers', login='admin')

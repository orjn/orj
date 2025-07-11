# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import orj
import orj.tests

@orj.tests.tagged('-at_install', 'post_install')
class TestWebsiteSettings(orj.tests.HttpCase):
    def test_01_multi_website_settings(self):
        # If not enabled (like in demo data), landing on res.config will try
        # to disable module_sale_quotation_builder and raise an issue
        group_order_template = self.env.ref('sale_management.group_sale_order_template', raise_if_not_found=False)
        if group_order_template:
            self.env.ref('base.group_user').write({"implied_ids": [(4, group_order_template.id)]})
        self.env['website'].create({'name': "Website Test Settings", 'specific_user_account': True})
        self.start_tour("/orj", 'website_settings_m2o_dirty', login="admin")

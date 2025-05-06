# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import orj
from orj.tests import HttpCase

@orj.tests.tagged('-at_install', 'post_install')
class TestImLivechatSupportPage(HttpCase):
    def test_load_modules(self):
        """Checks that all javascript modules load correctly on the livechat support page"""

        # Give some time to the assets to load to prevent fetch
        # interrupt errors then ensures all the assets are loaded.
        check_js_modules = """
            orj.livechatReady.then(() => {
                const errors = orj.loader.findErrors();
                if (Object.keys(errors).length) {
                    console.error(
                        "Couldn't load all JS modules.",
                        errors
                    );
                } else {
                    console.log("test successful");
                }
                Object.assign(console, {
                    log: () => {},
                    error: () => {},
                    warn: () => {},
                });
            })
        """
        self.browser_js("/im_livechat/support/1", code=check_js_modules)

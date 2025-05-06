# Part of Orj. See LICENSE file for full copyright and licensing details.

import orj.tests


@orj.tests.common.tagged('post_install', '-at_install')
class TestSnippetBackgroundVideo(orj.tests.HttpCase):

    def test_snippet_background_video(self):
        self.start_tour("/", "snippet_background_video", login="admin")

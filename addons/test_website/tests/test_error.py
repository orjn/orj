import orj.tests
from orj.tools import mute_logger


@orj.tests.common.tagged('post_install', '-at_install')
class TestWebsiteError(orj.tests.HttpCase):

    @mute_logger('orj.addons.http_routing.models.ir_http', 'orj.http')
    def test_01_run_test(self):
        self.start_tour("/test_error_view", 'test_error_website')

import orj
from orj.addons.web.tests.test_js import unit_test_error_checker


@orj.tests.tagged("post_install", "-at_install")
class ExternalTestSuite(orj.tests.HttpCase):
    def test_external_livechat(self):
        # webclient external test suite
        self.browser_js(
            "/web/tests/livechat?headless&loglevel=2&preset=desktop",
            "",
            "",
            login='admin',
            timeout=1800,
            success_signal="[HOOT] test suite succeeded",
            error_checker=unit_test_error_checker
        )

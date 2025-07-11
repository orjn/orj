import logging

from orj.addons.auth_totp.tests.test_totp import TestTOTPMixin
from orj.addons.base.tests.common import HttpCaseWithUserPortal
from orj.tests import tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestTOTPortal(HttpCaseWithUserPortal, TestTOTPMixin):
    """
    Largely replicates TestTOTP
    """
    def test_totp(self):
        self.install_totphook()

        self.start_tour('/my/security', 'totportal_tour_setup', login='portal')
        # also disables totp otherwise we can't re-login
        self.start_tour('/', 'totportal_login_enabled', login=None)
        self.start_tour('/', 'totportal_login_disabled', login=None)

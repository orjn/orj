# -*- coding: utf-8 -*-
import logging
import orj.addons.auth_totp.controllers.home

from orj import http
from orj.exceptions import AccessDenied, UserError
from orj.http import request

_logger = logging.getLogger(__name__)


class Home(orj.addons.auth_totp.controllers.home.Home):
    @http.route()
    def web_totp(self, redirect=None, **kwargs):
        response = super().web_totp(redirect=redirect, **kwargs)
        if response.status_code != 200 or response.qcontext['user']._mfa_type() != 'totp_mail':
            # In case the response from the super is a redirection
            # or the user has another TOTP method, we return the response from the call to super.
            return response
        assert request.session.pre_uid and not request.session.uid, \
            "The user must still be in the pre-authentication phase"

        # Send the email containing the code to the user inbox
        try:
            response.qcontext['user']._send_totp_mail_code()
        except (AccessDenied, UserError) as e:
            response.qcontext['error'] = str(e)
        except Exception as e:
            _logger.exception('Unable to send TOTP email')
            response.qcontext['error'] = str(e)
        return response

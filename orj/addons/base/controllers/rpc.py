import re
import sys
import traceback
import xmlrpc.client
from datetime import date, datetime

from collections import defaultdict
from markupsafe import Markup

import orj
from orj.http import Controller, route, dispatch_rpc, request, Response
from orj.fields import Date, Datetime, Command
from orj.tools import lazy
from orj.tools.misc import frozendict

# ==========================================================
# XML-RPC helpers
# ==========================================================

# XML-RPC fault codes. Some care must be taken when changing these: the
# constants are also defined client-side and must remain in sync.
# User code must use the exceptions defined in ``orj.exceptions`` (not
# create directly ``xmlrpc.client.Fault`` objects).
RPC_FAULT_CODE_CLIENT_ERROR = 1 # indistinguishable from app. error.
RPC_FAULT_CODE_APPLICATION_ERROR = 1
RPC_FAULT_CODE_WARNING = 2
RPC_FAULT_CODE_ACCESS_DENIED = 3
RPC_FAULT_CODE_ACCESS_ERROR = 4

# 0 to 31, excluding tab, newline, and carriage return
CONTROL_CHARACTERS = dict.fromkeys(set(range(32)) - {9, 10, 13})


def xmlrpc_handle_exception_int(e):
    if isinstance(e, orj.exceptions.RedirectWarning):
        fault = xmlrpc.client.Fault(RPC_FAULT_CODE_WARNING, str(e))
    elif isinstance(e, orj.exceptions.AccessError):
        fault = xmlrpc.client.Fault(RPC_FAULT_CODE_ACCESS_ERROR, str(e))
    elif isinstance(e, orj.exceptions.AccessDenied):
        fault = xmlrpc.client.Fault(RPC_FAULT_CODE_ACCESS_DENIED, str(e))
    elif isinstance(e, orj.exceptions.UserError):
        fault = xmlrpc.client.Fault(RPC_FAULT_CODE_WARNING, str(e))
    else:
        info = sys.exc_info()
        formatted_info = "".join(traceback.format_exception(*info))
        fault = xmlrpc.client.Fault(RPC_FAULT_CODE_APPLICATION_ERROR, formatted_info)

    return dumps(fault)


def xmlrpc_handle_exception_string(e):
    if isinstance(e, orj.exceptions.RedirectWarning):
        fault = xmlrpc.client.Fault('warning -- Warning\n\n' + str(e), '')
    elif isinstance(e, orj.exceptions.MissingError):
        fault = xmlrpc.client.Fault('warning -- MissingError\n\n' + str(e), '')
    elif isinstance(e, orj.exceptions.AccessError):
        fault = xmlrpc.client.Fault('warning -- AccessError\n\n' + str(e), '')
    elif isinstance(e, orj.exceptions.AccessDenied):
        fault = xmlrpc.client.Fault('AccessDenied', str(e))
    elif isinstance(e, orj.exceptions.UserError):
        fault = xmlrpc.client.Fault('warning -- UserError\n\n' + str(e), '')
    #InternalError
    else:
        info = sys.exc_info()
        formatted_info = "".join(traceback.format_exception(*info))
        fault = xmlrpc.client.Fault(orj.tools.exception_to_unicode(e), formatted_info)

    return dumps(fault)


class OrjMarshaller(xmlrpc.client.Marshaller):
    dispatch = dict(xmlrpc.client.Marshaller.dispatch)

    def dump_frozen_dict(self, value, write):
        value = dict(value)
        self.dump_struct(value, write)

    # By default, in xmlrpc, bytes are converted to xmlrpc.client.Binary object.
    # Historically, orj is sending binary as base64 string.
    # In python 3, base64.b64{de,en}code() methods now works on bytes.
    def dump_bytes(self, value, write):
        self.dump_unicode(value.decode(), write)

    def dump_datetime(self, value, write):
        # override to marshall as a string for backwards compatibility
        value = Datetime.to_string(value)
        self.dump_unicode(value, write)

    # convert date objects to strings in iso8061 format.
    def dump_date(self, value, write):
        value = Date.to_string(value)
        self.dump_unicode(value, write)

    def dump_lazy(self, value, write):
        v = value._value
        return self.dispatch[type(v)](self, v, write)

    def dump_unicode(self, value, write):
        # XML 1.0 disallows control characters, remove them otherwise they break clients
        return super().dump_unicode(value.translate(CONTROL_CHARACTERS), write)

    dispatch[frozendict] = dump_frozen_dict
    dispatch[bytes] = dump_bytes
    dispatch[datetime] = dump_datetime
    dispatch[date] = dump_date
    dispatch[lazy] = dump_lazy
    dispatch[str] = dump_unicode
    dispatch[Command] = dispatch[int]
    dispatch[defaultdict] = dispatch[dict]
    dispatch[Markup] = lambda self, value, write: self.dispatch[str](self, str(value), write)


def dumps(params: list | tuple | xmlrpc.client.Fault) -> str:
    response = OrjMarshaller(allow_none=False).dumps(params)
    return f"""\
<?xml version="1.0"?>
<methodResponse>
{response}
</methodResponse>
"""

# ==========================================================
# RPC Controller
# ==========================================================


def _check_request():
    if request.db:
        request.env.cr.close()

class RPC(Controller):
    """Handle RPC connections."""

    def _xmlrpc(self, service):
        """Common method to handle an XML-RPC request."""
        _check_request()
        data = request.httprequest.get_data()
        params, method = xmlrpc.client.loads(data, use_datetime=True)
        result = dispatch_rpc(service, method, params)
        return dumps((result,))

    @route("/xmlrpc/<service>", auth="none", methods=["POST"], csrf=False, save_session=False)
    def xmlrpc_1(self, service):
        """XML-RPC service that returns faultCode as strings.

        This entrypoint is historical and non-compliant, but kept for
        backwards-compatibility.
        """
        _check_request()
        try:
            response = self._xmlrpc(service)
        except Exception as error:
            error.error_response = Response(
                response=xmlrpc_handle_exception_string(error),
                mimetype='text/xml',
            )
            raise
        return Response(response=response, mimetype='text/xml')

    @route("/xmlrpc/2/<service>", auth="none", methods=["POST"], csrf=False, save_session=False)
    def xmlrpc_2(self, service):
        """XML-RPC service that returns faultCode as int."""
        _check_request()
        try:
            response = self._xmlrpc(service)
        except Exception as error:
            error.error_response = Response(
                response=xmlrpc_handle_exception_int(error),
                mimetype='text/xml',
            )
            raise
        return Response(response=response, mimetype='text/xml')

    @route('/jsonrpc', type='json', auth="none", save_session=False)
    def jsonrpc(self, service, method, args):
        """ Method used by client APIs to contact Orj. """
        _check_request()
        return dispatch_rpc(service, method, args)

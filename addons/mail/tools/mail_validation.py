# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
import logging

from orj import tools

_logger = logging.getLogger(__name__)

_flanker_lib_warning = False

try:
    from flanker.addresslib import address
    # Avoid warning each time a mx server is not reachable by flanker
    logging.getLogger("flanker.addresslib.validate").setLevel(logging.ERROR)

    def mail_validate(email):
        return bool(address.validate_address(email))

except ImportError:

    def mail_validate(email):
        global _flanker_lib_warning
        if not _flanker_lib_warning:
            _flanker_lib_warning = True
            _logger.info("The (optional) `flanker` Python module is not installed,"
                         "so email validation will fallback to email_normalize.")
        return tools.email_normalize(email)

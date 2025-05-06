# -*- coding: utf-8 -*-

from orj import models
from orj.api import Environment
from orj.fields import Datetime
from orj.http import request
from orj.modules.registry import Registry
from orj.addons.bus.websocket import wsrequest

class IrWebsocket(models.AbstractModel):
    _inherit = 'ir.websocket'

    def _update_bus_presence(self, inactivity_period, im_status_ids_by_model):
        super()._update_bus_presence(inactivity_period, im_status_ids_by_model)
        #  This method can either be called due to an http or a
        #  websocket request. The request itself is necessary to
        #  retrieve the current guest. Let's retrieve the proper
        #  request.
        req = request or wsrequest
        if req.env.user._is_internal():
            ip_address = req.httprequest.remote_addr
            users_log = req.env['res.users.log'].sudo().search_count([
                ('create_uid', '=', req.env.user.id),
                ('ip', '=', ip_address),
                ('create_date', '>=', Datetime.to_string(Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)))])
            if not users_log:
                with Registry(req.env.cr.dbname).cursor() as cr:
                    env = Environment(cr, req.env.user.id, {})
                    env['res.users.log'].sudo().create({'ip': ip_address})

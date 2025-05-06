# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models
from orj.modules.loading import force_demo
from orj.addons.base.models.ir_module import assert_log_admin_access


class IrDemo(models.TransientModel):

    _name = 'ir.demo'
    _description = 'Demo'

    @assert_log_admin_access
    def install_demo(self):
        force_demo(self.env)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/orj',
        }

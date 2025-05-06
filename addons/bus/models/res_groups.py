# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class ResGroups(models.Model):
    _name = "res.groups"
    _inherit = ["res.groups", "bus.listener.mixin"]

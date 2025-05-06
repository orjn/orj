# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import api, models


class ResCity(models.Model):
    _name = "res.city"
    _inherit = ["res.city", "pos.load.mixin"]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ["name", "country_id", "state_id"]

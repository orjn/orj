# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models, api


class ProductTag(models.Model):
    _name = 'product.tag'
    _inherit = ['product.tag', 'pos.load.mixin']

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['name']

# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    visibility = fields.Selection(
        selection=[('visible', "Visible"), ('hidden', "Hidden")],
        default='visible',
    )

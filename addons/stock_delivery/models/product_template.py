# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hs_code = fields.Char(
        string="HS Code",
        help="Standardized code for international shipping and goods declaration.",
    )
    country_of_origin = fields.Many2one(
        'res.country',
        'Origin of Goods',
        help="Rules of origin determine where goods originate, i.e. not where they have been shipped from, but where they have been produced or manufactured.\n"
             "As such, the ‘origin’ is the 'economic nationality' of goods traded in commerce.",
    )

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, models, _


class UoM(models.Model):
    _inherit = 'uom.uom'

    @api.onchange('rounding')
    def _onchange_rounding(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        if self.rounding < 1.0 / 10.0**precision:
            return {'warning': {
                'title': _('Warning!'),
                'message': _(
                    "This rounding precision is higher than the Decimal Accuracy"
                    " (%(digits)s digits).\nThis may cause inconsistencies in computations.\n"
                    "Please set a precision between %(min_precision)s and 1.",
                    digits=precision, min_precision=1.0 / 10.0**precision),
            }}

# coding: utf-8
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _force_http(self):
        enforce_https = self.env['ir.config_parameter'].sudo().get_param('point_of_sale.enforce_https')
        if not enforce_https and self.payment_method_ids.filtered(lambda pm: pm.use_payment_terminal == 'six'):
            return True
        return super(PosConfig, self)._force_http()

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.payment'

    def _update_payment_line_for_tip(self, tip_amount):
        """Inherit this method to perform reauthorization or capture on electronic payment."""
        self.ensure_one()
        self.write({
            "amount": self.amount + tip_amount,
        })

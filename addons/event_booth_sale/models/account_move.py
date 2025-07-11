# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _invoice_paid_hook(self):
        """ When an invoice linked to a sales order selling registrations is
        paid, update booths accordingly as they are booked when invoice is paid.
        """
        res = super(AccountMove, self)._invoice_paid_hook()
        self.mapped('line_ids.sale_line_ids')._update_event_booths(set_paid=True)
        return res

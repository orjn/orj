# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj import models, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('country_code', 'partner_type')
    def _compute_payment_receipt_title(self):
        # OVERRIDE
        super()._compute_payment_receipt_title()
        for payment in self.filtered(lambda p: p.country_code == 'AU' and p.partner_type == 'supplier'):
            payment.payment_receipt_title = _('Remittance Advice')

# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models


class PaymentCaptureWizard(models.TransientModel):
    _inherit = 'payment.capture.wizard'

    has_adyen_tx = fields.Boolean(compute='_compute_has_adyen_tx')

    @api.depends('transaction_ids')
    def _compute_has_adyen_tx(self):
        for wizard in self:
            wizard.has_adyen_tx = any(tx.provider_code == 'adyen' for tx in wizard.transaction_ids)

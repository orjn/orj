# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_picking(self):
        res = super()._prepare_picking()
        if not self.project_id:
            return res
        return {
            **res,
            'project_id': self.project_id.id,
        }

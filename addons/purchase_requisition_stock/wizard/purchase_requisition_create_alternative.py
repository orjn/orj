# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, Command, models


class PurchaseRequisitionCreateAlternative(models.TransientModel):
    _inherit = 'purchase.requisition.create.alternative'

    def _get_alternative_values(self):
        vals = super(PurchaseRequisitionCreateAlternative, self)._get_alternative_values()
        vals.update({
            'picking_type_id': self.origin_po_id.picking_type_id.id,
            'group_id': self.origin_po_id.group_id.id,
        })
        return vals

    @api.model
    def _get_alternative_line_value(self, order_line):
        res_line = super()._get_alternative_line_value(order_line)
        if order_line.move_dest_ids:
            res_line['move_dest_ids'] = [Command.set(order_line.move_dest_ids.ids)]

        return res_line

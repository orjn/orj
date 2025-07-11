# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models, _


class ChooseDeliveryPackage(models.TransientModel):
    _name = 'choose.delivery.package'
    _description = 'Delivery Package Selection Wizard'

    picking_id = fields.Many2one('stock.picking', 'Picking')
    delivery_package_type_id = fields.Many2one('stock.package.type', 'Delivery Package Type', check_company=True)
    shipping_weight = fields.Float('Shipping Weight', compute='_compute_shipping_weight', store=True, readonly=False)
    weight_uom_name = fields.Char(string='Weight unit of measure label', compute='_compute_weight_uom_name')
    company_id = fields.Many2one(related='picking_id.company_id')

    @api.depends('delivery_package_type_id')
    def _compute_weight_uom_name(self):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        for package in self:
            package.weight_uom_name = weight_uom_id.name

    @api.depends('delivery_package_type_id')
    def _compute_shipping_weight(self):
        for rec in self:
            move_line_ids = rec.picking_id._package_move_lines(
                batch_pack=self.env.context.get('batch_pack')
            )
            # Add package weights to shipping weight, package base weight is defined in package.type
            total_weight = rec.delivery_package_type_id.base_weight or 0.0
            for ml in move_line_ids:
                qty = ml.product_uom_id._compute_quantity(ml.quantity, ml.product_id.uom_id)
                total_weight += qty * ml.product_id.weight
            rec.shipping_weight = total_weight

    @api.onchange('delivery_package_type_id', 'shipping_weight')
    def _onchange_package_type_weight(self):
        if self.delivery_package_type_id.max_weight and self.shipping_weight > self.delivery_package_type_id.max_weight:
            warning_mess = {
                'title': _('Package too heavy!'),
                'message': _('The weight of your package is higher than the maximum weight authorized for this package type. Please choose another package type.')
            }
            return {'warning': warning_mess}

    def action_put_in_pack(self):
        move_line_ids = self.picking_id._package_move_lines(batch_pack=self.env.context.get("batch_pack"))
        delivery_package = self.picking_id._put_in_pack(move_line_ids)
        # write shipping weight and package type on 'stock_quant_package' if needed
        if self.delivery_package_type_id:
            delivery_package.package_type_id = self.delivery_package_type_id
        if self.shipping_weight:
            delivery_package.shipping_weight = self.shipping_weight
        return self.picking_id._post_put_in_pack_hook(delivery_package)

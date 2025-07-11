# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models, _


class SupplierInfo(models.Model):
    _name = "product.supplierinfo"
    _description = "Supplier Pricelist"
    _order = 'sequence, min_qty DESC, price, id'
    _rec_name = 'partner_id'

    def _default_product_id(self):
        product_id = self.env.get('default_product_id')
        if not product_id:
            model, active_id = [self.env.context.get(k) for k in ['model', 'active_id']]
            if model == 'product.product' and active_id:
                product_id = self.env[model].browse(active_id).exists()
        return product_id

    partner_id = fields.Many2one(
        'res.partner', 'Vendor',
        ondelete='cascade', required=True,
        check_company=True)
    product_name = fields.Char(
        'Vendor Product Name',
        help="This vendor's product name will be used when printing a request for quotation. Keep empty to use the internal one.")
    product_code = fields.Char(
        'Vendor Product Code',
        help="This vendor's product code will be used when printing a request for quotation. Keep empty to use the internal one.")
    sequence = fields.Integer(
        'Sequence', default=1, help="Assigns the priority to the list of product vendor.")
    product_uom = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        related='product_tmpl_id.uom_po_id')
    min_qty = fields.Float(
        'Quantity', default=0.0, required=True, digits="Product Unit of Measure",
        help="The quantity to purchase from this vendor to benefit from the price, expressed in the vendor Product Unit of Measure if not any, in the default unit of measure of the product otherwise.")
    price = fields.Float(
        'Price', default=0.0, digits='Product Price',
        required=True, help="The price to purchase a product")
    price_discounted = fields.Float('Discounted Price', compute='_compute_price_discounted')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company.id, index=1)
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True)
    date_start = fields.Date('Start Date', help="Start date for this vendor price")
    date_end = fields.Date('End Date', help="End date for this vendor price")
    product_id = fields.Many2one(
        'product.product', 'Product Variant', check_company=True,
        domain="[('product_tmpl_id', '=', product_tmpl_id)] if product_tmpl_id else []",
        default=_default_product_id,
        help="If not set, the vendor price will apply to all variants of this product.")
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template', check_company=True,
        index=True, ondelete='cascade')
    product_variant_count = fields.Integer('Variant Count', related='product_tmpl_id.product_variant_count')
    delay = fields.Integer(
        'Delivery Lead Time', default=1, required=True,
        help="Lead time in days between the confirmation of the purchase order and the receipt of the products in your warehouse. Used by the scheduler for automatic computation of the purchase order planning.")
    discount = fields.Float(
        string="Discount (%)",
        digits='Discount',
        readonly=False)

    @api.depends('discount', 'price')
    def _compute_price_discounted(self):
        for rec in self:
            rec.price_discounted = rec.price * (1 - rec.discount / 100)

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        """Clear product variant if it no longer matches the product template."""
        if self.product_id and self.product_id not in self.product_tmpl_id.product_variant_ids:
            self.product_id = False

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Vendor Pricelists'),
            'template': '/product/static/xls/product_supplierinfo.xls'
        }]

    def _sanitize_vals(self, vals):
        """Sanitize vals to sync product variant & template on read/write."""
        # add product's product_tmpl_id if none present in vals
        if  vals.get('product_id') and not vals.get('product_tmpl_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            vals['product_tmpl_id'] = product.product_tmpl_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._sanitize_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._sanitize_vals(vals)
        return super().write(vals)

    def _get_filtered_supplier(self, company_id, product_id, params=False):
        return self.filtered(lambda s: (not s.company_id or s.company_id.id == company_id.id) and (s.partner_id.active and (not s.product_id or s.product_id == product_id)))

# Part of Orj. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from orj import Command, _, api, fields, models
from orj.exceptions import ValidationError
from orj.tools import float_repr


class SaleOrderDiscount(models.TransientModel):
    _name = 'sale.order.discount'
    _description = "Discount Wizard"

    sale_order_id = fields.Many2one(
        'sale.order', default=lambda self: self.env.context.get('active_id'), required=True)
    company_id = fields.Many2one(related='sale_order_id.company_id')
    currency_id = fields.Many2one(related='sale_order_id.currency_id')
    discount_amount = fields.Monetary(string="Amount")
    discount_percentage = fields.Float(string="Percentage")
    discount_type = fields.Selection(
        selection=[
            ('sol_discount', "On All Order Lines"),
            ('so_discount', "Global Discount"),
            ('amount', "Fixed Amount"),
        ],
        default='sol_discount',
    )
    tax_ids = fields.Many2many(
        string="Taxes",
        help="Taxes to add on the discount line.",
        comodel_name='account.tax',
        domain="[('type_tax_use', '=', 'sale'), ('company_id', '=', company_id)]",
    )

    # CONSTRAINT METHODS #

    @api.constrains('discount_type', 'discount_percentage')
    def _check_discount_amount(self):
        for wizard in self:
            if (
                wizard.discount_type in ('sol_discount', 'so_discount')
                and wizard.discount_percentage > 1.0
            ):
                raise ValidationError(_("Invalid discount amount"))

    def _prepare_discount_product_values(self):
        self.ensure_one()
        return {
            'name': _('Discount'),
            'type': 'service',
            'invoice_policy': 'order',
            'list_price': 0.0,
            'company_id': self.company_id.id,
            'taxes_id': None,
        }

    def _prepare_discount_line_values(self, product, amount, taxes, description=None):
        self.ensure_one()

        vals = {
            'order_id': self.sale_order_id.id,
            'product_id': product.id,
            'sequence': 999,
            'price_unit': -amount,
            'tax_id': [Command.set(taxes.ids)],
        }
        if description:
            # If not given, name will fallback on the standard SOL logic (cf. _compute_name)
            vals['name'] = description

        return vals

    def _get_discount_product(self):
        """Return product.product used for discount line"""
        self.ensure_one()
        discount_product = self.company_id.sale_discount_product_id
        if not discount_product:
            if (
                self.env['product.product'].has_access('create')
                and self.company_id.has_access('write')
                and self.company_id._filtered_access('write')
                and self.company_id.check_field_access_rights('write', ['sale_discount_product_id'])
            ):
                self.company_id.sale_discount_product_id = self.env['product.product'].create(
                    self._prepare_discount_product_values()
                )
            else:
                raise ValidationError(_(
                    "There does not seem to be any discount product configured for this company yet."
                    " You can either use a per-line discount, or ask an administrator to grant the"
                    " discount the first time."
                ))
            discount_product = self.company_id.sale_discount_product_id
        return discount_product

    def _create_discount_lines(self):
        """Create SOline(s) according to wizard configuration"""
        self.ensure_one()
        discount_product = self._get_discount_product()

        if self.discount_type == 'amount':
            if not self.sale_order_id.amount_total:
                return
            so_amount = self.sale_order_id.amount_total
            # Fixed taxes cannot be discounted, so they cannot be considered in the total amount
            # when computing the discount percentage.
            if any(tax.amount_type == 'fixed' for tax in self.sale_order_id.order_line.tax_id.flatten_taxes_hierarchy()):
                fixed_taxes_amount = 0
                for line in self.sale_order_id.order_line:
                    taxes = line.tax_id.flatten_taxes_hierarchy()
                    for tax in taxes.filtered(lambda tax: tax.amount_type == 'fixed'):
                        fixed_taxes_amount += tax.amount * line.product_uom_qty
                so_amount -= fixed_taxes_amount
            discount_percentage = self.discount_amount / so_amount
        else: # so_discount
            discount_percentage = self.discount_percentage
        total_price_per_tax_groups = defaultdict(float)
        for line in self.sale_order_id.order_line:
            if not line.product_uom_qty or not line.price_unit:
                continue
            # Fixed taxes cannot be discounted.
            taxes = line.tax_id.flatten_taxes_hierarchy()
            fixed_taxes = taxes.filtered(lambda t: t.amount_type == 'fixed')
            taxes -= fixed_taxes
            total_price_per_tax_groups[taxes] += line.price_unit * (1 - (line.discount or 0.0) / 100) * line.product_uom_qty

        discount_dp = self.env['decimal.precision'].precision_get('Discount')
        context = {'lang': self.sale_order_id._get_lang()}  # noqa: F841
        if not total_price_per_tax_groups:
            # No valid lines on which the discount can be applied
            return
        if len(total_price_per_tax_groups) == 1:
            # No taxes, or all lines have the exact same taxes
            taxes = next(iter(total_price_per_tax_groups.keys()))
            subtotal = total_price_per_tax_groups[taxes]
            vals_list = [{
                **self._prepare_discount_line_values(
                    product=discount_product,
                    amount=subtotal * discount_percentage,
                    taxes=taxes,
                    description=_(
                        "Discount %(percent)s%%",
                        percent=float_repr(discount_percentage * 100, discount_dp),
                    ),
                ),
            }]
        else:
            vals_list = []
            for taxes, subtotal in total_price_per_tax_groups.items():
                discount_line_value = self._prepare_discount_line_values(
                    product=discount_product,
                    amount=subtotal * discount_percentage,
                    taxes=taxes,
                    description=_(
                        "Discount %(percent)s%%"
                        "- On products with the following taxes %(taxes)s",
                        percent=float_repr(discount_percentage * 100, discount_dp),
                        taxes=", ".join(taxes.mapped('name')),
                    ) if self.discount_type != 'amount' else _(
                        "Discount"
                        "- On products with the following taxes %(taxes)s",
                        taxes=", ".join(taxes.mapped('name')),
                    )
                )
                vals_list.append(discount_line_value)
        return self.env['sale.order.line'].create(vals_list)

    def action_apply_discount(self):
        self.ensure_one()
        self = self.with_company(self.company_id)
        if self.discount_type == 'sol_discount':
            self.sale_order_id.order_line.write({'discount': self.discount_percentage*100})
        else:
            self._create_discount_lines()

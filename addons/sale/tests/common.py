# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.fields import Command
from orj.tests import TransactionCase

from orj.addons.account.tests.common import AccountTestInvoicingCommon, TestTaxCommon
from orj.addons.product.tests.common import ProductCommon
from orj.addons.sales_team.tests.common import SalesTeamCommon


class SaleCommon(
    ProductCommon, # BaseCommon, UomCommon
    SalesTeamCommon,
):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env.company.country_id = cls.env.ref('base.us')

        # Not defined in product common because only used in sale
        cls.group_discount_per_so_line = cls.env.ref('sale.group_discount_per_so_line')

        (cls.product + cls.service_product).write({
                'taxes_id': [Command.clear()],
        })

        cls.empty_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
        })
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [
                Command.create({
                    'product_id': cls.product.id,
                    'product_uom_qty': 5.0,
                }),
                Command.create({
                    'product_id': cls.service_product.id,
                    'product_uom_qty': 12.5,
                })
            ]
        })

    @classmethod
    def _enable_pricelists(cls):
        cls.env.user.groups_id += cls.env.ref('product.group_product_pricelist')

    @classmethod
    def _enable_discounts(cls):
        cls.env.user.groups_id += cls.group_discount_per_so_line


class TestSaleCommonBase(TransactionCase):
    ''' Setup with sale test configuration. '''

    @classmethod
    def setup_sale_configuration_for_company(cls, company):
        Users = cls.env['res.users'].with_context(no_reset_password=True)

        company_data = {
            # Sales Team
            'default_sale_team': cls.env['crm.team'].with_context(tracking_disable=True).create({
                'name': 'Test Channel',
                'company_id': company.id,
            }),

            # Users
            'default_user_salesman': Users.create({
                'name': 'default_user_salesman',
                'login': 'default_user_salesman.comp%s' % company.id,
                'email': 'default_user_salesman@example.com',
                'signature': '--\nMark',
                'notification_type': 'email',
                'groups_id': [(6, 0, cls.env.ref('sales_team.group_sale_salesman').ids)],
                'company_ids': [(6, 0, company.ids)],
                'company_id': company.id,
            }),
            'default_user_portal': Users.create({
                'name': 'default_user_portal',
                'login': 'default_user_portal.comp%s' % company.id,
                'email': 'default_user_portal@gladys.portal',
                'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])],
                'company_ids': [(6, 0, company.ids)],
                'company_id': company.id,
            }),
            'default_user_employee': Users.create({
                'name': 'default_user_employee',
                'login': 'default_user_employee.comp%s' % company.id,
                'email': 'default_user_employee@example.com',
                'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
                'company_ids': [(6, 0, company.ids)],
                'company_id': company.id,
            }),

            # Pricelist
            'default_pricelist': cls.env['product.pricelist'].with_company(company).create({
                'name': 'default_pricelist',
                'currency_id': company.currency_id.id,
                'company_id': False,
            }),

            # Product category
            'product_category': cls.env['product.category'].with_company(company).create({
                'name': 'Test category',
            }),
        }

        company_data.update({
            # Products
            'product_service_delivery': cls.env['product.product'].with_company(company).create({
                'name': 'product_service_delivery',
                'categ_id': company_data['product_category'].id,
                'standard_price': 200.0,
                'list_price': 180.0,
                'type': 'service',
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'SERV_DEL',
                'invoice_policy': 'delivery',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
                'company_id': company.id,
            }),
            'product_service_order': cls.env['product.product'].with_company(company).create({
                'name': 'product_service_order',
                'categ_id': company_data['product_category'].id,
                'standard_price': 40.0,
                'list_price': 90.0,
                'type': 'service',
                'uom_id': cls.env.ref('uom.product_uom_hour').id,
                'uom_po_id': cls.env.ref('uom.product_uom_hour').id,
                'description': 'Example of product to invoice on order',
                'default_code': 'PRE-PAID',
                'invoice_policy': 'order',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
                'company_id': company.id,
            }),
            'product_order_cost': cls.env['product.product'].with_company(company).create({
                'name': 'product_order_cost',
                'categ_id': company_data['product_category'].id,
                'standard_price': 235.0,
                'list_price': 280.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_9999',
                'invoice_policy': 'order',
                'expense_policy': 'cost',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
                'company_id': company.id,
            }),
            'product_delivery_cost': cls.env['product.product'].with_company(company).create({
                'name': 'product_delivery_cost',
                'categ_id': company_data['product_category'].id,
                'standard_price': 55.0,
                'list_price': 70.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_7777',
                'invoice_policy': 'delivery',
                'expense_policy': 'cost',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
                'company_id': company.id,
            }),
            'product_order_sales_price': cls.env['product.product'].with_company(company).create({
                'name': 'product_order_sales_price',
                'categ_id': company_data['product_category'].id,
                'standard_price': 235.0,
                'list_price': 280.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_9999',
                'invoice_policy': 'order',
                'expense_policy': 'sales_price',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
                'company_id': company.id,
            }),
            'product_delivery_sales_price': cls.env['product.product'].with_company(company).create({
                'name': 'product_delivery_sales_price',
                'categ_id': company_data['product_category'].id,
                'standard_price': 55.0,
                'list_price': 70.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_7777',
                'invoice_policy': 'delivery',
                'expense_policy': 'sales_price',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
                'company_id': company.id,
            }),
            'product_order_no': cls.env['product.product'].with_company(company).create({
                'name': 'product_order_no',
                'categ_id': company_data['product_category'].id,
                'standard_price': 235.0,
                'list_price': 280.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_9999',
                'invoice_policy': 'order',
                'expense_policy': 'no',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
                'company_id': company.id,
            }),
            'product_delivery_no': cls.env['product.product'].with_company(company).create({
                'name': 'product_delivery_no',
                'categ_id': company_data['product_category'].id,
                'standard_price': 55.0,
                'list_price': 70.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_7777',
                'invoice_policy': 'delivery',
                'expense_policy': 'no',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
                'company_id': company.id,
            }),
        })

        return company_data


class TestSaleCommon(AccountTestInvoicingCommon, TestSaleCommonBase):
    ''' Setup to be used post-install with sale and accounting test configuration.'''

    @classmethod
    def collect_company_accounting_data(cls, company):
        company_data = super().collect_company_accounting_data(company)

        company_data.update(cls.setup_sale_configuration_for_company(company_data['company']))

        company_data['product_category'].write({
            'property_account_income_categ_id': company_data['default_account_revenue'].id,
            'property_account_expense_categ_id': company_data['default_account_expense'].id,
        })

        return company_data


class TestTaxCommonSale(TestTaxCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.foreign_currency_pricelist = cls.env['product.pricelist'].create({
            'name': "TestTaxCommonSale",
            'company_id': cls.env.company.id,
        })

    def convert_document_to_sale_order(self, document):
        order_date = '2020-01-01'
        currency = self.setup_other_currency(document['currency'].name.upper(), rates=[(order_date, document['rate'])])
        self.foreign_currency_pricelist.currency_id = currency
        order = self.env['sale.order'].create({
            'date_order': order_date,
            'currency_id': currency.id,
            'partner_id': self.partner_a.id,
            'pricelist_id': self.foreign_currency_pricelist.id,
            'order_line': [
                Command.create({
                    'name': str(i),
                    'product_id': self.product_a.id,
                    'price_unit': base_line['price_unit'],
                    'discount': base_line['discount'],
                    'product_uom_qty': base_line['quantity'],
                    'tax_id': [Command.set(base_line['tax_ids'].ids)],
                })
                for i, base_line in enumerate(document['lines'])
            ],
        })
        return order

    def assert_sale_order_tax_totals_summary(self, sale_order, expected_values, soft_checking=False):
        self._assert_tax_totals_summary(sale_order.tax_totals, expected_values, soft_checking=soft_checking)
        cash_rounding_base_amount_currency = sale_order.tax_totals.get('cash_rounding_base_amount_currency', 0.0)
        self.assertRecordValues(sale_order, [{
            'amount_untaxed': expected_values['base_amount_currency'] + cash_rounding_base_amount_currency,
            'amount_tax': expected_values['tax_amount_currency'],
            'amount_total': expected_values['total_amount_currency'] + cash_rounding_base_amount_currency,
        }])

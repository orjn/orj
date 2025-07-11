# Part of Orj. See LICENSE file for full copyright and licensing details.

from werkzeug import urls

from orj import Command
from orj.http import root
from orj.tests import tagged

from orj.addons.base.tests.common import HttpCaseWithUserDemo
from orj.addons.website_sale.controllers.main import WebsiteSale


@tagged('at_install')
class TestWebsiteSaleExpressCheckoutFlows(HttpCaseWithUserDemo):
    """ The goal of this method class is to test the address management on
        express checkout.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('website.default_website')
        cls.country_id = cls.env.ref('base.be').id
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.website.user_id.partner_id.id,
            'website_id': cls.website.id,
            'order_line': [Command.create({
                'product_id': cls.env['product.product'].create({
                    'name': 'Product A',
                    'list_price': 100,
                    'website_published': True,
                    'sale_ok': True}).id,
                'name': 'Product A',
            })]
        })
        cls.express_checkout_billing_values = {
            'name': 'Express Checkout Partner',
            'email': 'express@check.out',
            'phone': '0000000000',
            'street': 'ooo',
            'street2': 'ppp',
            'city': 'ooo',
            'zip': '1200',
            'country': 'US',
            'state': 'WA',
        }
        # Ensure demo user address exists and is valid
        cls.user_demo.write({
            'street': "215 Vine St",
            'city': "Scranton",
            'zip': "18503",
            'country_id': cls.env.ref('base.us').id,
            'state_id': cls.env.ref('base.state_us_39').id,
        })

    def assertPartnerShippingValues(self, partner, shipping_values):
        for key, expected in shipping_values.items():
            if key in ('state', 'country'):
                value = partner[f'{key}_id'].code
            else:
                value = partner[key]
            self.assertEqual(value, expected, "Shipping value should match")
        if partner.state_id:
            self.assertEqual(
                partner.state_id.country_id,
                partner.country_id,
                "Partner's state should be within partner's country",
            )

    def test_express_checkout_public_user(self):
        """ Test that when using express checkout as a public user, a new partner is created. """
        session = self.authenticate(None, None)
        session['sale_order_id'] = self.sale_order.id
        root.session_store.save(session)

        self.make_jsonrpc_request(
            urls.url_join(
                self.base_url(), WebsiteSale._express_checkout_route
            ), params={
                'billing_address': dict(self.express_checkout_billing_values)
            }
        )

        new_partner = self.sale_order.partner_id
        self.assertNotEqual(new_partner, self.website.user_id.partner_id)
        self.assertPartnerShippingValues(
            new_partner,
            self.express_checkout_billing_values,
        )

    def test_express_checkout_registered_user(self):
        """ Test that when you use express checkout as a registered user and the address sent by the
            express checkout form exactly matches the one registered in orj, we do not create a new
            partner and reuse the existing one.
        """
        self.sale_order.partner_id = self.user_demo.partner_id.id
        session = self.authenticate(self.user_demo.login, self.user_demo.login)
        session['sale_order_id'] = self.sale_order.id
        root.session_store.save(session)

        self.make_jsonrpc_request(
            urls.url_join(
                self.base_url(), WebsiteSale._express_checkout_route
            ), params={
                'billing_address': {
                    'name': self.user_demo.partner_id.name,
                    'email': self.user_demo.partner_id.email,
                    'phone': self.user_demo.partner_id.phone,
                    'street': self.user_demo.partner_id.street,
                    'street2': self.user_demo.partner_id.street2,
                    'city': self.user_demo.partner_id.city,
                    'zip': self.user_demo.partner_id.zip,
                    'country': self.user_demo.partner_id.country_id.code,
                    'state': self.user_demo.partner_id.state_id.code,
                }
            }
        )

        self.assertEqual(self.sale_order.partner_id.id, self.user_demo.partner_id.id)
        self.assertEqual(self.sale_order.partner_invoice_id.id, self.user_demo.partner_id.id)

    def test_express_checkout_registered_user_existing_address(self):
        """ Test that when you use the express checkout as a registered user and the address sent by
            the express checkout form exactly matches to one of the addresses linked to this user in
            orj, we do not create a new partner and reuse the existing one.
        """
        # Create a child partner for the demo partner
        child_partner_address = dict(self.express_checkout_billing_values)
        child_partner_country = self.env['res.country'].search([
            ('code', '=', child_partner_address.pop('country')),
        ], limit=1)
        child_partner_state = self.env['res.country.state'].search([
            ('code', '=', child_partner_address.pop('state')),
            ('country_id', '=', child_partner_country.id),
        ], limit=1)
        child_partner = self.env['res.partner'].create(dict(
            **child_partner_address,
            parent_id=self.user_demo.partner_id.id,
            type='invoice',
            country_id=child_partner_country.id,
            state_id=child_partner_state.id,
        ))

        self.sale_order.partner_id = self.user_demo.partner_id.id
        session = self.authenticate(self.user_demo.login, self.user_demo.login)
        session['sale_order_id'] = self.sale_order.id
        root.session_store.save(session)

        self.make_jsonrpc_request(
            urls.url_join(
                self.base_url(), WebsiteSale._express_checkout_route
            ), params={
                'billing_address': dict(self.express_checkout_billing_values)
            }
        )

        self.assertEqual(self.sale_order.partner_id.id, self.user_demo.partner_id.id)
        self.assertEqual(self.sale_order.partner_invoice_id.id, child_partner.id)

    def test_express_checkout_registered_user_new_address(self):
        """ Test that when you use the express checkout as a registered user and the address sent by
            the express checkout form doesn't match to one of the addresses linked to this user in
            orj, we create a new partner.
        """
        self.sale_order.partner_id = self.user_demo.partner_id.id
        session = self.authenticate(self.user_demo.login, self.user_demo.login)
        session['sale_order_id'] = self.sale_order.id
        root.session_store.save(session)

        self.make_jsonrpc_request(
            urls.url_join(
                self.base_url(), WebsiteSale._express_checkout_route
            ), params={
                'billing_address': dict(self.express_checkout_billing_values)
            }
        )

        self.assertEqual(self.sale_order.partner_id.id, self.user_demo.partner_id.id)
        new_partner = self.sale_order.partner_invoice_id
        self.assertNotEqual(new_partner, self.website.user_id.partner_id)
        self.assertPartnerShippingValues(
            new_partner,
            self.express_checkout_billing_values,
        )

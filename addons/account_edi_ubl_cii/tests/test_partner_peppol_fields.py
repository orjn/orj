# -*- coding: utf-8 -*-

from contextlib import contextmanager
from unittest.mock import patch

from orj.tests import tagged
from orj.addons.account.tests.common import AccountTestInvoicingCommon
from orj.addons.account_edi_ubl_cii.models.account_edi_common import EAS_MAPPING


@tagged('post_install', '-at_install')
class TestAccountUblCii(AccountTestInvoicingCommon):

    @contextmanager
    def check_peppol_vals(self, partner, expected, reset=True):
        if reset:
            partner.write({
                'country_id': False,
                'peppol_eas': False,
                'peppol_endpoint': False,
            })
        yield
        partner.country_id = self.env.ref('base.ba')
        self.assertEqual((partner.peppol_eas, partner.peppol_endpoint), expected)

    def _build_error_peppol_endpoint(self, eas, endpoint):
        """ Mock _build_error_peppol_endpoint"""
        if eas == "0184" and endpoint != "12345674":
            return f"(0184, {endpoint}) is not a valid peppol couple."

    @patch(
        'orj.addons.account_edi_ubl_cii.models.res_partner.ResPartner._build_error_peppol_endpoint',
        _build_error_peppol_endpoint,
    )
    @patch.dict(EAS_MAPPING, {'BA': {'0184': 'company_registry', '0198': 'vat'}})
    def test_peppol_eas_endpoint(self):
        partner = self.company_data['company'].partner_id

        partner.company_registry = "12345674"
        partner.vat = "BA12345674"

        # Base case -> (0184, company_registry)
        with self.check_peppol_vals(partner, expected=("0184", partner.company_registry)):
            pass

        # No company_registry -> (0198, vat)
        with self.check_peppol_vals(partner, expected=("0198", partner.vat)):
            partner.company_registry = False

        # Invalid company_registry -> (0198, vat)
        with self.check_peppol_vals(partner, expected=("0198", partner.vat)):
            partner.company_registry = "turlututu"

        # No company_registry nor vat -> (0184, False)
        with self.check_peppol_vals(partner, expected=("0184", False)):
            partner.write({
                'company_registry': False,
                'vat': False,
            })

        # Create a partner, fill the peppol fields, then set the country
        partner_1 = self.env['res.partner'].create({
            'name': "A new partner",
            'peppol_eas': '0184',
            'peppol_endpoint': '12345674'
        })
        with self.check_peppol_vals(partner_1, expected=("0184", '12345674'), reset=False):
            pass

        # Create a partner, set the country, then fill the peppol fields
        partner_2 = self.env['res.partner'].create({
            'name': "A new partner",
            'country_id': self.env.ref('base.ba').id,
        })
        with self.check_peppol_vals(partner_2, expected=("0184", '12345674'), reset=False):
            partner_2.peppol_eas = '0184'
            partner_2.peppol_endpoint = '12345674'

        # Change the country, the EAS changes but we do not overwrite the existing endpoint
        partner_2.country_id = self.env.ref('base.be')
        self.assertEqual((partner_2.peppol_eas, partner_2.peppol_endpoint), ('0208', '12345674'))

    def test_partner_ubl_cii_formats(self):
        def _get_ubl_cii_formats_info(self):
            return {
                'ubl_no_country': {'on_peppol': True},
                'peppol': {'countries': ['NZ', 'AU'], 'on_peppol': True},
                'cii': {'countries': ['AU'], 'on_peppol': False, 'sequence': 90},
            }

        Partner = self.env['res.partner']
        partner_nz = self.env['res.partner'].create({
            'name': "NZ partner",
            'country_id': self.env.ref('base.nz').id,
        })
        partner_be = self.env['res.partner'].create({
            'name': "BE partner",
            'country_id': self.env.ref('base.be').id,
        })
        partner_au = self.env['res.partner'].create({
            'name': "AU partner",
            'country_id': self.env.ref('base.au').id,
        })
        with patch.object(self.env.registry['res.partner'], '_get_ubl_cii_formats_info', _get_ubl_cii_formats_info):
            self.assertEqual(Partner._get_ubl_cii_formats(), ['ubl_no_country', 'peppol', 'cii'])
            self.assertEqual(Partner._get_ubl_cii_formats_by_country()['NZ'], ['peppol'])
            self.assertEqual(Partner._get_ubl_cii_formats_by_country()['AU'], ['peppol', 'cii'])
            self.assertEqual(Partner._get_peppol_formats(), ['ubl_no_country', 'peppol'])
            self.assertEqual(partner_au._get_suggested_ubl_cii_edi_format(), 'cii')  # AU matches 2 formats but 'cii' has a lower sequence
            self.assertEqual(partner_nz._get_suggested_ubl_cii_edi_format(), 'peppol')
            self.assertFalse(partner_be._get_suggested_ubl_cii_edi_format())

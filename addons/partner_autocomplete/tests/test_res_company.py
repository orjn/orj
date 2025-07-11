from orj.tests import common, tagged
from orj.addons.partner_autocomplete.tests.common import MockIAPPartnerAutocomplete


@tagged('post_install', '-at_install')
class TestResCompany(common.TransactionCase, MockIAPPartnerAutocomplete):

    @classmethod
    def setUpClass(cls):
        super(TestResCompany, cls).setUpClass()
        cls._init_mock_partner_autocomplete()

    def test_enrich(self):
        company = self.env['res.company'].create({'name': "Test Company 1"})
        with self.mockPartnerAutocomplete():
            res = company._enrich()
            self.assertFalse(res)

        company.write({'email': 'friedrich@heinrich.de'})
        with self.mockPartnerAutocomplete():
            # asserts are synchronized with default mock values
            res = company._enrich()
            self.assertTrue(res)
            self.assertEqual(company.country_id, self.env.ref('base.de'))

    def test_extract_company_domain(self):
        company_1 = self.env['res.company'].create({'name': "Test Company 1"})

        company_1.website = 'http://www.info.proximus.be/faq/test'
        self.assertEqual(company_1._get_company_domain(), "proximus.be")

        company_1.email = 'info@waterlink.be'
        self.assertEqual(company_1._get_company_domain(), "waterlink.be")

        company_1.website = False
        company_1.email = False
        self.assertEqual(company_1._get_company_domain(), False)

        company_1.email = "at@"
        self.assertEqual(company_1._get_company_domain(), False)

        company_1.website = "http://superFalsyWebsiteName"
        self.assertEqual(company_1._get_company_domain(), False)

        company_1.website = "http://www.superwebsite.com"
        self.assertEqual(company_1._get_company_domain(), 'superwebsite.com')

        company_1.website = "http://superwebsite.com"
        self.assertEqual(company_1._get_company_domain(), 'superwebsite.com')

        company_1.website = "http://localhost:8069/%7Eguido/Python.html"
        self.assertEqual(company_1._get_company_domain(), False)

        company_1.website = "http://runbot.orj.net"
        self.assertEqual(company_1._get_company_domain(), 'orj.net')

        company_1.website = "http://www.example.com/biniou"
        self.assertEqual(company_1._get_company_domain(), False)

        company_1.website = "http://www.cwi.nl:80/%7Eguido/Python.html"
        self.assertEqual(company_1._get_company_domain(), "cwi.nl")

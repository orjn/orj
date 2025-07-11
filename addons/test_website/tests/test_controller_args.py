# Part of Orj. See LICENSE file for full copyright and licensing details.
import orj.tests
from orj.tools import mute_logger
from unittest.mock import patch


@orj.tests.common.tagged('post_install', '-at_install')
class TestWebsiteControllerArgs(orj.tests.HttpCase):

    @mute_logger('orj.http')
    def test_crawl_args(self):
        req = self.url_open('/ignore_args/converter/valueA/?b=valueB&c=valueC')
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'a': 'valueA', 'b': 'valueB', 'kw': {'c': 'valueC'}})

        req = self.url_open('/ignore_args/converter/valueA/nokw?b=valueB&c=valueC')
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'a': 'valueA', 'b': 'valueB'})

        req = self.url_open('/ignore_args/converteronly/valueA/?b=valueB&c=valueC')
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'a': 'valueA', 'kw': None})

        req = self.url_open('/ignore_args/none?a=valueA&b=valueB')
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'a': None, 'kw': None})

        req = self.url_open('/ignore_args/a?a=valueA&b=valueB')
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'a': 'valueA', 'kw': None})

        req = self.url_open('/ignore_args/kw?a=valueA&b=valueB')
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json(), {'a': 'valueA', 'kw': {'b': 'valueB'}})

        with patch.object(self.registry['ir.http'], '_get_error_html', lambda e, code, v: (code, '')):
            req = self.url_open('/test_website/country/whatever-999999')
            self.assertEqual(req.status_code, 404,
                             "Model converter record does not exist, return a 404.")


@orj.tests.common.tagged('post_install', '-at_install')
class TestWebsiteControllers(orj.tests.TransactionCase):

    def test_01_sitemap(self):
        website = self.env['website'].browse(1)
        locs = website.with_user(website.user_id)._enumerate_pages(query_string='test_website_sitemap')
        self.assertEqual(len(list(locs)), 1, "The same URL should only be shown once")

    def test_02_search_controller(self):
        website = self.env['website'].browse(1)
        res = website._enumerate_pages(query_string="/test_website/country/elgium")
        self.assertIn('/test_website/country/belgium', next(res).get('loc'))

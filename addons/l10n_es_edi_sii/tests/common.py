# coding: utf-8
import base64
from pytz import timezone
from datetime import datetime

from orj.tools import misc
from orj.addons.account_edi.tests.common import AccountEdiTestCommon


class TestEsEdiCommon(AccountEdiTestCommon):

    @classmethod
    @AccountEdiTestCommon.setup_edi_format('l10n_es_edi_sii.edi_es_sii')
    @AccountEdiTestCommon.setup_country('es')
    def setUpClass(cls):
        super().setUpClass()

        cls.frozen_today = datetime(year=2019, month=1, day=1, hour=0, minute=0, second=0, tzinfo=timezone('utc'))

        # Allow to see the full result of AssertionError.
        cls.maxDiff = None

        # ==== Config ====

        cls.certificate = cls.env['certificate.certificate'].create({
            'name': 'Test ES certificate',
            'content': base64.b64encode(
                misc.file_open("l10n_es_edi_sii/demo/certificates/aeat_1234.p12", 'rb').read()),
            'pkcs12_password': '1234',
            'scope': 'sii',
            'company_id': cls.company_data['company'].id,
        })

        cls.company_data['company'].write({
            'state_id': cls.env.ref('base.state_es_z').id,
            'l10n_es_sii_certificate_id': cls.certificate.id,
            'vat': 'ES59962470K',
            'l10n_es_sii_test_env': True,
            'l10n_es_sii_tax_agency': 'bizkaia',
        })

        # To be sure it is put by default on purchase journals as well (tbai module)
        cls.company_data['default_journal_purchase'].write({
            'edi_format_ids': [(6, 0, cls.edi_format.ids)],
        })
        # ==== Business ====

        cls.partner_a.write({
            'vat': 'BE0477472701',
            'country_id': cls.env.ref('base.be').id,
        })

        cls.partner_b.write({
            'vat': 'ESF35999705',
        })

        cls.product_t = cls.env["product.product"].create(
            {"name": "Test product"})
        cls.partner_t = cls.env["res.partner"].create({"name": "Test partner", "vat": "ESF35999705"})

    @classmethod
    def _get_tax_by_xml_id(cls, trailing_xml_id):
        """ Helper to retrieve a tax easily.

        :param trailing_xml_id: The trailing tax's xml id.
        :return:                An account.tax record
        """
        return cls.env.ref(f'account.{cls.env.company.id}_account_tax_template_{trailing_xml_id}')

    @classmethod
    def create_invoice(cls, **kwargs):
        return cls.env['account.move'].with_context(edi_test_mode=True).create({
            'move_type': 'out_invoice',
            'partner_id': cls.partner_a.id,
            'invoice_date': '2019-01-01',
            'date': '2019-01-01',
            **kwargs,
            'invoice_line_ids': [(0, 0, {
                'product_id': cls.product_a.id,
                'price_unit': 1000.0,
                **line_vals,
            }) for line_vals in kwargs.get('invoice_line_ids', [])],
        })

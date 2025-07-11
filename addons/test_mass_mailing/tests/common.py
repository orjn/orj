# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.addons.phone_validation.tools import phone_validation

from orj.addons.mass_mailing_sms.tests.common import MassSMSCommon


class TestMassMailCommon(MassSMSCommon):

    @classmethod
    def setUpClass(cls):
        super(TestMassMailCommon, cls).setUpClass()

        cls.test_alias = cls.env['mail.alias'].create({
            'alias_name': 'test.alias',
            'alias_model_id': cls.env['ir.model']._get('mailing.test.simple').id,
            'alias_contact': 'everyone'
        })

        # enforce last update by user_marketing to match _process_mass_mailing_queue
        # taking last writer as user running a batch
        cls.mailing_bl = cls.env['mailing.mailing'].with_user(cls.user_marketing).create({
            'name': 'SourceName',
            'subject': 'MailingSubject',
            # `+ ""` is for insuring that _prepend_preview rule out that case
            'preview': 'Hi {{ object.name + "" }} :)',
            'body_html': """<div><p>Hello <t t-out="object.name"/></p>,
<t t-set="url" t-value="'www.orj.net'"/>
<t t-set="httpurl" t-value="'https://www.orj.eu'"/>f
<span>Website0: <a id="url0" t-attf-href="https://www.orj.tz/my/{{object.name}}">https://www.orj.tz/my/<t t-out="object.name"/></a></span>
<span>Website1: <a id="url1" href="https://www.orj.be">https://www.orj.be</a></span>
<span>Website2: <a id="url2" t-attf-href="https://{{url}}">https://<t t-out="url"/></a></span>
<span>Website3: <a id="url3" t-att-href="httpurl"><t t-out="httpurl"/></a></span>
<span>External1: <a id="url4" href="https://www.example.com/foo/bar?baz=qux">Youpie</a></span>
<span>Internal1: <a id="url5" href="/event/dummy-event-0">Internal link</a></span>
<span>Internal2: <a id="url6" href="/view"/>View link</a></span>
<span>Email: <a id="url7" href="mailto:test@orj.net">test@orj.net</a></span>
<p>Stop spam ? <a id="url8" role="button" href="/unsubscribe_from_list">Ok</a></p>
</div>""",
            'mailing_type': 'mail',
            'mailing_model_id': cls.env['ir.model']._get('mailing.test.blacklist').id,
            'reply_to_mode': 'update',
        })

        cls.mailing_sms = cls.env['mailing.mailing'].with_user(cls.user_marketing).create({
            'name': 'XMas SMS',
            'subject': 'Xmas SMS for {object.name}',
            'mailing_model_id': cls.env['ir.model']._get('mail.test.sms').id,
            'mailing_type': 'sms',
            'mailing_domain': '%s' % repr([('name', 'ilike', 'MassSMSTest')]),
            'body_plaintext': 'Dear {{object.display_name}} this is a mass SMS with two links http://www.orj.net/smstest and http://www.orj.net/smstest/{{object.id}}',
            'sms_force_send': True,
            'sms_allow_unsubscribe': True,
        })

    @classmethod
    def _create_test_blacklist_records(cls, model='mailing.test.blacklist', count=1):
        """ Deprecated, remove in 14.4 """
        return cls.__create_mailing_test_records(model=model, count=count)

    @classmethod
    def _create_mailing_sms_test_records(cls, model='mail.test.sms', partners=None, count=1):
        """ Helper to create data. Currently simple, to be improved. """
        Model = cls.env[model]
        phone_field = 'phone_nbr' if 'phone_nbr' in Model else 'phone'
        partner_field = 'customer_id' if 'customer_id' in Model else 'partner_id'

        vals_list = []
        for idx in range(count):
            vals = {
                'name': 'MassSMSTestRecord_%02d' % idx,
                phone_field: '045600%02d%02d' % (idx, idx)
            }
            if partners:
                vals[partner_field] = partners[idx % len(partners)]

            vals_list.append(vals)

        return cls.env[model].create(vals_list)

    @classmethod
    def _create_mailing_test_records(cls, model='mailing.test.blacklist', partners=None, count=1):
        """ Helper to create data. Currently simple, to be improved. """
        Model = cls.env[model]
        email_field = 'email' if 'email' in Model else 'email_from'
        partner_field = 'customer_id' if 'customer_id' in Model else 'partner_id'

        vals_list = []
        for x in range(0, count):
            vals = {
                'name': 'TestRecord_%02d' % x,
                email_field: '"TestCustomer %02d" <test.record.%02d@test.example.com>' % (x, x),
            }
            if partners:
                vals[partner_field] = partners[x % len(partners)]

            vals_list.append(vals)

        return cls.env[model].create(vals_list)


class TestMassSMSCommon(TestMassMailCommon):

    @classmethod
    def setUpClass(cls):
        super(TestMassSMSCommon, cls).setUpClass()
        cls._test_body = 'Mass SMS in your face'

        records = cls.env['mail.test.sms']
        partners = cls.env['res.partner']
        country_be_id = cls.env.ref('base.be').id
        _country_us_id = cls.env.ref('base.us').id

        for x in range(10):
            partners += cls.env['res.partner'].with_context(**cls._test_context).create({
                'name': 'Partner_%s' % (x),
                'email': '_test_partner_%s@example.com' % (x),
                'country_id': country_be_id,
                'mobile': '045600%s%s99' % (x, x)
            })
            records += cls.env['mail.test.sms'].with_context(**cls._test_context).create({
                'name': 'MassSMSTest_%s' % (x),
                'customer_id': partners[x].id,
                'phone_nbr': '045600%s%s44' % (x, x)
            })
        cls.records = cls._reset_mail_context(records)
        cls.records_numbers = [phone_validation.phone_format(r.phone_nbr, 'BE', '32', force_format='E164') for r in cls.records]
        cls.partners = partners

        cls.sms_template = cls.env['sms.template'].create({
            'name': 'Test Template',
            'model_id': cls.env['ir.model']._get('mail.test.sms').id,
            'body': 'Dear {{ object.display_name }} this is a mass SMS.',
        })

        cls.partner_numbers = [
            phone_validation.phone_format(partner.mobile, partner.country_id.code, partner.country_id.phone_code, force_format='E164')
            for partner in partners
        ]

    @classmethod
    def _get_sms_test_records(cls, mobile_numbers):
        """ Helper to create data. Currently simple, to be improved. """
        country_be_id = cls.env.ref('base.be').id
        partners = cls.env['res.partner'].with_context(**cls._test_context).create([{
            'name': f'Partner_{x}',
            'email': f'_test_partner_{x}@example.com',
            'country_id': country_be_id,
            'mobile': mobile_numbers[x]
        } for x, mobile_number in enumerate(mobile_numbers)])
        records = cls.env['mail.test.sms'].with_context(**cls._test_context).create([{
            'name': f'MassSMSTest_{x}',
            'customer_id': partner.id,
            'phone_nbr': mobile_number
        } for x, (mobile_number, partner) in enumerate(zip(mobile_numbers, partners))])

        return records

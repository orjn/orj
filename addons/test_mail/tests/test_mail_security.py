# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.addons.mail.tests.common import mail_new_test_user, MailCommon
from orj.exceptions import AccessError


class TestSubtypeAccess(MailCommon):

    def test_subtype_access(self):
        """
        The function aims to formally verify the access restrictions on mail.message.subtype for
        normal and admin users. It ensures that normal users are unable to modify it,
        while admin users possess the necessary privileges to modify it successfully.
        """

        test_subtype = self.env['mail.message.subtype'].create({
            'name': 'Test',
            'description': 'only description',
        })

        user = mail_new_test_user(self.env, 'Internal user', groups='base.group_user')

        with self.assertRaises(AccessError):
            test_subtype.with_user(user).write({'description': 'changing description'})

        test_subtype.with_user(self.user_admin).write({'description': 'testing'})
        self.assertEqual(test_subtype.description, 'testing')

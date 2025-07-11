# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.tests import Form, TransactionCase


class TestResUsers(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.users = cls.env["res.users"].create([
            {'name': 'Jean', 'login': 'jean@mail.com', 'password': 'jean@mail.com'},
            {'name': 'Jean-Paul', 'login': 'jean-paul@mail.com', 'password': 'jean-paul@mail.com'},
            {'name': 'Jean-Jacques', 'login': 'jean-jacques@mail.com', 'password': 'jean-jacques@mail.com'},
            {'name': 'Georges', 'login': 'georges@mail.com', 'password': 'georges@mail.com'},
            {'name': 'Claude', 'login': 'claude@mail.com', 'password': 'claude@mail.com'},
            {'name': 'Pascal', 'login': 'pascal@mail.com', 'password': 'pascal@mail.com'},
        ])

    def test_name_search(self):
        """
        Test name search with self assign feature
        The self assign feature is present only when a limit is present,
        which is the case with the public name_search by default
        """
        ResUsers = self.env['res.users']
        jean = self.users[0]
        user_ids = [id_ for id_, __ in ResUsers.with_user(jean).name_search('')]
        self.assertEqual(jean.id, user_ids[0], "The current user, Jean, should be the first in the result.")
        user_ids = [id_ for id_, __ in ResUsers.with_user(jean).name_search('Claude')]
        self.assertNotIn(jean.id, user_ids, "The current user, Jean, should not be in the result because his name does not fit the condition.")
        pascal = self.users[-1]
        user_ids = [id_ for id_, __ in ResUsers.with_user(pascal).name_search('')]
        self.assertEqual(pascal.id, user_ids[0], "The current user, Pascal, should be the first in the result.")
        user_ids = [id_ for id_, __ in ResUsers.with_user(pascal).name_search('', limit=3)]
        self.assertEqual(pascal.id, user_ids[0], "The current user, Pascal, should be the first in the result.")
        self.assertEqual(len(user_ids), 3, "The number of results found should still respect the limit set.")
        jean_paul = self.users[1]
        user_ids = [id_ for id_, __ in ResUsers.with_user(jean_paul).name_search('Jean')]
        self.assertEqual(jean_paul.id, user_ids[0], "The current user, Jean-Paul, should be the first in the result")
        claude = self.users[4]
        user_ids = [id_ for id_, __ in ResUsers.with_user(claude).name_search('', limit=2)]
        self.assertEqual(claude.id, user_ids[0], "The current user, Claude, should be the first in the result.")
        self.assertNotEqual(claude.id, user_ids[1], "The current user, Claude, should not appear twice in the result")
        user_ids = [id_ for id_, __ in ResUsers.with_user(claude).name_search('', limit=5)]
        self.assertEqual(len(user_ids), len(set(user_ids)), "Some user(s), appear multiple times in the result")

    def test_change_password(self):
        '''
        We should be able to change user password without any issue
        '''
        user_internal = self.env['res.users'].create({
            'name': 'Internal',
            'login': 'user_internal',
            'password': 'password',
            'groups_id': [self.env.ref('base.group_user').id],
        })
        with Form(self.env['change.password.wizard'].with_context(active_model='res.users', active_ids=user_internal.ids), view='base.change_password_wizard_view') as form:
            with form.user_ids.edit(0) as line:
                line.new_passwd = 'bla'
        rec = form.save()
        rec.change_password_button()

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.tests import common


class TestWebsiteBlogCommon(common.TransactionCase):
    def setUp(self):
        super(TestWebsiteBlogCommon, self).setUp()

        Users = self.env['res.users']

        group_blog_manager_id = self.ref('website.group_website_designer')
        group_employee_id = self.ref('base.group_user')
        group_public_id = self.ref('base.group_public')

        self.user_employee = Users.with_context({'no_reset_password': True}).create({
            'name': 'Armande Employee',
            'login': 'armande',
            'email': 'armande.employee@example.com',
            'notification_type': 'inbox',
            'groups_id': [(6, 0, [group_employee_id])]
        })
        self.user_blogmanager = Users.with_context({'no_reset_password': True}).create({
            'name': 'Bastien BlogManager',
            'login': 'bastien',
            'email': 'bastien.blogmanager@example.com',
            'notification_type': 'inbox',
            'groups_id': [(6, 0, [group_blog_manager_id, group_employee_id])]
        })
        self.user_public = Users.with_context({'no_reset_password': True}).create({
            'name': 'Cedric Public',
            'login': 'cedric',
            'email': 'cedric.public@example.com',
            'notification_type': 'email',
            'groups_id': [(6, 0, [group_public_id])]
        })

        self.test_blog = self.env['blog.blog'].with_user(self.user_blogmanager).create({
            'name': 'New Blog',
        })
        self.test_blog_post = self.env['blog.post'].with_user(self.user_blogmanager).create({
            'name': 'New Post',
            'blog_id': self.test_blog.id,
            'website_published': True,
        })

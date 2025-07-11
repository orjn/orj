# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import http
from orj.http import request


class WebsiteMailGroup(http.Controller):
    @http.route('/group/is_member', type='json', auth='public', website=True)
    def group_is_member(self, group_id=0, email=None, **kw):
        """Return the email of the member if found, otherwise None."""
        group = request.env['mail.group'].browse(int(group_id)).exists()
        if not group:
            return

        token = kw.get('token')

        if token and token != group._generate_group_access_token():
            return

        if token:
            group = group.sudo()

        if not group.has_access('read'):
            return

        if not request.env.user._is_public():
            email = request.env.user.email_normalized
            partner_id = request.env.user.partner_id.id
        else:
            partner_id = None

        member = group.sudo()._find_member(email, partner_id)

        return {
            'is_member': bool(member),
            'email': member.email if member else email,
        }

# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import http
from orj.http import request


class WebsiteUrl(http.Controller):
    @http.route('/website_links/new', type='json', auth='user', methods=['POST'])
    def create_shorten_url(self, **post):
        if 'url' not in post or post['url'] == '':
            return {'error': 'empty_url'}
        return request.env['link.tracker'].search_or_create([post]).read()

    @http.route('/r', type='http', auth='user', website=True)
    def shorten_url(self, **post):
        return request.render("website_links.page_shorten_url", {
            "can_create_link_tracker": request.env['link.tracker'].has_access('create'),
            "can_create_link_tracker_code": request.env['link.tracker.code'].has_access('create'),
            **post,
        })

    @http.route('/website_links/add_code', type='json', auth='user')
    def add_code(self, **post):
        link_id = request.env['link.tracker.code'].search([('code', '=', post['init_code'])], limit=1).link_id.id
        new_code = request.env['link.tracker.code'].search_count([('code', '=', post['new_code']), ('link_id', '=', link_id)])
        if new_code > 0:
            return new_code.read()
        else:
            return request.env['link.tracker.code'].create({'code': post['new_code'], 'link_id': link_id})[0].read()

    @http.route('/website_links/recent_links', type='json', auth='user')
    def recent_links(self, **post):
        return request.env['link.tracker'].recent_links(post['filter'], post['limit'])

    @http.route('/r/<string:code>+', type='http', auth="user", website=True)
    def statistics_shorten_url(self, code, **post):
        code = request.env['link.tracker.code'].search([('code', '=', code)], limit=1)

        if code:
            return request.render("website_links.graphs", {
                "can_create_link_tracker_code": request.env['link.tracker.code'].has_access('create'),
                **code.link_id.read()[0]
            })
        else:
            return request.redirect('/', code=301)

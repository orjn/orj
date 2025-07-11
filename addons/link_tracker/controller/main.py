# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from werkzeug.exceptions import NotFound

from orj import http
from orj.http import request


class LinkTracker(http.Controller):

    @http.route('/r/<string:code>', type='http', auth='public', website=True)
    def full_url_redirect(self, code, **post):
        if not request.env['ir.http'].is_a_bot():
            request.env['link.tracker.click'].sudo().add_click(
                code,
                ip=request.httprequest.remote_addr,
                country_code=request.geoip.country_code,
            )
        redirect_url = request.env['link.tracker'].get_url_from_code(code)
        if not redirect_url:
            raise NotFound()
        return request.redirect(redirect_url, code=301, local=False)

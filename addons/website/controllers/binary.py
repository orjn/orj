from orj import http
from orj.http import request
from orj.addons.web.controllers.binary import Binary


class WebsiteBinary(Binary):
    @http.route([
        '/web/assets/<int:website_id>/<unique>/<string:filename>'], type='http', auth="public", readonly=True)
    def content_assets_website(self, website_id=None, **kwargs):
        if not request.env['website'].browse(website_id).exists():
            raise request.not_found()
        return super().content_assets(**kwargs, assets_params={'website_id': website_id})

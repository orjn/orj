# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, models, fields
from orj.tools.translate import html_translate


class ImLivechatChannel(models.Model):

    _name = 'im_livechat.channel'
    _inherit = ['im_livechat.channel', 'website.published.mixin']

    def _compute_website_url(self):
        super(ImLivechatChannel, self)._compute_website_url()
        for channel in self:
            channel.website_url = "/livechat/channel/%s" % (self.env['ir.http']._slug(channel),)

    website_description = fields.Html(
        "Website description", default=False, translate=html_translate,
        sanitize_overridable=True,
        sanitize_attributes=False, sanitize_form=False,
        help="Description of the channel displayed on the website page")

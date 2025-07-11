# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import http
from orj.http import request
from orj.addons.mail.models.discuss.mail_guest import add_guest_to_context


class LinkPreviewController(http.Controller):
    @http.route("/mail/link_preview", methods=["POST"], type="json", auth="public")
    @add_guest_to_context
    def mail_link_preview(self, message_id):
        if not request.env["mail.link.preview"]._is_link_preview_enabled():
            return
        guest = request.env["mail.guest"]._get_guest_from_context()
        message = guest.env["mail.message"].search([("id", "=", int(message_id))])
        if not message:
            return
        if not message.is_current_user_or_guest_author and not guest.env.user._is_admin():
            return
        guest.env["mail.link.preview"].sudo()._create_from_message_and_notify(
            message, request_url=request.httprequest.url_root
        )

    @http.route("/mail/link_preview/hide", methods=["POST"], type="json", auth="public")
    @add_guest_to_context
    def mail_link_preview_hide(self, link_preview_ids):
        guest = request.env["mail.guest"]._get_guest_from_context()
        link_preview_sudo = guest.env["mail.link.preview"].sudo().search([("id", "in", link_preview_ids)])
        if not link_preview_sudo:
            return
        if not link_preview_sudo.message_id.is_current_user_or_guest_author and not guest.env.user._is_admin():
            return
        link_preview_sudo._hide_and_notify()

# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.http import request
from orj.addons.mail.controllers.thread import ThreadController


class DiscussThreadController(ThreadController):
    def _filter_message_post_partners(self, thread, partners):
        if thread._name == "discuss.channel":
            domain = [("channel_id", "=", thread.id), ("partner_id", "in", partners.ids)]
            # sudo: discuss.channel.member - filtering partners that are members is acceptable
            return request.env["discuss.channel.member"].sudo().search(domain).partner_id
        return super()._filter_message_post_partners(thread, partners)

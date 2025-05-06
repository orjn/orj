# Part of Orj. See LICENSE file for full copyright and licensing details.

from markupsafe import Markup

from orj import models, fields, _

class Users(models.Model):
    _inherit = 'res.users'

    orjbot_state = fields.Selection(
        [
            ('not_initialized', 'Not initialized'),
            ('onboarding_emoji', 'Onboarding emoji'),
            ('onboarding_attachement', 'Onboarding attachment'),
            ('onboarding_command', 'Onboarding command'),
            ('onboarding_ping', 'Onboarding ping'),
            ('onboarding_canned', 'Onboarding canned'),
            ('idle', 'Idle'),
            ('disabled', 'Disabled'),
        ], string="OrjBot Status", readonly=True, required=False)  # keep track of the state: correspond to the code of the last message sent
    orjbot_failed = fields.Boolean(readonly=True)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['orjbot_state']

    def _on_webclient_bootstrap(self):
        super()._on_webclient_bootstrap()
        if self._is_internal() and self.orjbot_state in [False, "not_initialized"]:
            self._init_orjbot()

    def _init_orjbot(self):
        self.ensure_one()
        orjbot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
        channel = self.env['discuss.channel'].channel_get([orjbot_id, self.partner_id.id])
        message = Markup("%s<br/>%s<br/><b>%s</b> <span class=\"o_orjbot_command\">:)</span>") % (
            _("Hello,"),
            _("Orj's chat helps employees collaborate efficiently. I'm here to help you discover its features."),
            _("Try to send me an emoji")
        )
        channel.sudo().message_post(
            author_id=orjbot_id,
            body=message,
            message_type="comment",
            silent=True,
            subtype_xmlid="mail.mt_comment",
        )
        self.sudo().orjbot_state = 'onboarding_emoji'
        return channel

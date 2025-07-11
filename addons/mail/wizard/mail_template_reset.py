# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models, _


class MailTemplateReset(models.TransientModel):
    _name = 'mail.template.reset'
    _description = 'Mail Template Reset'

    template_ids = fields.Many2many('mail.template')

    def reset_template(self):
        if not self.template_ids:
            return False
        self.template_ids.reset_template()
        if self.env.context.get('params', {}).get('view_type') == 'list':
            next_action = {'type': 'ir.actions.client', 'tag': 'reload'}
        else:
            next_action = {'type': 'ir.actions.act_window_close'}
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _('The email template(s) have been restored to their original settings.'),
                'next': next_action,
            }
        }

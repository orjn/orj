# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, fields, models, _


class SMSTemplate(models.Model):
    "Templates for sending SMS"
    _name = "sms.template"
    _inherit = ['mail.render.mixin', 'template.reset.mixin']
    _description = 'SMS Templates'

    _unrestricted_rendering = True

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'model_id' in fields and not res.get('model_id') and res.get('model'):
            res['model_id'] = self.env['ir.model']._get(res['model']).id
        return res

    name = fields.Char('Name', translate=True)
    model_id = fields.Many2one(
        'ir.model', string='Applies to', required=True,
        domain=['&', ('is_mail_thread_sms', '=', True), ('transient', '=', False)],
        help="The type of document this template can be used with", ondelete='cascade')
    model = fields.Char('Related Document Model', related='model_id.model', index=True, store=True, readonly=True)
    body = fields.Char('Body', translate=True, required=True)
    # Use to create contextual action (same as for email template)
    sidebar_action_id = fields.Many2one('ir.actions.act_window', 'Sidebar action', readonly=True, copy=False,
                                        help="Sidebar action to make this template available on records "
                                        "of the related document model")

    # Overrides of mail.render.mixin
    @api.depends('model')
    def _compute_render_model(self):
        for template in self:
            template.render_model = template.model

    # ------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------

    def copy_data(self, default=None):
        vals_list = super().copy_data(default=default)
        return [dict(vals, name=self.env._("%s (copy)", template.name)) for template, vals in zip(self, vals_list)]

    def unlink(self):
        self.sudo().mapped('sidebar_action_id').unlink()
        return super(SMSTemplate, self).unlink()

    def action_create_sidebar_action(self):
        ActWindow = self.env['ir.actions.act_window']
        view = self.env.ref('sms.sms_composer_view_form')

        for template in self:
            button_name = _('Send SMS (%s)', template.name)
            action = ActWindow.create({
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'sms.composer',
                # Add default_composition_mode to guess to determine if need to use mass or comment composer
                'context': "{'default_template_id' : %d, 'sms_composition_mode': 'guess', 'default_res_ids': active_ids, 'default_res_id': active_id}" % (template.id),
                'view_mode': 'form',
                'view_id': view.id,
                'target': 'new',
                'binding_model_id': template.model_id.id,
            })
            template.write({'sidebar_action_id': action.id})
        return True

    def action_unlink_sidebar_action(self):
        for template in self:
            if template.sidebar_action_id:
                template.sidebar_action_id.unlink()
        return True

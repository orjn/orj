# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models, _
from orj.exceptions import UserError


class StockPickingToBatch(models.TransientModel):
    _name = 'stock.picking.to.batch'
    _description = 'Batch Transfer Lines'

    batch_id = fields.Many2one('stock.picking.batch', string='Batch Transfer', domain="[('is_wave', '=', False), ('state', 'in', ('draft', 'in_progress'))]")
    mode = fields.Selection([('existing', 'an existing batch transfer'), ('new', 'a new batch transfer')], default='new')
    user_id = fields.Many2one('res.users', string='Responsible')
    is_create_draft = fields.Boolean(string="Draft", help='When checked, create the batch in draft status')
    description = fields.Char('Description')

    def attach_pickings(self):
        self.ensure_one()
        pickings = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        if self.mode == 'new':
            company = pickings.company_id
            if len(company) > 1:
                raise UserError(_("The selected pickings should belong to an unique company."))
            batch = self.env['stock.picking.batch'].create({
                'user_id': self.user_id.id,
                'company_id': company.id,
                'picking_type_id': pickings[0].picking_type_id.id,
                'description': self.description,
            })
        else:
            batch = self.batch_id

        pickings.write({'batch_id': batch.id})
        # you have to set some pickings to batch before confirm it.
        if self.mode == 'new' and not self.is_create_draft:
            batch.action_confirm()
        return {
            'name': _('Batch Transfer'),
            'view_mode': 'form',
            'res_model': 'stock.picking.batch',
            'type': 'ir.actions.act_window',
            'res_id': batch.id,
        }

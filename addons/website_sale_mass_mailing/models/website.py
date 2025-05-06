# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class Website(models.Model):
    _inherit = 'website'

    newsletter_id = fields.Many2one(string="Newsletter List", comodel_name='mailing.list')

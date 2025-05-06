# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    gelato_api_key = fields.Char(string="Gelato API Key")
    gelato_webhook_secret = fields.Char(string="Gelato Webhook Secret")

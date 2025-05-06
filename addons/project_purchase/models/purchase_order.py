# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one('project.project')

# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one('project.project')

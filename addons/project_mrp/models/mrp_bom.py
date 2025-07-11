# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    project_id = fields.Many2one('project.project')

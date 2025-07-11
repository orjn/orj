# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import api, models, fields

class goal_manual_wizard(models.TransientModel):
    """Wizard to update a manual goal"""
    _name = 'gamification.goal.wizard'
    _description = 'Gamification Goal Wizard'

    goal_id = fields.Many2one("gamification.goal", string='Goal', required=True)
    current = fields.Float('Current')

    def action_update_current(self):
        """Wizard action for updating the current value"""
        for wiz in self:
            wiz.goal_id.write({
                'current': wiz.current,
                'goal_id': wiz.goal_id.id,
                'to_update': False,
            })
            wiz.goal_id.update_goal()

        return False

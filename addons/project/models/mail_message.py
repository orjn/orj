# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models
from orj.tools.sql import create_index


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def init(self):
        super().init()
        create_index(
            self._cr,
            'mail_message_date_res_id_id_for_burndown_chart',
            self._table,
            ['date', 'res_id', 'id'],
            where="model='project.task' AND message_type='notification'"
        )

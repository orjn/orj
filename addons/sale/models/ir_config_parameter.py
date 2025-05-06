# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models, api
from orj.tools.misc import str2bool


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    def _sale_sync_cron(self, unlink=False):
        for config in self:
            if (
                config.key == 'sale.automatic_invoice'
                and (send_invoice_cron := self.env.ref('sale.send_invoice_cron', raise_if_not_found=False))
            ):
                send_invoice_cron.active = False if unlink else str2bool(config.value)

    @api.model_create_multi
    def create(self, vals_list):
        configs = super().create(vals_list)
        configs._sale_sync_cron()
        return configs

    def write(self, vals):
        res = super().write(vals)
        self._sale_sync_cron()
        return res

    def unlink(self):
        self._sale_sync_cron(unlink=True)
        return super().unlink()

# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj import models
from orj.osv import expression


class ProductReplenishMixin(models.AbstractModel):
    _inherit = 'stock.replenish.mixin'

    def _get_allowed_route_domain(self):
        domains = super()._get_allowed_route_domain()
        return expression.AND([domains, [('id', '!=', self.env.ref('stock_dropshipping.route_drop_shipping', raise_if_not_found=False).id)]])

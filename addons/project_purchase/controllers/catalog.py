# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.http import request, route
from orj.addons.product.controllers.catalog import ProductCatalogController


class ProjectPurchaseCatalogController(ProductCatalogController):

    @route()
    def product_catalog_update_order_line_info(self, res_model, order_id, product_id, quantity=0, **kwargs):
        """ Override to update context with project_id.

        :param string res_model: The order model.
        :param int order_id: The order id.
        :param int product_id: The product, as a `product.product` id.
        :return: The unit price price of the product, based on the pricelist of the order and
                 the quantity selected.
        :rtype: float
        """
        if (project_id := kwargs.get('project_id')):
            request.update_context(project_id=project_id)
        return super().product_catalog_update_order_line_info(res_model, order_id, product_id, quantity, **kwargs)

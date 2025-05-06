# Part of Orj. See LICENSE file for full copyright and licensing details.

from orj.fields import Command
from orj.tests import tagged

from orj.addons.website_sale_collect.tests.common import ClickAndCollectCommon


@tagged('post_install', '-at_install')
class TestWebsite(ClickAndCollectCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse_2 = cls._create_warehouse()

    def test_product_available_qty_if_in_store_dm_published(self):
        self.website.warehouse_id = self.warehouse_2
        free_qty = self.website._get_product_available_qty(self.storable_product)
        self.assertEqual(free_qty, 10)

    def test_product_available_qty_if_in_store_dm_unpublished(self):
        self.in_store_dm.is_published = False
        self.website.warehouse_id = self.warehouse_2
        free_qty = self.website._get_product_available_qty(self.storable_product)
        self.assertEqual(free_qty, 0)

    def test_in_store_product_available_qty_for_order(self):
        self.in_store_dm.warehouse_ids = [Command.link(self.warehouse_2.id)]
        self._add_product_qty_to_wh(self.storable_product.id, 15, self.warehouse_2.lot_stock_id.id)
        free_qty = self.website._get_max_in_store_product_available_qty(self.storable_product)
        self.assertEqual(free_qty, 15)

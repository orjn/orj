from freezegun import freeze_time

from orj import _
from orj.fields import Command
from orj.tests import tagged

from orj.addons.l10n_in.tests.common import L10nInTestInvoicingCommon


@tagged('post_install', '-at_install', 'post_install_l10n')
class TestStockEwaybill(L10nInTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env.user.groups_id += cls.env.ref('stock.group_stock_manager')
        cls.product_a.standard_price = 500.00
        cls.partner_a.write({
            'vat': '27DJMPM8965E1ZE',
            'l10n_in_gst_treatment': 'regular',
            'state_id': cls.state_in_mh.id,
            'zip': '431122'
        })

    def _create_stock_picking(self):
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)])
        delivery_picking = self.env['stock.picking'].create({
            'partner_id': self.partner_a.id,
            'picking_type_id': warehouse.out_type_id.id,
            'move_ids': [Command.create({
                'name': self.product_a.name,
                'product_id': self.product_a.id,
                'product_uom_qty': 5,
                'quantity': 5,
                'location_id': self.env.ref('stock.stock_location_customers').id,
                'location_dest_id': warehouse.lot_stock_id.id,
            })]
        })
        delivery_picking.button_validate()
        return delivery_picking

    @freeze_time('2024-04-26')
    def test_ewaybill_stock(self):
        delivery_picking = self._create_stock_picking()
        ewaybill = self.env['l10n.in.ewaybill'].create({
            'picking_id': delivery_picking.id,
            'mode': False,
            'type_id': self.env.ref('l10n_in_ewaybill_stock.type_delivery_challan_sub_line_sales').id,
        })
        self.assertRecordValues(ewaybill, [{
            'state': 'pending',
            'display_name': _('Pending'),
            'fiscal_position_id': self.fp_in_inter_state.id,
        }])
        ewaybill.fiscal_position_id = self.fp_in_inter_state
        self.assertEqual(ewaybill.move_ids[0].ewaybill_tax_ids, self.igst_sale_5)
        expected_json = {
            'supplyType': 'O',
            'subSupplyType': '10',
            'docType': 'CHL',
            'transactionType': 1,
            'transDistance': '0',
            'docNo': 'compa/OUT/00001',
            'docDate': '26/04/2024',
            'fromGstin': '24AAGCC7144L6ZE',
            'toGstin': '27DJMPM8965E1ZE',
            'fromTrdName': 'Default Company',
            'toTrdName': 'Partner Intra State',
            'fromStateCode': 24,
            'toStateCode': 27,
            'fromAddr1': 'Khodiyar Chowk',
            'toAddr1': 'Karansinhji Rd',
            'fromAddr2': 'Sala Number 3',
            'toAddr2': 'Karanpara',
            'fromPlace': 'Amreli',
            'toPlace': 'Rajkot',
            'fromPincode': 365220,
            'toPincode': 431122,
            'actToStateCode': 27,
            'actFromStateCode': 24,
            'itemList': [{
                'productName': 'product_a',
                'hsnCode': '111111',
                'productDesc': 'product_a',
                'quantity': 5.0,
                'qtyUnit': 'UNT',
                'taxableAmount': 2500.0,
                'igstRate': 5.0,
            }],
            'totalValue': 2500.0,
            'cgstValue': 0.0,
            'sgstValue': 0.0,
            'igstValue': 125.0,
            'cessValue': 0.0,
            'cessNonAdvolValue': 0.0,
            'otherValue': 0.0,
            'totInvValue': 2625.0
        }
        self.assertDictEqual(ewaybill._ewaybill_generate_direct_json(), expected_json)

    @freeze_time('2024-04-26')
    def test_ewaybill_stock_test_2(self):
        """
        Ewaybill challan type other test with description
        """
        delivery_picking = self._create_stock_picking()
        ewaybill = self.env['l10n.in.ewaybill'].create({
            'picking_id': delivery_picking.id,
            'transporter_id': self.partner_a.id,
            'mode': False,
            'type_id': self.env.ref('l10n_in_ewaybill_stock.type_delivery_challan_sub_others').id,
            'type_description': "Other reasons"
        })
        expected_json = {
          'supplyType': 'O',
          'subSupplyType': '8',
          'subSupplyDesc': 'Other reasons',
          'docType': 'CHL',
          'transactionType': 1,
          'transDistance': '0',
          'docNo': 'compa/OUT/00002',
          'docDate': '26/04/2024',
          'fromGstin': '24AAGCC7144L6ZE',
          'toGstin': '27DJMPM8965E1ZE',
          'fromTrdName': 'Default Company',
          'toTrdName': 'Partner Intra State',
          'fromStateCode': 24,
          'toStateCode': 27,
          'fromAddr1': 'Khodiyar Chowk',
          'toAddr1': 'Karansinhji Rd',
          'fromAddr2': 'Sala Number 3',
          'toAddr2': 'Karanpara',
          'fromPlace': 'Amreli',
          'toPlace': 'Rajkot',
          'fromPincode': 365220,
          'toPincode': 431122,
          'actToStateCode': 27,
          'actFromStateCode': 24,
          'transporterId': '27DJMPM8965E1ZE',
          'transporterName': 'Partner Intra State',
          'itemList': [
            {
              'productName': 'product_a',
              'hsnCode': '111111',
              'productDesc': 'product_a',
              'quantity': 5.0,
              'qtyUnit': 'UNT',
              'taxableAmount': 2500.0,
              'igstRate': 5.0
            }
          ],
          'totalValue': 2500.0,
          'cgstValue': 0.0,
          'sgstValue': 0.0,
          'igstValue': 125.0,
          'cessValue': 0.0,
          'cessNonAdvolValue': 0.0,
          'otherValue': 0.0,
          'totInvValue': 2625.0
        }
        self.assertDictEqual(ewaybill._ewaybill_generate_direct_json(), expected_json)

    @freeze_time('2024-04-26')
    def test_ewaybill_stock_test_3(self):
        """
        Ewaybill Zero distance test
        """
        delivery_picking = self._create_stock_picking()
        ewaybill = self.env['l10n.in.ewaybill'].create({
            'type_id': self.env.ref('l10n_in_ewaybill_stock.type_delivery_challan_sub_others').id,
            'type_description': "Other reasons",
            'picking_id': delivery_picking.id,
            'transporter_id': self.partner_a.id,
            'mode': '2',
            'distance': 0,
            'transportation_doc_no': 123456789,
            'transportation_doc_date': '2024-04-26'
        })

        # Sub-test: Extract `Distance` when multiple alerts in response
        with self.subTest(scenario="Extract distance when multiple alerts in response"):
            expected_distance = 118
            response = {
                'status_cd': '1',
                'status_desc': 'EWAYBILL request succeeds',
                'data': {
                    'ewayBillNo': 123456789012,
                    'ewayBillDate': '26/02/2024 12:09:43 PM',
                    'validUpto': '27/02/2024 12:09:43 PM',
                    'alert': ', Distance between these two pincodes is 118, '
                }
            }
            ewaybill._l10n_in_ewaybill_stock_handle_zero_distance_alert_if_present(response)
            self.assertEqual(ewaybill.distance, expected_distance)

        # Sub-test: Extract `Distance` when single alert in response
        with self.subTest(scenario="Extract distance when single alert in response"):
            ewaybill.distance = 0
            expected_distance = 222
            response = {
                'status_cd': '1',
                'status_desc': 'EWAYBILL request succeeds',
                'data': {
                    'ewayBillNo': 987654321012,
                    'ewayBillDate': '08/04/2025 11:04:04 AM',
                    'validUpto': '09/04/2025 11:04:04 AM',
                    'alert': 'Distance between these two pincodes is 222'
                }
            }
            ewaybill._l10n_in_ewaybill_stock_handle_zero_distance_alert_if_present(response)
            self.assertEqual(ewaybill.distance, expected_distance)

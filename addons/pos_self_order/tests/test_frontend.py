# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

import json
from uuid import uuid4

import orj.tests
from orj.addons.pos_self_order.tests.self_order_common_test import SelfOrderCommonTest
from orj import Command


@orj.tests.tagged("post_install", "-at_install")
class TestFrontendMobile(SelfOrderCommonTest):
    def test_order_fiscal_position(self):
        """ Orders made in take away should have the alternative fiscal position. """

        tax30 = self.env['account.tax'].create({
            'name': '30%',
            'amount': 30,
            'amount_type': 'percent',
        })

        alternative_fp = self.env['account.fiscal.position'].create({
            'name': "Test",
            'auto_apply': True,
            'tax_ids': [
                Command.create({
                    'tax_src_id': self.default_tax15.id,
                    'tax_dest_id': tax30.id,
                }),
            ]
        })

        self.pos_config.write({
            'self_ordering_mode': 'kiosk',
            'takeaway': True,
            'self_ordering_takeaway': True,
            'takeaway_fp_id': alternative_fp.id,
        })

        self.pos_config.open_ui()
        self.pos_config.current_session_id.set_opening_control(0, "")

        response = self.url_open(
            "/pos-self-order/process-order/kiosk",
            data=json.dumps({
                "jsonrpc": "2.0",
                "method": "call",
                "id": str(uuid4()),
                "params": {
                    "access_token": self.pos_config.access_token,
                    "order": {
                        "id": None,
                        "config_id": self.pos_config.id,
                        "session_id": self.pos_config.current_session_id.id,
                        "access_token": None,
                        "pos_reference": None,
                        "state": "draft",
                        "amount_total": 0,
                        "amount_tax": 0,
                        "amount_paid": 0,
                        "amount_return": 0,
                        "lines": [],
                        "tracking_number": None,
                        "takeaway": True,
                        "uuid": str(uuid4()),
                    },
                    "table_identifier": None,
                }
            }),
            headers={"Content-Type": "application/json"},
        )

        result = response.json()
        order_id = result['result']['pos.order'][0]['id']
        self.assertEqual(self.env['pos.order'].browse(order_id).fiscal_position_id.id, alternative_fp.id)

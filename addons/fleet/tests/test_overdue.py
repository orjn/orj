# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.
from orj.tests import common, new_test_user
from orj import fields


class TestFleet(common.TransactionCase):

    def test_search_renewal(self):
        """
            Should find the car with overdue contract or renewal due soon
        """
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        brand = self.env["fleet.vehicle.model.brand"].create({
            "name": "Audi",
        })
        model = self.env["fleet.vehicle.model"].create({
            "brand_id": brand.id,
            "name": "A3",
        })
        car_1 = self.env["fleet.vehicle"].create({
            "model_id": model.id,
            "driver_id": user.partner_id.id,
            "plan_to_change_car": False
        })

        car_2 = self.env["fleet.vehicle"].create({
            "model_id": model.id,
            "driver_id": user.partner_id.id,
            "plan_to_change_car": False
        })
        Log = self.env['fleet.vehicle.log.contract']
        Log.create({
            'vehicle_id': car_2.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=10)
        })
        res = self.env["fleet.vehicle"].search([('contract_renewal_due_soon', '=', True), ('id', '=', car_2.id)])
        self.assertEqual(res, car_2)

        Log.create({
            'vehicle_id': car_1.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=-10)
        })
        res = self.env["fleet.vehicle"].search([('contract_renewal_overdue', '=', True), ('id', '=', car_1.id)])
        self.assertEqual(res, car_1)

    def test_exclude_resolved_vehicles_from_overdue(self):
        """
            if there is an expired contract for the car, but it also has an open contract
            it should not be considered overdue
        """
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        brand = self.env["fleet.vehicle.model.brand"].create({
            "name": "Audi",
        })
        model = self.env["fleet.vehicle.model"].create({
            "brand_id": brand.id,
            "name": "A3",
        })
        car_1 = self.env["fleet.vehicle"].create({
            "model_id": model.id,
            "driver_id": user.partner_id.id,
            "plan_to_change_car": False
        })

        Log = self.env['fleet.vehicle.log.contract']
        Log.create({
            'vehicle_id': car_1.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=-2)
        })
        Log.create({
            'vehicle_id': car_1.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=365)
        })

        res = self.env["fleet.vehicle"].search([('contract_renewal_overdue', '=', True), ('id', '=', car_1.id)])
        self.assertFalse(res)

from orj.tests import common

class TestActionBindings(common.TransactionCase):

    def test_bindings(self):
        """ check the action bindings on models """
        Actions = self.env['ir.actions.actions']

        # first make sure there is no bound action
        self.env.ref('base.action_partner_merge').unlink()
        bindings = Actions.get_bindings('res.partner')
        self.assertFalse(bindings.get('action'))
        self.assertFalse(bindings.get('report'))

        # create action bindings, and check the returned bindings
        action1 = self.env.ref('base.action_attachment')
        action2 = self.env.ref('base.ir_default_menu_action')
        action3 = self.env['ir.actions.report'].search([('groups_id', '=', False)], limit=1)
        action1.binding_model_id = action2.binding_model_id \
                                 = action3.binding_model_id \
                                 = self.env['ir.model']._get('res.partner')

        bindings = Actions.get_bindings('res.partner')
        self.assertItemsEqual(
            bindings['action'],
            (action1 + action2).read(['name', 'binding_view_types']),
            "Wrong action bindings",
        )
        self.assertItemsEqual(
            bindings['report'],
            action3.read(['name', 'binding_view_types']),
            "Wrong action bindings",
        )

        # add a group on an action, and check that it is not returned
        group = self.env.ref('base.group_system')
        action2.groups_id += group
        self.env.user.groups_id -= group

        bindings = Actions.get_bindings('res.partner')
        self.assertItemsEqual(
            bindings['action'],
            action1.read(['name', 'binding_view_types']),
            "Wrong action bindings",
        )
        self.assertItemsEqual(
            bindings['report'],
            action3.read(['name', 'binding_view_types']),
            "Wrong action bindings",
        )

class TestBindingViewFilters(common.TransactionCase):
    def test_act_window(self):
        A = self.env['tab.a']

        form_act = A.get_views([(False, 'form')], {'toolbar': True})['views']['form']['toolbar']['action']
        self.assertEqual(
            [a['name'] for a in form_act],
            ['Action 1', 'Action 2', 'Action 3'],
            "forms should have all actions")

        list_act = A.get_views([(False, 'list')], {'toolbar': True})['views']['list']['toolbar']['action']
        self.assertEqual(
            [a['name'] for a in list_act],
            ['Action 1', 'Action 3'],
            "lists should not have the form-only action")

        kanban_act = A.get_views([(False, 'kanban')], {'toolbar': True})['views']['kanban']['toolbar']['action']
        self.assertEqual(
            [a['name'] for a in kanban_act],
            ['Action 1'],
            "kanban should only have the universal action")

    def test_act_record(self):
        B = self.env['tab.b']

        form_act = B.get_views([(False, 'form')], {'toolbar': True})['views']['form']['toolbar']['action']
        self.assertEqual(
            [a['name'] for a in form_act],
            ['Record 1', 'Record 2', 'Record 3'],
            "forms should have all actions")

        list_act = B.get_views([(False, 'list')], {'toolbar': True})['views']['list']['toolbar']['action']
        self.assertEqual(
            [a['name'] for a in list_act],
            ['Record 1', 'Record 3'],
            "lists should not have the form-only action")

        kanban_act = B.get_views([(False, 'kanban')], {'toolbar': True})['views']['kanban']['toolbar']['action']
        self.assertEqual(
            [a['name'] for a in kanban_act],
            ['Record 1'],
            "kanban should only have the universal action")

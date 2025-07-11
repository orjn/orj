/* @orj-module */

import { startServer } from "@bus/../tests/helpers/mock_python_environment";
import { addModelNamesToFetch } from "@bus/../tests/helpers/model_definitions_helpers";

import { openFormView, start } from "@mail/../tests/helpers/test_utils";

import {
    editInput,
    click,
    getFixture,
    clickOpenedDropdownItem,
    clickDropdown,
} from "@web/../tests/helpers/utils";
import { setupViewRegistries } from "@web/../tests/views/helpers";

addModelNamesToFetch(["project.project", "project.task"]);

let target;

QUnit.module('Subtask Kanban List tests', {
    beforeEach: async function () {
        const pyEnv = await startServer();
        const projectId = pyEnv['project.project'].create([
            { name: "Project One" },
        ]);
        const projectId2 = pyEnv['project.project'].create([
            { name: "Project Two" },
        ]);
        const userId = pyEnv['res.users'].create([
            { name: "User One", login: 'one', password: 'one' },
        ]);
        pyEnv['project.task'].create([
            { name: 'task one', project_id: projectId, closed_subtask_count: 1, subtask_count: 4, child_ids: [2, 3, 4, 7], state: '01_in_progress', user_ids: [userId] },
            { name: 'task two', parent_id: 1, closed_subtask_count: 0, subtask_count: 0, child_ids: [], state: '03_approved' },
            { name: 'task three', parent_id: 1, closed_subtask_count: 0, subtask_count: 0, child_ids: [], state: '02_changes_requested' },
            { name: 'task four', parent_id: 1, closed_subtask_count: 0, subtask_count: 0, child_ids: [], state: '1_done' },
            { name: 'task five', closed_subtask_count: 0, subtask_count: 1, child_ids: [6], state: '03_approved' },
            { name: 'task six', parent_id: 5, closed_subtask_count: 0, subtask_count: 0, child_ids: [], state: '1_canceled' },
            { name: 'task seven', parent_id: 1, closed_subtask_count: 0, subtask_count: 0, child_ids: [], state: '01_in_progress', user_ids: [userId] },
        ]);
        this.task = pyEnv['project.task'].create([
            { name: "task's Project Two", project_id: projectId2, child_ids: [] }
        ]);
        this.views = {
            "project.task,false,kanban":
                `<kanban js_class="project_task_kanban">
                    <field name="subtask_count"/>
                    <field name="project_id"/>
                    <field name="user_ids"/>
                    <field name="state"/>
                    <templates>
                        <t t-name="card">
                            <field name="display_name" widget="name_with_subtask_count"/>
                            <t t-if="record.project_id.raw_value and record.subtask_count.raw_value">
                                <widget name="subtask_counter"/>
                            </t>
                            <widget name="subtask_kanban_list" />
                        </t>
                    </templates>
                </kanban>`,
            "project.task,false,form":
                `<form>
                    <field name="child_ids" widget="subtasks_one2many">
                        <list editable="bottom">
                            <field name="display_in_project" force_save="1"/>
                            <field name="project_id" widget="project"/>
                            <field name="name"/>
                        </list>
                    </field>
                </form>`
        };
        target = getFixture();
        setupViewRegistries();
    }
}, function () {
    QUnit.test("Check whether subtask list functionality works as intended", async function (assert) {
        assert.expect(9);

        const views = this.views;
        const { openView } = await start({ serverData: { views } });
        await openView({
            res_model: "project.task",
            views: [[false, "kanban"]],
        });

        assert.containsOnce(target, '.o_field_name_with_subtask_count:contains("(1/4 sub-tasks)")', "Task title should also display the number of (closed) sub-tasks linked to the task");
        assert.containsOnce(target, '.subtask_list_button', "Only kanban boxes of parent tasks having open subtasks should have the drawdown button, in this case this is 1");
        assert.containsNone(target, '.subtask_list', "If the drawdown button is not clicked, the subtasks list should be hidden");

        await click(target, '.subtask_list_button');

        assert.containsOnce(target, '.subtask_list', "Clicking on the button should make the subtask list render, in this case we are expectig 1 list");
        assert.containsN(target, '.subtask_list_row', 3, "The list rendered should show the open subtasks of the task, in this case 3");
        assert.containsN(target, '.subtask_state_widget_col', 3, "Each of the list's rows should have 1 state widget, thus we are looking for 3 in total");
        assert.containsN(target, '.subtask_user_widget_col', 3, "Each of the list's rows should have 1 user widgets, thus we are looking for 3 in total");
        assert.containsN(target, '.subtask_name_col', 3, "Each of the list's rows should display the subtask's name, thus we are looking for 3 in total");

        await click(target, '.subtask_list_button');

        assert.containsNone(target, '.subtask_list', "If the drawdown button is clicked again, the subtasks list should be hidden again");
    });

    QUnit.test("Update closed subtask count in the kanban card when the state of a subtask is set to Done.", async function (assert) {
        let checkSteps = false;
        const { openView } = await start({
            serverData: { views: this.views },
            mockRPC(route, { model, method }) {
                if (checkSteps) {
                    assert.step(`${model}/${method}`);
                }
            },
        });
        await openView({
            res_model: "project.task",
            views: [[false, "kanban"]],
        });

        assert.strictEqual(target.querySelector(".subtask_list_button").parentElement.textContent, "1/4");
        checkSteps = true;
        await click(target, '.subtask_list_button');
        const subtaskEl = target.querySelector(".subtask_list");
        assert.containsOnce(subtaskEl, ".o_field_widget.o_field_project_task_state_selection.subtask_state_widget_col .o_status:not(.o_status_green,.o_status_bubble)", "The state of the subtask should be in progress");
        await click(subtaskEl, ".o_field_widget.o_field_project_task_state_selection.subtask_state_widget_col .o_status:not(.o_status_green,.o_status_bubble)");
        assert.containsNone(subtaskEl, ".o_field_widget.o_field_project_task_state_selection.subtask_state_widget_col .o_status:not(.o_status_green,.o_status_bubble)", "The state of the subtask should no longer be in progress");
        assert.verifySteps([
            "project.task/web_read",
            "project.task/onchange",
            "project.task/web_save",
        ]);
    });

    QUnit.test("Create a subtask from the kanban view", async function (assert) {
        let checkSteps = false;
        const pyEnv = await startServer();
        const { openView } = await start({
            serverData: { views: this.views },
            mockRPC(route, { args, model, method }) {
                if (checkSteps) {
                    assert.step(`${model}/${method}`);
                }
                if (route === '/web/dataset/call_kw/project.task/create') {
                    const [{ display_name, parent_id }] = args[0];
                    assert.strictEqual(display_name, 'foo')
                    assert.strictEqual(parent_id, 1)
                    return pyEnv['project.task'].create({ name: display_name, parent_id: parent_id, state: '01_in_progress' });
                }
            },
        });
        await openView({
            res_model: "project.task",
            views: [[false, "kanban"]],
        });

        assert.strictEqual(target.querySelector(".subtask_list_button").parentElement.textContent, "1/4");
        checkSteps = true;
        await click(target.querySelector('.subtask_list_button'));
        await click(target.querySelector('.subtask_create'));
        await editInput(target.querySelector('.subtask_create_input'), "input", "foo");

        assert.containsN(target, '.subtask_list_row', 4, "The subtasks list should now display the subtask created on the card, thus we are looking for 4 in total");
        assert.verifySteps([
            "project.task/web_read",
            "project.task/create",
            "project.task/web_read",
        ]);
    });

    QUnit.test("Check that the sub task of another project can be added", async function (assert) {
        assert.expect(1);
        await start({
            serverData: { views: this.views },
        });
        await openFormView("project.task", this.task);
        await click(target.querySelector(".o_field_x2many_list_row_add a"));
        await clickDropdown(target, 'project_id');
        await clickOpenedDropdownItem(target, 'project_id', 'Project One');
        await editInput(target, ".o_data_row > td[name='name'] > div > input", "aaa");
        await click(target, ".o_form_button_save");
        assert.equal(target.querySelector('.o_field_project').textContent.trim(), 'Project One')
    });

    QUnit.test("focus new subtask's name", async function (assert) {
        const views = this.views;
        await start({ serverData: { views } });
        await openFormView("project.task");
        await click(target.querySelector(".o_field_x2many_list_row_add a"));

        assert.strictEqual(
            document.activeElement,
            target.querySelector(".o_data_row > td[name='name'] > div > input"),
            "Upon clicking on 'Add a line', the new subtask's name should be focused."
        );
    });
});

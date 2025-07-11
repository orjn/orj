import { _t } from "@web/core/l10n/translation";

import { Component, useState } from "@orj/owl";

import { useService } from "@web/core/utils/hooks";
import { useModel } from "@web/model/model";
import { extractFieldsFromArchInfo } from "@web/model/relational_model/utils";
import { CogMenu } from "@web/search/cog_menu/cog_menu";
import { Layout } from "@web/search/layout";
import { SearchBar } from "@web/search/search_bar/search_bar";
import { usePager } from "@web/search/pager_hook";
import { standardViewProps } from "@web/views/standard_view_props";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";

export class ActivityController extends Component {
    static components = { Layout, SearchBar, CogMenu };
    static props = {
        ...standardViewProps,
        Model: Function,
        Renderer: Function,
        archInfo: Object,
    };
    static template = "mail.ActivityController";

    setup() {
        this.model = useState(useModel(this.props.Model, this.modelParams));

        this.dialog = useService("dialog");
        this.action = useService("action");
        this.store = useService("mail.store");
        this.ui = useState(useService("ui"));
        usePager(() => {
            const { count, hasLimitedCount, limit, offset } = this.model.root;
            return {
                offset: offset,
                limit: limit,
                total: count,
                onUpdate: async (params) => {
                    // Ensure that only (active) records with at least one activity, "done" (archived) or not, are fetched.
                    // We don't use active_test=false in the context because otherwise we would also get archived records.
                    params.domain = [...(this.model.originalDomain || []), ["activity_ids.active", "in", [true, false]]];
                    await Promise.all([
                        this.model.root.load(params),
                        this.model.fetchActivityData(params),
                    ]);
                },
                updateTotal: hasLimitedCount ? () => this.model.root.fetchCount() : undefined,
            };
        });
    }

    get modelParams() {
        const { archInfo, resModel } = this.props;
        const { activeFields, fields } = extractFieldsFromArchInfo(archInfo, this.props.fields);
        return {
            config: {
                activeFields,
                resModel,
                fields,
            },
        };
    }

    getSearchProps() {
        const { comparision, context, domain, groupBy, orderBy } = this.env.searchModel;
        return { comparision, context, domain, groupBy, orderBy };
    }

    scheduleActivity() {
        this.dialog.add(SelectCreateDialog, {
            resModel: this.props.resModel,
            searchViewId: this.env.searchModel.searchViewId,
            domain: this.model.originalDomain,
            title: _t("Search: %s", this.props.archInfo.title),
            multiSelect: false,
            context: this.props.context,
            noCreate: this.props.context?.create === false,
            onSelected: async (resIds) => {
                await this.store.scheduleActivity(this.props.resModel, resIds);
            },
        }, {
            onClose: () => this.model.load(this.getSearchProps())
        });
    }

    openActivityFormView(resId, activityTypeId) {
        this.action.doAction(
            {
                type: "ir.actions.act_window",
                res_model: "mail.activity",
                views: [[false, "form"]],
                view_mode: "form",
                view_type: "form",
                res_id: false,
                target: "new",
                context: {
                    default_res_id: resId,
                    default_res_model: this.props.resModel,
                    default_activity_type_id: activityTypeId,
                },
            },
            {
                onClose: () => this.model.load(this.getSearchProps()),
            }
        );
    }

    sendMailTemplate(templateID, activityTypeID) {
        const groupedActivities = this.model.activityData.grouped_activities;
        const resIds = [];
        for (const resId in groupedActivities) {
            const activityByType = groupedActivities[resId];
            const activity = activityByType[activityTypeID];
            if (activity) {
                resIds.push(parseInt(resId));
            }
        }
        this.model.orm.call(this.props.resModel, "activity_send_mail", [resIds, templateID], {});
    }

    async openRecord(record, mode) {
        const activeIds = this.model.root.records.map((datapoint) => datapoint.resId);
        this.props.selectRecord(record.resId, { activeIds, mode });
    }

    get rendererProps() {
        return {
            activityTypes: this.model.activityData.activity_types,
            activityResIds: this.model.activityData.activity_res_ids,
            fields: this.model.root.fields,
            records: this.model.root.records,
            resModel: this.props.resModel,
            archInfo: this.props.archInfo,
            groupedActivities: this.model.activityData.grouped_activities,
            scheduleActivity: this.scheduleActivity.bind(this),
            onReloadData: () => this.model.load(this.getSearchProps()),
            onEmptyCell: this.openActivityFormView.bind(this),
            onSendMailTemplate: this.sendMailTemplate.bind(this),
            openRecord: this.openRecord.bind(this),
        };
    }
}

import { ActivityListPopover } from "@mail/core/web/activity_list_popover";
import { Avatar } from "@mail/views/web/fields/avatar/avatar";

import { Component, useRef } from "@orj/owl";

import { usePopover } from "@web/core/popover/popover_hook";

import { formatDate } from "@web/core/l10n/dates";

export class ActivityCell extends Component {
    static components = {
        Avatar,
    };
    static props = {
        activityIds: {
            type: Array,
            elements: Number,
        },
        attachmentsInfo: {
            optional: true,
            type: Object,
        },
        activityTypeId: Number,
        reportingDate: String,
        countByState: Object,
        reloadFunc: Function,
        resId: Number,
        resModel: String,
        userAssignedIds: Array,
    };
    static template = "mail.ActivityCell";

    setup() {
        this.popover = usePopover(ActivityListPopover, { position: "bottom-start" });
        this.contentRef = useRef("content");
    }

    get reportingDateFormatted() {
        return formatDate(luxon.DateTime.fromISO(this.props.reportingDate));
    }

    get ongoingActivityCount() {
        return (
            (this.props.countByState?.planned ?? 0) +
            (this.props.countByState?.today ?? 0) +
            (this.props.countByState?.overdue ?? 0)
        );
    }

    get totalActivityCount() {
        return this.ongoingActivityCount + (this.props.countByState?.done ?? 0);
    }

    onClick() {
        if (this.popover.isOpen) {
            this.popover.close();
        } else {
            this.popover.open(this.contentRef.el, {
                activityIds: this.props.activityIds,
                defaultActivityTypeId: this.props.activityTypeId,
                onActivityChanged: () => {
                    this.props.reloadFunc();
                    this.popover.close();
                },
                resId: this.props.resId,
                resModel: this.props.resModel,
            });
        }
    }
}

import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { ChatterComposer } from "./chatter_composer";
import { ChatterMessageCounter } from "./chatter_message_counter";
import { ChatterMessages } from "./chatter_messages";
import { ChatterPager } from "./chatter_pager";
import { Component, markup, onWillStart, useState, onWillUpdateProps } from "@orj/owl";

export class ChatterContainer extends Component {
    static template = "project.ChatterContainer";
    static components = {
        ChatterComposer,
        ChatterMessageCounter,
        ChatterMessages,
        ChatterPager,
    };
    static props = {
        token: { type: String, optional: true },
        resModel: String,
        resId: { type: Number, optional: true },
        pid: { type: String, optional: true },
        hash: { type: String, optional: true },
        pagerStart: { type: Number, optional: true },
        twoColumns: { type: Boolean, optional: true },
        projectSharingId: Number,
        isFollower: Boolean,
        displayFollowButton: Boolean,
    };
    static defaultProps = {
        token: "",
        pid: "",
        hash: "",
        pagerStart: 1,
    };

    setup() {
        this.state = useState({
            currentPage: this.props.pagerStart,
            messages: [],
            options: this.defaultOptions,
        });
        this.ormService = useService("orm");

        onWillStart(this.onWillStart);
        onWillUpdateProps(this.onWillUpdateProps);
    }

    get defaultOptions() {
        return {
            message_count: 0,
            is_user_public: true,
            is_user_employee: false,
            is_user_published: false,
            display_composer: Boolean(this.props.resId),
            partner_id: null,
            pager_scope: 4,
            pager_step: 10,
            is_follower: this.props.isFollower,
        };
    }

    get options() {
        return this.state.options;
    }

    set options(options) {
        this.state.options = {
            ...this.defaultOptions,
            ...options,
            display_composer: !!options.display_composer,
            access_token: typeof options.display_composer === 'string' ? options.display_composer : '',
        };
    }

    get composerProps() {
        return {
            allowComposer: Boolean(this.props.resId),
            displayComposer: this.state.options.display_composer,
            partnerId: this.state.options.partner_id || undefined,
            token: this.state.options.access_token,
            resModel: this.props.resModel,
            resId: this.props.resId,
            projectSharingId: this.props.projectSharingId,
            postProcessMessageSent: async () => {
                this.state.currentPage = 1;
                const prom = [this.fetchMessages()];
                this.state.options.is_follower = true;
                await Promise.all(prom);
            },
            attachments: this.state.options.default_attachment_ids,
        };
    }

    onWillStart() {
        this.initChatter(this.messagesParams(this.props));
    }

    onWillUpdateProps(nextProps) {
        this.initChatter(this.messagesParams(nextProps));
    }

    async onChangePage(page) {
        this.state.currentPage = page;
        await this.fetchMessages();
    }

    async initChatter(params) {
        if (params.res_id && params.res_model) {
            const chatterData = await rpc(
                '/mail/chatter_init',
                params,
            );
            this.state.messages = this.preprocessMessages(chatterData.messages);
            this.options = chatterData.options;
        } else {
            this.state.messages = [];
            this.options = {};
        }
    }

    async fetchMessages() {
        const result = await rpc(
            '/mail/chatter_fetch',
            this.messagesParams(this.props),
        );
        this.state.messages = this.preprocessMessages(result.messages);
        this.state.options.message_count = result.message_count;
        return result;
    }

    async toggleIsFollower() {
        const isFollower = await this.ormService.call(
            this.props.resModel,
            "project_sharing_toggle_is_follower",
            [this.props.resId]
        );
        this.state.options.is_follower = isFollower;
    }

    messagesParams(props) {
        const params = {
            res_model: props.resModel,
            res_id: props.resId,
            limit: this.state.options.pager_step,
            offset: (this.state.currentPage - 1) * this.state.options.pager_step,
            allow_composer: Boolean(props.resId),
            project_sharing_id: props.projectSharingId,
        };
        if (props.token) {
            params.token = props.token;
        }
        return params;
    }

    preprocessMessages(messages) {
        return messages.map(m => ({
            ...m,
            body: markup(m.body),
        }));
    }

    updateMessage(message_id, changes) {
        Object.assign(
            this.state.messages.find(m => m.id === message_id),
            changes,
        );
    }
}

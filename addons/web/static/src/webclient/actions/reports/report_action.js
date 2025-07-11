import { useService } from "@web/core/utils/hooks";
import { useSetupAction } from "@web/search/action_hook";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useEnrichWithActionLinks } from "@web/webclient/actions/reports/report_hook";

import { Component, useRef, useSubEnv } from "@orj/owl";

/**
 * Most of the time reports are printed as pdfs.
 * However, reports have 3 possible actions: pdf, text and HTML.
 * This file is the HTML action.
 * The HTML action is a client action (with control panel) rendering the template in an iframe.
 * If not defined as the default action, the HTML is the fallback to pdf if wkhtmltopdf is not available.
 *
 * It has a button to print the report.
 * It uses a feature to automatically create links to other orj pages if the selector [res-id][res-model][view-type]
 * is detected.
 */
export class ReportAction extends Component {
    static components = { Layout };
    static template = "web.ReportAction";
    static props = ["*"];
    setup() {
        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });
        useSetupAction();

        this.action = useService("action");
        this.title = this.props.display_name || this.props.name;
        this.reportUrl = this.props.report_url;
        this.iframe = useRef("iframe");
        useEnrichWithActionLinks(this.iframe);
    }

    onIframeLoaded(ev) {
        const iframeDocument = ev.target.contentWindow.document;
        iframeDocument.body.classList.add("o_in_iframe", "container-fluid");
        iframeDocument.body.classList.remove("container");
    }

    print() {
        this.action.doAction({
            type: "ir.actions.report",
            report_type: "qweb-pdf",
            report_name: this.props.report_name,
            report_file: this.props.report_file,
            data: this.props.data || {},
            context: this.props.context || {},
            display_name: this.title,
        });
    }
}

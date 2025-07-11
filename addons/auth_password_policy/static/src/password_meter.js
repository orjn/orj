/** @orj-module **/

import { _t } from "@web/core/l10n/translation";
import { computeScore } from "./password_policy";
import { Component, xml } from "@orj/owl";

export class Meter extends Component {
    static template = xml`
    <meter class="o_password_meter"
           min="0" low="0.5" high="0.99" max="1" optimum="1"
           t-att-title="title" t-att-value="value"/>
    `;
    static props = {
        password: { type: String },
        required: Object,
        recommended: Object,
    };

    get title() {
        return _t(
            "Required: %s\n\nHint: to increase password strength, increase length, use multiple words, and use non-letter characters.",
            String(this.props.required) || _t("no requirements")
        );
    }

    get value() {
        return computeScore(this.props.password, this.props.required, this.props.recommended);
    }
}

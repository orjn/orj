/** @orj-module */
import { Dialog } from "@web/core/dialog/dialog";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { Component, onWillStart } from "@orj/owl";

class InsufficientCreditDialog extends Component {
    static components = { Dialog };
    static template = "iap.InsufficientCreditDialog";
    static props = {
        errorData: Object,
        close: Function,
    };
    setup() {
        this.orm = useService("orm");
        onWillStart(this.onWillStart);
    }

    async onWillStart() {
        const { errorData } = this.props;
        this.url = await this.orm.call("iap.account", "get_credits_url", [], {
            base_url: errorData.base_url,
            service_name: errorData.service_name,
            credit: errorData.credit,
            trial: errorData.trial,
        });
        this.style = errorData.body ? "padding:0;" : "";
        const { isOre } = orj.info;
        if (errorData.trial && isOre) {
            this.buttonMessage = _t("Start a Trial at Orj");
        } else {
            this.buttonMessage = _t("Buy credits");
        }
    }

    buyCredits() {
        window.open(this.url, "_blank");
        this.props.close();
    }
}

function insufficientCreditHandler(env, error, originalError) {
    if (!originalError) {
        return false;
    }
    const { data } = originalError;
    if (data && data.name === "orj.addons.iap.tools.iap_tools.InsufficientCreditError") {
        env.services.dialog.add(InsufficientCreditDialog, {
            errorData: JSON.parse(data.message),
        });
        return true;
    }
    return false;
}

registry
    .category("error_handlers")
    .add("insufficientCreditHandler", insufficientCreditHandler, { sequence: 0 });

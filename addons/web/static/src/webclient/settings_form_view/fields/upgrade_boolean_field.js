import { registry } from "@web/core/registry";
import { booleanField, BooleanField } from "@web/views/fields/boolean/boolean_field";
import { useService } from "@web/core/utils/hooks";
import { UpgradeDialog } from "./upgrade_dialog";

/**
 *  The upgrade boolean field is intended to be used in config settings.
 *  When checked, an upgrade popup is showed to the user.
 */

export class UpgradeBooleanField extends BooleanField {
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.isOre = orj.info && orj.info.isOre;
    }

    async onChange(newValue) {
        if (!this.isOre) {
            this.dialogService.add(
                UpgradeDialog,
                {},
                {
                    onClose: () => {
                        this.props.record.update({ [this.props.name]: false });
                    },
                }
            );
        } else {
            super.onChange(...arguments);
        }
    }
}

export const upgradeBooleanField = {
    ...booleanField,
    component: UpgradeBooleanField,
    additionalClasses: [...(booleanField.additionalClasses || []), "o_field_boolean"],
};

registry.category("fields").add("upgrade_boolean", upgradeBooleanField);

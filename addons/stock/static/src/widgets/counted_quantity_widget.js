/** @orj-module **/

import { FloatField, floatField } from "@web/views/fields/float/float_field";
import { registry } from "@web/core/registry";
import { getActiveHotkey } from "@web/core/hotkeys/hotkey_service";
import { useEffect, useRef } from "@orj/owl";

export class CountedQuantityWidgetField extends FloatField {
    setup() {
        // Need to adapt useInputField to overide onInput and onChange
        super.setup();

        const inputRef = useRef("numpadDecimal");

        useEffect(
            (inputEl) => {
                if (inputEl) {
                    inputEl.addEventListener("input", this.onInput.bind(this));
                    inputEl.addEventListener("keydown", this.onKeydown.bind(this));
                    inputEl.addEventListener("blur", this.onBlur.bind(this));
                    return () => {
                        inputEl.removeEventListener("input", this.onInput.bind(this));
                        inputEl.removeEventListener("keydown", this.onKeydown.bind(this));
                        inputEl.removeEventListener("blur", this.onBlur.bind(this));
                    };
                }
            },
            () => [inputRef.el]
        );
    }

    onInput(ev) {
        return this.props.record.update({ inventory_quantity_set: true });
    }

    updateValue(ev){
        try {
           const val = this.parse(ev.target.value);
            this.props.record.update({ [this.props.name]: val });
        } catch {} // ignore since it will be handled later
    }

    onBlur(ev) {
         if (!this.props.record.data.inventory_quantity_set) {
           return;
        }
        this.updateValue(ev);
    }

    onKeydown(ev) {
        const hotkey = getActiveHotkey(ev);
        if (["enter", "tab", "shift+tab"].includes(hotkey)) {
            this.updateValue(ev);
            this.onInput(ev);
        }
    }

    get formattedValue() {
        if (
            this.props.readonly &&
            !this.props.record.data[this.props.name] & !this.props.record.data.inventory_quantity_set
        ) {
            return "";
        }
        return super.formattedValue;
    }
}

export const countedQuantityWidgetField = {
    ...floatField,
    component: CountedQuantityWidgetField,
};

registry.category("fields").add("counted_quantity_widget", countedQuantityWidgetField);

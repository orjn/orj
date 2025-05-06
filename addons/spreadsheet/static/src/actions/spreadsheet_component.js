/** @orj-module */

import { useSpreadsheetNotificationStore } from "@spreadsheet/hooks";
import { Spreadsheet, Model } from "@orj/o-spreadsheet";
import { Component } from "@orj/owl";

/**
 * Component wrapping the <Spreadsheet> component from o-spreadsheet
 * to add user interactions extensions from orj such as notifications,
 * error dialogs, etc.
 */
export class SpreadsheetComponent extends Component {
    static template = "spreadsheet.SpreadsheetComponent";
    static components = { Spreadsheet };
    static props = {
        model: Model,
    };

    get model() {
        return this.props.model;
    }
    setup() {
        useSpreadsheetNotificationStore();
    }
}

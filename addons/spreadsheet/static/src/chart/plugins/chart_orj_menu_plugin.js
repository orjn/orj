/** @orj-module */

import { OrjCorePlugin } from "@spreadsheet/plugins";
import { coreTypes, helpers } from "@orj/o-spreadsheet";
import { omit } from "@web/core/utils/objects";
const { deepEquals } = helpers;

/** Plugin that link charts with Orj menus. It can contain either the Id of the orj menu, or its xml id. */
export class ChartOrjMenuPlugin extends OrjCorePlugin {
    static getters = /** @type {const} */ (["getChartOrjMenu"]);
    constructor(config) {
        super(config);
        this.orjMenuReference = {};
    }

    /**
     * Handle a spreadsheet command
     * @param {Object} cmd Command
     */
    handle(cmd) {
        switch (cmd.type) {
            case "LINK_ORJ_MENU_TO_CHART":
                this.history.update("orjMenuReference", cmd.chartId, cmd.orjMenuId);
                break;
            case "DELETE_FIGURE":
                this.history.update("orjMenuReference", cmd.id, undefined);
                break;
            case "DUPLICATE_SHEET":
                this.updateOnDuplicateSheet(cmd.sheetId, cmd.sheetIdTo);
                break;
        }
    }

    updateOnDuplicateSheet(sheetIdFrom, sheetIdTo) {
        for (const oldChartId of this.getters.getChartIds(sheetIdFrom)) {
            if (!this.orjMenuReference[oldChartId]) {
                continue;
            }
            const oldChartDefinition = this.getters.getChartDefinition(oldChartId);
            const oldFigure = this.getters.getFigure(sheetIdFrom, oldChartId);
            const newChartId = this.getters.getChartIds(sheetIdTo).find((newChartId) => {
                const newChartDefinition = this.getters.getChartDefinition(newChartId);
                const newFigure = this.getters.getFigure(sheetIdTo, newChartId);
                return (
                    deepEquals(oldChartDefinition, newChartDefinition) &&
                    deepEquals(omit(newFigure, "id"), omit(oldFigure, "id")) // compare size and position
                );
            });

            if (newChartId) {
                this.history.update(
                    "orjMenuReference",
                    newChartId,
                    this.orjMenuReference[oldChartId]
                );
            }
        }
    }

    /**
     * Get orj menu linked to the chart
     *
     * @param {string} chartId
     * @returns {object | undefined}
     */
    getChartOrjMenu(chartId) {
        const menuId = this.orjMenuReference[chartId];
        return menuId ? this.getters.getIrMenu(menuId) : undefined;
    }

    import(data) {
        if (data.chartOrjMenusReferences) {
            this.orjMenuReference = data.chartOrjMenusReferences;
        }
    }

    export(data) {
        data.chartOrjMenusReferences = this.orjMenuReference;
    }
}

coreTypes.add("LINK_ORJ_MENU_TO_CHART");

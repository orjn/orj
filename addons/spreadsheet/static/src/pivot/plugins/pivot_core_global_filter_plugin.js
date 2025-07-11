/** @orj-module */
// @ts-check
/**
 *
 * @typedef {import("@spreadsheet").OrjPivotDefinition} OrjPivotDefinition
 * @typedef {import("@spreadsheet").AllCoreCommand} AllCoreCommand
 * @typedef {import("@spreadsheet").GFLocalPivot} GFLocalPivot
 *
 * @typedef {import("@spreadsheet").FieldMatching} FieldMatching
 */

import { CommandResult } from "../../o_spreadsheet/cancelled_reason";
import { _t } from "@web/core/l10n/translation";
import { globalFiltersFieldMatchers } from "@spreadsheet/global_filters/plugins/global_filters_core_plugin";
import { sprintf } from "@web/core/utils/strings";
import { checkFilterFieldMatching } from "@spreadsheet/global_filters/helpers";
import { deepCopy } from "@web/core/utils/objects";
import { OrjCorePlugin } from "@spreadsheet/plugins";

export class PivotCoreGlobalFilterPlugin extends OrjCorePlugin {
    static getters = /** @type {const} */ (["getPivotFieldMatch", "getPivotFieldMatching"]);
    constructor(config) {
        super(config);

        /** @type {Object.<string, GFLocalPivot>} */
        this.pivots = {};
        globalFiltersFieldMatchers["pivot"] = {
            getIds: () =>
                this.getters
                    .getPivotIds()
                    .filter(
                        (id) =>
                            this.getters.getPivotCoreDefinition(id).type === "ORJ" &&
                            id in this.pivots
                    ),
            getDisplayName: (pivotId) => this.getters.getPivotName(pivotId),
            getTag: (pivotId) => sprintf(_t("Pivot #%s"), this.getters.getPivotFormulaId(pivotId)),
            getFieldMatching: (pivotId, filterId) => this.getPivotFieldMatching(pivotId, filterId),
            getModel: (pivotId) => {
                const pivot = this.getters.getPivotCoreDefinition(pivotId);
                return pivot.type === "ORJ" && pivot.model;
            },
        };
    }

    /**
     * @param {AllCoreCommand} cmd
     *
     * @returns {string | string[]}
     */
    allowDispatch(cmd) {
        switch (cmd.type) {
            case "ADD_GLOBAL_FILTER":
            case "EDIT_GLOBAL_FILTER":
                if (cmd.pivot) {
                    return checkFilterFieldMatching(cmd.pivot);
                }
        }
        return CommandResult.Success;
    }

    /**
     * @param {AllCoreCommand} cmd
     *
     */
    handle(cmd) {
        switch (cmd.type) {
            case "ADD_PIVOT": {
                if (cmd.pivot.type === "ORJ") {
                    this._addPivot(cmd.pivotId, undefined);
                }
                break;
            }
            case "REMOVE_PIVOT": {
                this.history.update("pivots", cmd.pivotId, undefined);
                break;
            }
            case "DUPLICATE_PIVOT": {
                const { pivotId, newPivotId } = cmd;
                const pivotDefinition = this.getters.getPivotCoreDefinition(pivotId);
                if(pivotDefinition.type !== "ORJ") {
                    break;
                }
                const pivot = deepCopy(this.pivots[pivotId]);
                this._addPivot(newPivotId, pivot.fieldMatching);
                break;
            }
            case "ADD_GLOBAL_FILTER":
            case "EDIT_GLOBAL_FILTER":
                if (cmd.pivot) {
                    this._setPivotFieldMatching(cmd.filter.id, cmd.pivot);
                }
                break;
            case "REMOVE_GLOBAL_FILTER":
                this._onFilterDeletion(cmd.id);
                break;
        }
    }

    // -------------------------------------------------------------------------
    // Getters
    // -------------------------------------------------------------------------

    /**
     * @param {string} id
     * @returns {Record<string, FieldMatching>}
     */
    getPivotFieldMatch(id) {
        const pivot = this.getters.getPivotCoreDefinition(id);
        if (pivot.type !== "ORJ") {
            return {};
        }
        return this.pivots[id].fieldMatching;
    }

    /**
     * Get the current pivotFieldMatching on a pivot
     *
     * @param {string} pivotId
     * @param {string} filterId
     */
    getPivotFieldMatching(pivotId, filterId) {
        return this.getPivotFieldMatch(pivotId)[filterId];
    }

    // -------------------------------------------------------------------------
    // Private
    // -------------------------------------------------------------------------

    /**
     * Sets the current pivotFieldMatching on a pivot
     *
     * @param {string} filterId
     * @param {Record<string,FieldMatching>} pivotFieldMatches
     */
    _setPivotFieldMatching(filterId, pivotFieldMatches) {
        for (const [pivotId, fieldMatch] of Object.entries(pivotFieldMatches)) {
            const pivot = this.getters.getPivotCoreDefinition(pivotId);
            if (pivot.type !== "ORJ") {
                continue;
            }
            this.history.update("pivots", pivotId, "fieldMatching", filterId, fieldMatch);
        }
    }

    _onFilterDeletion(filterId) {
        const pivots = { ...this.pivots };
        for (const pivotId in pivots) {
            this.history.update("pivots", pivotId, "fieldMatching", filterId, undefined);
        }
    }

    /**
     * @param {string} id
     * @param {Record<string, FieldMatching>} [fieldMatching]
     */
    _addPivot(id, fieldMatching = undefined) {
        const pivot = this.getters.getPivotCoreDefinition(id);
        if (pivot.type === "ORJ") {
            this.history.update("pivots", id, {
                id,
                fieldMatching: fieldMatching || this.getters.getFieldMatchingForModel(pivot.model),
            });
        }
    }

    // ---------------------------------------------------------------------
    // Import/Export
    // ---------------------------------------------------------------------

    /**
     * Import the pivots
     *
     * @param {Object} data
     */
    import(data) {
        if (data.pivots) {
            for (const [id, pivot] of Object.entries(data.pivots)) {
                this._addPivot(id, pivot.fieldMatching);
            }
        }
    }
    /**
     * Export the pivots
     *
     * @param {Object} data
     */
    export(data) {
        for (const id in this.pivots) {
            const pivot = this.getters.getPivotCoreDefinition(id);
            data.pivots[id].fieldMatching =
                pivot.type === "ORJ" ? this.pivots[id].fieldMatching : {};
        }
    }
}

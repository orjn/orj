/** @orj-module */
import { globalFiltersFieldMatchers } from "@spreadsheet/global_filters/plugins/global_filters_core_plugin";
import { checkFilterFieldMatching } from "@spreadsheet/global_filters/helpers";
import { CommandResult } from "../../o_spreadsheet/cancelled_reason";
import { Domain } from "@web/core/domain";
import { OrjCorePlugin } from "@spreadsheet/plugins";
import { _t } from "@web/core/l10n/translation";

/**
 * @typedef {Object} Chart
 * @property {Object} fieldMatching
 *
 * @typedef {import("@spreadsheet").FieldMatching} FieldMatching
 */

const CHART_PLACEHOLDER_DISPLAY_NAME = {
    orj_bar: _t("Orj Bar Chart"),
    orj_line: _t("Orj Line Chart"),
    orj_pie: _t("Orj Pie Chart"),
};

export class OrjChartCorePlugin extends OrjCorePlugin {
    static getters = /** @type {const} */ ([
        "getOrjChartIds",
        "getChartFieldMatch",
        "getOrjChartDisplayName",
        "getOrjChartFieldMatching",
    ]);

    constructor(config) {
        super(config);

        /** @type {Object.<string, Chart>} */
        this.charts = {};

        globalFiltersFieldMatchers["chart"] = {
            getIds: () => this.getters.getOrjChartIds(),
            getDisplayName: (chartId) => this.getters.getOrjChartDisplayName(chartId),
            getFieldMatching: (chartId, filterId) =>
                this.getOrjChartFieldMatching(chartId, filterId),
            getModel: (chartId) =>
                this.getters.getChart(chartId).getDefinitionForDataSource().metaData.resModel,
        };
    }

    allowDispatch(cmd) {
        switch (cmd.type) {
            case "ADD_GLOBAL_FILTER":
            case "EDIT_GLOBAL_FILTER":
                if (cmd.chart) {
                    return checkFilterFieldMatching(cmd.chart);
                }
        }
        return CommandResult.Success;
    }

    /**
     * Handle a spreadsheet command
     *
     * @param {Object} cmd Command
     */
    handle(cmd) {
        switch (cmd.type) {
            case "CREATE_CHART": {
                switch (cmd.definition.type) {
                    case "orj_pie":
                    case "orj_bar":
                    case "orj_line":
                        this._addOrjChart(cmd.id);
                        break;
                }
                break;
            }
            case "DELETE_FIGURE": {
                const charts = { ...this.charts };
                delete charts[cmd.id];
                this.history.update("charts", charts);
                break;
            }
            case "REMOVE_GLOBAL_FILTER":
                this._onFilterDeletion(cmd.id);
                break;
            case "ADD_GLOBAL_FILTER":
            case "EDIT_GLOBAL_FILTER":
                if (cmd.chart) {
                    this._setOrjChartFieldMatching(cmd.filter.id, cmd.chart);
                }
                break;
        }
    }

    // -------------------------------------------------------------------------
    // Getters
    // -------------------------------------------------------------------------

    /**
     * Get all the orj chart ids
     * @returns {Array<string>}
     */
    getOrjChartIds() {
        return Object.keys(this.charts);
    }

    /**
     * @param {string} chartId
     * @returns {string}
     */
    getChartFieldMatch(chartId) {
        return this.charts[chartId].fieldMatching;
    }

    /**
     *
     * @param {string} chartId
     * @returns {string}
     */
    getOrjChartDisplayName(chartId) {
        const { title, type } = this.getters.getChart(chartId);
        const name = title.text || CHART_PLACEHOLDER_DISPLAY_NAME[type];
        return `(#${this.getOrjChartIds().indexOf(chartId) + 1}) ${name}`;
    }

    /**
     * Import the charts
     *
     * @param {Object} data
     */
    import(data) {
        for (const sheet of data.sheets) {
            if (sheet.figures) {
                for (const figure of sheet.figures) {
                    if (figure.tag === "chart" && figure.data.type.startsWith("orj_")) {
                        this._addOrjChart(figure.id, figure.data.fieldMatching);
                    }
                }
            }
        }
    }
    /**
     * Export the chart
     *
     * @param {Object} data
     */
    export(data) {
        for (const sheet of data.sheets) {
            if (sheet.figures) {
                for (const figure of sheet.figures) {
                    if (figure.tag === "chart" && figure.data.type.startsWith("orj_")) {
                        figure.data.fieldMatching = this.getChartFieldMatch(figure.id);
                        figure.data.searchParams.domain = new Domain(
                            figure.data.searchParams.domain
                        ).toJson();
                    }
                }
            }
        }
    }
    // -------------------------------------------------------------------------
    // Private
    // -------------------------------------------------------------------------

    /**
     * Get the current orjChartFieldMatching of a chart
     *
     * @param {string} chartId
     * @param {string} filterId
     */
    getOrjChartFieldMatching(chartId, filterId) {
        return this.charts[chartId].fieldMatching[filterId];
    }

    /**
     * Sets the current orjChartFieldMatching of a chart
     *
     * @param {string} filterId
     * @param {Record<string,FieldMatching>} chartFieldMatches
     */
    _setOrjChartFieldMatching(filterId, chartFieldMatches) {
        const charts = { ...this.charts };
        for (const [chartId, fieldMatch] of Object.entries(chartFieldMatches)) {
            charts[chartId].fieldMatching[filterId] = fieldMatch;
        }
        this.history.update("charts", charts);
    }

    _onFilterDeletion(filterId) {
        const charts = { ...this.charts };
        for (const chartId in charts) {
            this.history.update("charts", chartId, "fieldMatching", filterId, undefined);
        }
    }

    /**
     * @param {string} chartId
     * @param {Object} fieldMatching
     */
    _addOrjChart(chartId, fieldMatching = undefined) {
        const charts = { ...this.charts };
        if (!fieldMatching) {
            const model = this.getters.getChartDefinition(chartId).metaData.resModel;
            fieldMatching = this.getters.getFieldMatchingForModel(model);
        }
        charts[chartId] = {
            fieldMatching,
        };
        this.history.update("charts", charts);
    }
}

/** @orj-module */

import * as spreadsheet from "@orj/o-spreadsheet";
import { _t } from "@web/core/l10n/translation";
import { OrjChart } from "./orj_chart";

const { chartRegistry } = spreadsheet.registries;

const {
    getDefaultChartJsRuntime,
    getChartAxisTitleRuntime,
    chartFontColor,
    ColorGenerator,
    getTrendDatasetForBarChart,
    formatValue,
    formatTickValue,
} = spreadsheet.helpers;

const { TREND_LINE_XAXIS_ID } = spreadsheet.constants;

export class OrjBarChart extends OrjChart {
    constructor(definition, sheetId, getters) {
        super(definition, sheetId, getters);
        this.verticalAxisPosition = definition.verticalAxisPosition;
        this.stacked = definition.stacked;
        this.axesDesign = definition.axesDesign;
        this.trend = definition.trend;
    }

    getDefinition() {
        return {
            ...super.getDefinition(),
            verticalAxisPosition: this.verticalAxisPosition,
            stacked: this.stacked,
            axesDesign: this.axesDesign,
            trend: this.trend,
        };
    }
}

chartRegistry.add("orj_bar", {
    match: (type) => type === "orj_bar",
    createChart: (definition, sheetId, getters) => new OrjBarChart(definition, sheetId, getters),
    getChartRuntime: createOrjChartRuntime,
    validateChartDefinition: (validator, definition) =>
        OrjBarChart.validateChartDefinition(validator, definition),
    transformDefinition: (definition) => OrjBarChart.transformDefinition(definition),
    getChartDefinitionFromContextCreation: () => OrjBarChart.getDefinitionFromContextCreation(),
    name: _t("Bar"),
});

function createOrjChartRuntime(chart, getters) {
    const background = chart.background || "#FFFFFF";
    const { datasets, labels } = chart.dataSource.getData();
    const locale = getters.getLocale();
    const chartJsConfig = getBarConfiguration(chart, labels, locale);
    chartJsConfig.options = {
        ...chartJsConfig.options,
        ...getters.getChartDatasetActionCallbacks(chart),
    };
    const colors = new ColorGenerator(datasets.length);
    const trendDatasets = [];
    for (const { label, data } of datasets) {
        const color = colors.next();
        const dataset = {
            label,
            data,
            borderColor: "#FFFFFF",
            borderWidth: 1,
            backgroundColor: color,
        };
        chartJsConfig.data.datasets.push(dataset);

        const trend = chart.getDefinition().trend;
        if (!trend?.display || chart.horizontal) {
            continue;
        }

        const trendDataset = getTrendDatasetForBarChart(trend, dataset);
        if (trendDataset) {
            trendDatasets.push(trendDataset);
        }
    }

    if (trendDatasets.length) {
        /* We add a second x axis here to draw the trend lines, with the labels length being
         * set so that the second axis points match the classical x axis
         */
        const maxLength = Math.max(
            ...trendDatasets.map((trendDataset) => trendDataset.data.length)
        );
        chartJsConfig.options.scales[TREND_LINE_XAXIS_ID] = {
            ...chartJsConfig.options.scales.x,
            labels: Array(maxLength).fill(""),
            offset: false,
            display: false,
        };
        /* These datasets must be inserted after the original
         * datasets to ensure the way we distinguish the originals and trendLine datasets after
         */
        trendDatasets.forEach((x) => chartJsConfig.data.datasets.push(x));

        const originalTooltipTitle = chartJsConfig.options.plugins.tooltip.callbacks.title;
        chartJsConfig.options.plugins.tooltip.callbacks.title = function (tooltipItems) {
            if (tooltipItems.some((item) => item.dataset.xAxisID !== TREND_LINE_XAXIS_ID)) {
                return originalTooltipTitle?.(tooltipItems);
            }
            return "";
        };
    }
    return { background, chartJsConfig };
}

function getBarConfiguration(chart, labels, locale) {
    const color = chartFontColor(chart.background);
    const config = getDefaultChartJsRuntime(chart, labels, color, { locale });
    config.type = chart.type.replace("orj_", "");
    const legend = {
        ...config.options.legend,
        display: chart.legendPosition !== "none",
        labels: { color },
    };
    legend.position = chart.legendPosition;
    config.options.plugins = config.options.plugins || {};
    config.options.plugins.legend = legend;
    config.options.layout = {
        padding: { left: 20, right: 20, top: chart.title ? 10 : 25, bottom: 10 },
    };
    config.options.scales = {
        x: {
            ticks: {
                // x axis configuration
                maxRotation: 60,
                minRotation: 15,
                padding: 5,
                labelOffset: 2,
                color,
            },
            title: getChartAxisTitleRuntime(chart.axesDesign?.x),
        },
        y: {
            position: chart.verticalAxisPosition,
            ticks: {
                color,
                callback: (value) =>
                    formatValue(value, {
                        locale,
                        format: Math.abs(value) >= 1000 ? "#,##" : undefined,
                    }),
            },
            beginAtZero: true, // the origin of the y axis is always zero
            title: getChartAxisTitleRuntime(chart.axesDesign?.y),
        },
    };
    if (chart.stacked) {
        config.options.scales.x.stacked = true;
        config.options.scales.y.stacked = true;
    }

    config.options.plugins.chartShowValuesPlugin = {
        showValues: chart.showValues,
        background: chart.background,
        horizontal: chart.horizontal,
        callback: formatTickValue({ locale }),
    };

    return config;
}

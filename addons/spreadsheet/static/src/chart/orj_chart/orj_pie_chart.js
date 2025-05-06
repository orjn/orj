/** @orj-module */

import * as spreadsheet from "@orj/o-spreadsheet";
import { _t } from "@web/core/l10n/translation";
import { OrjChart } from "./orj_chart";

const { chartRegistry } = spreadsheet.registries;

const { getDefaultChartJsRuntime, chartFontColor, ColorGenerator, formatTickValue } =
    spreadsheet.helpers;

chartRegistry.add("orj_pie", {
    match: (type) => type === "orj_pie",
    createChart: (definition, sheetId, getters) => new OrjChart(definition, sheetId, getters),
    getChartRuntime: createOrjChartRuntime,
    validateChartDefinition: (validator, definition) =>
        OrjChart.validateChartDefinition(validator, definition),
    transformDefinition: (definition) => OrjChart.transformDefinition(definition),
    getChartDefinitionFromContextCreation: () => OrjChart.getDefinitionFromContextCreation(),
    name: _t("Pie"),
});

function createOrjChartRuntime(chart, getters) {
    const background = chart.background || "#FFFFFF";
    const { datasets, labels } = chart.dataSource.getData();
    const locale = getters.getLocale();
    const chartJsConfig = getPieConfiguration(chart, labels, locale);
    chartJsConfig.options = {
        ...chartJsConfig.options,
        ...getters.getChartDatasetActionCallbacks(chart),
    };
    const dataSetsLength = Math.max(0, ...datasets.map((ds) => ds?.data?.length ?? 0));
    const colors = new ColorGenerator(dataSetsLength);
    for (const { label, data } of datasets) {
        const backgroundColor = getPieColors(colors, datasets);
        const dataset = {
            label,
            data,
            borderColor: "#FFFFFF",
            backgroundColor,
            hoverOffset: 30,
        };
        chartJsConfig.data.datasets.push(dataset);
    }
    return { background, chartJsConfig };
}

function getPieConfiguration(chart, labels, locale) {
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
    config.options.plugins.tooltip = {
        callbacks: {
            title: function (tooltipItem) {
                return tooltipItem.label;
            },
        },
    };

    config.options.plugins.chartShowValuesPlugin = {
        showValues: chart.showValues,
        callback: formatTickValue({ locale }),
    };
    return config;
}

function getPieColors(colors, dataSetsValues) {
    const pieColors = [];
    const maxLength = Math.max(...dataSetsValues.map((ds) => ds.data.length));
    for (let i = 0; i <= maxLength; i++) {
        pieColors.push(colors.next());
    }

    return pieColors;
}

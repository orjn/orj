/** @orj-module */

import * as spreadsheet from "@orj/o-spreadsheet";

const { chartComponentRegistry } = spreadsheet.registries;
const { ChartJsComponent } = spreadsheet.components;

chartComponentRegistry.add("orj_bar", ChartJsComponent);
chartComponentRegistry.add("orj_line", ChartJsComponent);
chartComponentRegistry.add("orj_pie", ChartJsComponent);

import { OrjChartCorePlugin } from "./plugins/orj_chart_core_plugin";
import { ChartOrjMenuPlugin } from "./plugins/chart_orj_menu_plugin";
import { OrjChartUIPlugin } from "./plugins/orj_chart_ui_plugin";

export { OrjChartCorePlugin, ChartOrjMenuPlugin, OrjChartUIPlugin };

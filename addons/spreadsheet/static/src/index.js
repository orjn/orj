/** @orj-module */

/**
 * This file is meant to load the different subparts of the module
 * to guarantee their plugins are loaded in the right order
 *
 * dependency:
 *             other plugins
 *                   |
 *                  ...
 *                   |
 *                filters
 *                /\    \
 *               /  \    \
 *           pivot  list  Orj chart
 */

/** TODO: Introduce a position parameter to the plugin registry in order to load them in a specific order */
import * as spreadsheet from "@orj/o-spreadsheet";
const { corePluginRegistry, coreViewsPluginRegistry } = spreadsheet.registries;

import { GlobalFiltersCorePlugin, GlobalFiltersUIPlugin } from "@spreadsheet/global_filters/index";
import { PivotOrjCorePlugin, PivotUIGlobalFilterPlugin } from "@spreadsheet/pivot/index"; // list depends on filter for its getters
import { ListCorePlugin, ListUIPlugin } from "@spreadsheet/list/index"; // pivot depends on filter for its getters
import {
    ChartOrjMenuPlugin,
    OrjChartCorePlugin,
    OrjChartUIPlugin,
} from "@spreadsheet/chart/index"; // Orjchart depends on filter for its getters
import { PivotCoreGlobalFilterPlugin } from "./pivot/plugins/pivot_core_global_filter_plugin";
import { PivotOrjUIPlugin } from "./pivot/plugins/pivot_orj_ui_plugin";

corePluginRegistry.add("OrjGlobalFiltersCorePlugin", GlobalFiltersCorePlugin);
corePluginRegistry.add("PivotOrjCorePlugin", PivotOrjCorePlugin);
corePluginRegistry.add("OrjPivotGlobalFiltersCorePlugin", PivotCoreGlobalFilterPlugin);
corePluginRegistry.add("OrjListCorePlugin", ListCorePlugin);
corePluginRegistry.add("orjChartCorePlugin", OrjChartCorePlugin);
corePluginRegistry.add("chartOrjMenuPlugin", ChartOrjMenuPlugin);

coreViewsPluginRegistry.add("OrjGlobalFiltersUIPlugin", GlobalFiltersUIPlugin);
coreViewsPluginRegistry.add("OrjPivotGlobalFilterUIPlugin", PivotUIGlobalFilterPlugin);
coreViewsPluginRegistry.add("OrjListUIPlugin", ListUIPlugin);
coreViewsPluginRegistry.add("orjChartUIPlugin", OrjChartUIPlugin);
coreViewsPluginRegistry.add("orjPivotUIPlugin", PivotOrjUIPlugin);

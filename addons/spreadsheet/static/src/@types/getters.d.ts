import { CorePlugin, Model, UID } from "@orj/o-spreadsheet";
import { ChartOrjMenuPlugin, OrjChartCorePlugin, OrjChartUIPlugin } from "@spreadsheet/chart";
import { CurrencyPlugin } from "@spreadsheet/currency/plugins/currency";
import { AccountingPlugin } from "addons/spreadsheet_account/static/src/plugins/accounting_plugin";
import { GlobalFiltersCorePlugin, GlobalFiltersUIPlugin } from "@spreadsheet/global_filters";
import { ListCorePlugin, ListUIPlugin } from "@spreadsheet/list";
import { IrMenuPlugin } from "@spreadsheet/ir_ui_menu/ir_ui_menu_plugin";
import { PivotOrjCorePlugin } from "@spreadsheet/pivot";
import { PivotCoreGlobalFilterPlugin } from "@spreadsheet/pivot/plugins/pivot_core_global_filter_plugin";

type Getters = Model["getters"];
type CoreGetters = CorePlugin["getters"];

/**
 * Union of all getter names of a plugin.
 *
 * e.g. With the following plugin
 * @example
 * class MyPlugin {
 *   static getters = [
 *     "getCell",
 *     "getCellValue",
 *   ] as const;
 *   getCell() { ... }
 *   getCellValue() { ... }
 * }
 * type Names = GetterNames<typeof MyPlugin>
 * // is equivalent to "getCell" | "getCellValue"
 */
type GetterNames<Plugin extends { getters: readonly string[] }> = Plugin["getters"][number];

/**
 * Extract getter methods from a plugin, based on its `getters` static array.
 * @example
 * class MyPlugin {
 *   static getters = [
 *     "getCell",
 *     "getCellValue",
 *   ] as const;
 *   getCell() { ... }
 *   getCellValue() { ... }
 * }
 * type MyPluginGetters = PluginGetters<typeof MyPlugin>;
 * // MyPluginGetters is equivalent to:
 * // {
 * //   getCell: () => ...,
 * //   getCellValue: () => ...,
 * // }
 */
type PluginGetters<Plugin extends { new (...args: unknown[]): any; getters: readonly string[] }> =
    Pick<InstanceType<Plugin>, GetterNames<Plugin>>;

declare module "@spreadsheet" {
    /**
     * Add getters from custom plugins defined in orj
     */

    interface OrjCoreGetters extends CoreGetters {}
    interface OrjCoreGetters extends PluginGetters<typeof GlobalFiltersCorePlugin> {}
    interface OrjCoreGetters extends PluginGetters<typeof ListCorePlugin> {}
    interface OrjCoreGetters extends PluginGetters<typeof OrjChartCorePlugin> {}
    interface OrjCoreGetters extends PluginGetters<typeof ChartOrjMenuPlugin> {}
    interface OrjCoreGetters extends PluginGetters<typeof IrMenuPlugin> {}
    interface OrjCoreGetters extends PluginGetters<typeof PivotOrjCorePlugin> {}
    interface OrjCoreGetters extends PluginGetters<typeof PivotCoreGlobalFilterPlugin> {}

    interface OrjGetters extends Getters {}
    interface OrjGetters extends OrjCoreGetters {}
    interface OrjGetters extends PluginGetters<typeof GlobalFiltersUIPlugin> {}
    interface OrjGetters extends PluginGetters<typeof ListUIPlugin> {}
    interface OrjGetters extends PluginGetters<typeof OrjChartUIPlugin> {}
    interface OrjGetters extends PluginGetters<typeof CurrencyPlugin> {}
    interface OrjGetters extends PluginGetters<typeof AccountingPlugin> {}
}

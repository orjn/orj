/** @orj-module */

import { CorePlugin, UIPlugin } from "@orj/o-spreadsheet";

/**
 * An o-spreadsheet core plugin with access to all custom Orj plugins
 * @type {import("@spreadsheet").OrjCorePluginConstructor}
 **/
export const OrjCorePlugin = CorePlugin;

/**
 * An o-spreadsheet UI plugin with access to all custom Orj plugins
 * @type {import("@spreadsheet").OrjUIPluginConstructor}
 **/
export const OrjUIPlugin = UIPlugin;

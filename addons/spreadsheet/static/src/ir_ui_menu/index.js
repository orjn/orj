/** @orj-module */

import { registry } from "@web/core/registry";
import * as spreadsheet from "@orj/o-spreadsheet";

import { IrMenuPlugin } from "./ir_ui_menu_plugin";

import {
    isMarkdownIrMenuIdUrl,
    isIrMenuXmlUrl,
    isMarkdownViewUrl,
    parseIrMenuXmlUrl,
    parseViewLink,
    parseIrMenuIdLink,
} from "./orj_menu_link_cell";
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";
import { navigateTo } from "../actions/helpers";

const { urlRegistry, corePluginRegistry, errorTypes } = spreadsheet.registries;
const { EvaluationError } = spreadsheet;

corePluginRegistry.add("ir_ui_menu_plugin", IrMenuPlugin);

const LINK_ERROR = "#LINK";
errorTypes.add(LINK_ERROR);

class BadOrjLinkError extends EvaluationError {
    constructor(menuId) {
        super(
            sprintf(_t("Menu %s not found. You may not have the required access rights."), menuId),
            LINK_ERROR
        );
    }
}

export const spreadsheetLinkMenuCellService = {
    dependencies: ["menu"],
    start(env) {
        function _getIrMenuByXmlId(xmlId) {
            const menu = env.services.menu.getAll().find((menu) => menu.xmlid === xmlId);
            if (!menu) {
                throw new BadOrjLinkError(xmlId);
            }
            return menu;
        }

        urlRegistry
            .add("OrjMenuIdLink", {
                sequence: 65,
                match: isMarkdownIrMenuIdUrl,
                createLink(url, label) {
                    const menuId = parseIrMenuIdLink(url);
                    const menu = env.services.menu.getMenu(menuId);
                    if (!menu) {
                        throw new BadOrjLinkError(menuId);
                    }
                    return {
                        url,
                        label: _t(label),
                        isExternal: false,
                        isUrlEditable: false,
                    };
                },
                urlRepresentation(url) {
                    const menuId = parseIrMenuIdLink(url);
                    return env.services.menu.getMenu(menuId).name;
                },
                open(url) {
                    const menuId = parseIrMenuIdLink(url);
                    const menu = env.services.menu.getMenu(menuId);
                    env.services.action.doAction(menu.actionID);
                },
            })
            .add("OrjMenuXmlLink", {
                sequence: 66,
                match: isIrMenuXmlUrl,
                createLink(url, label) {
                    const xmlId = parseIrMenuXmlUrl(url);
                    _getIrMenuByXmlId(xmlId);
                    return {
                        url,
                        label: _t(label),
                        isExternal: false,
                        isUrlEditable: false,
                    };
                },
                urlRepresentation(url) {
                    const xmlId = parseIrMenuXmlUrl(url);
                    const menuId = _getIrMenuByXmlId(xmlId).id;
                    return env.services.menu.getMenu(menuId).name;
                },
                open(url) {
                    const xmlId = parseIrMenuXmlUrl(url);
                    const menuId = _getIrMenuByXmlId(xmlId).id;
                    const menu = env.services.menu.getMenu(menuId);
                    env.services.action.doAction(menu.actionID);
                },
            })
            .add("OrjViewLink", {
                sequence: 67,
                match: isMarkdownViewUrl,
                createLink(url, label) {
                    return {
                        url,
                        label: _t(label),
                        isExternal: false,
                        isUrlEditable: false,
                    };
                },
                urlRepresentation(url) {
                    const actionDescription = parseViewLink(url);
                    return actionDescription.name;
                },
                async open(url, env) {
                    const { viewType, action, name } = parseViewLink(url);
                    await navigateTo(env, action.xmlId,
                        {
                            type: "ir.actions.act_window",
                            name: name,
                            res_model: action.modelName,
                            views: action.views,
                            target: "current",
                            domain: action.domain,
                            context: action.context,
                        },
                        { viewType }
                    );
                },
            });

        return true;
    },
};

registry.category("services").add("spreadsheetLinkMenuCell", spreadsheetLinkMenuCellService);

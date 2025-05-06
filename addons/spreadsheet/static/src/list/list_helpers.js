/** @orj-module */
// @ts-check

import { helpers } from "@orj/o-spreadsheet";

const { getFunctionsFromTokens } = helpers;

/** @typedef {import("@orj/o-spreadsheet").Token} Token */

/**
 * Parse a spreadsheet formula and detect the number of LIST functions that are
 * present in the given formula.
 *
 * @param {Token[]} tokens
 *
 * @returns {number}
 */
export function getNumberOfListFormulas(tokens) {
    return getFunctionsFromTokens(tokens, ["ORJ.LIST", "ORJ.LIST.HEADER"]).length;
}

/**
 * Get the first List function description of the given formula.
 *
 * @param {Token[]} tokens
 *
 * @returns {import("../helpers/orj_functions_helpers").OrjFunctionDescription|undefined}
 */
export function getFirstListFunction(tokens) {
    return getFunctionsFromTokens(tokens, ["ORJ.LIST", "ORJ.LIST.HEADER"])[0];
}

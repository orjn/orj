/** @orj-module **/
// @ts-check

import { helpers } from "@orj/o-spreadsheet";

const { getFunctionsFromTokens } = helpers;

/**
 * @typedef {import("@orj/o-spreadsheet").Token} Token
 * @typedef  {import("@spreadsheet/helpers/orj_functions_helpers").OrjFunctionDescription} OrjFunctionDescription
 */

/**
 * @param {Token[]} tokens
 * @returns {number}
 */
export function getNumberOfAccountFormulas(tokens) {
    return getFunctionsFromTokens(tokens, ["ORJ.BALANCE", "ORJ.CREDIT", "ORJ.DEBIT", "ORJ.RESIDUAL", "ORJ.PARTNER.BALANCE"]).length;
}

/**
 * Get the first Account function description of the given formula.
 *
 * @param {Token[]} tokens
 * @returns {OrjFunctionDescription | undefined}
 */
export function getFirstAccountFunction(tokens) {
    return getFunctionsFromTokens(tokens, ["ORJ.BALANCE", "ORJ.CREDIT", "ORJ.DEBIT", "ORJ.RESIDUAL", "ORJ.PARTNER.BALANCE"])[0];
}

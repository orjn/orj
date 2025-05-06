/** @orj-module */

import { helpers } from "@orj/o-spreadsheet";

const { toUnboundedZone } = helpers;

export function toRangeData(sheetId, xc) {
    return { _zone: toUnboundedZone(xc), _sheetId: sheetId };
}

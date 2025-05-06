import { SpreadsheetChildEnv as SSChildEnv } from "@orj/o-spreadsheet";
import { Services } from "services";

declare module "@spreadsheet" {
    import { Model } from "@orj/o-spreadsheet";

    export interface SpreadsheetChildEnv extends SSChildEnv {
        model: OrjSpreadsheetModel;
        services: Services;
    }
}

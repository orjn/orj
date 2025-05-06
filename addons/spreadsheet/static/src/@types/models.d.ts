declare module "@spreadsheet" {
    import { Model } from "@orj/o-spreadsheet";

    export interface OrjSpreadsheetModel extends Model {
        getters: OrjGetters;
        dispatch: OrjDispatch;
    }

    export interface OrjSpreadsheetModelConstructor {
        new (
            data: object,
            config: Partial<Model["config"]>,
            revisions: object[]
        ): OrjSpreadsheetModel;
    }
}

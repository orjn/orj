declare module "@spreadsheet" {
    import { CommandResult, CorePlugin, UIPlugin } from "@orj/o-spreadsheet";
    import { CommandResult as CR } from "@spreadsheet/o_spreadsheet/cancelled_reason";
    type OrjCommandResult = CommandResult | typeof CR;

    export interface OrjCorePlugin extends CorePlugin {
        getters: OrjCoreGetters;
        dispatch: OrjCoreDispatch;
        allowDispatch(command: AllCoreCommand): string | string[];
        beforeHandle(command: AllCoreCommand): void;
        handle(command: AllCoreCommand): void;
    }

    export interface OrjCorePluginConstructor {
        new (config: unknown): OrjCorePlugin;
    }

    export interface OrjUIPlugin extends UIPlugin {
        getters: OrjGetters;
        dispatch: OrjDispatch;
        allowDispatch(command: AllCommand): string | string[];
        beforeHandle(command: AllCommand): void;
        handle(command: AllCommand): void;
    }

    export interface OrjUIPluginConstructor {
        new (config: unknown): OrjUIPlugin;
    }
}

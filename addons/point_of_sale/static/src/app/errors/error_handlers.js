import { registry } from "@web/core/registry";
import { orjExceptionTitleMap, ErrorDialog } from "@web/core/errors/error_dialogs";
import { ConnectionLostError, RPCError } from "@web/core/network/rpc";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

export function handleRPCError(error, dialog) {
    const { data } = error;
    if (orjExceptionTitleMap.has(error.exceptionName)) {
        const title = orjExceptionTitleMap.get(error.exceptionName).toString();
        dialog.add(AlertDialog, { title, body: data.message });
    } else {
        if (orj.debug === "assets") {
            dialog.add(ErrorDialog, {
                traceback: data.message + "\n" + data.debug + "\n",
            });
        } else {
            dialog.add(AlertDialog, {
                title: _t("Orj Server Error"),
                body: data.message,
            });
        }
    }
}

function rpcErrorHandler(env, error, originalError) {
    if (originalError instanceof RPCError) {
        handleRPCError(originalError, env.services.dialog);
        return true;
    }
}
registry.category("error_handlers").add("rpcErrorHandler", rpcErrorHandler);

export function offlineErrorHandler(env, error, originalError) {
    if (originalError instanceof ConnectionLostError) {
        if (!env.services.pos.data.network.warningTriggered) {
            env.services.dialog.add(AlertDialog, {
                title: _t("Connection Lost"),
                body: _t(
                    "Until the connection is reestablished, Orj Point of Sale will operate with limited functionality."
                ),
                confirmLabel: _t("Continue with limited functionality"),
            });
            env.services.pos.data.network.warningTriggered = true;
        }

        return true;
    }
}
registry.category("error_handlers").add("offlineErrorHandler", offlineErrorHandler);

function defaultErrorHandler(env, error, originalError) {
    if (error instanceof Error) {
        env.services.dialog.add(ErrorDialog, {
            traceback: error.traceback,
        });
    } else {
        env.services.dialog.add(AlertDialog, {
            title: _t("Unknown Error"),
            body: _t("Unable to show information about this error."),
        });
    }
    return true;
}
registry
    .category("error_handlers")
    .add("defaultErrorHandler", defaultErrorHandler, { sequence: 99 });

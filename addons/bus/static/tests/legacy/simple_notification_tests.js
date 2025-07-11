/** @orj-module alias=@bus/../tests/simple_notification_tests default=false */

import { simpleNotificationService } from "@bus/simple_notification_service";
import { addBusServicesToRegistry } from "@bus/../tests/helpers/test_utils";
import { startServer } from "@bus/../tests/helpers/mock_python_environment";

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { patchWithCleanup } from "@web/../tests/helpers/utils";
import { contains } from "@web/../tests/utils";
import { createWebClient } from "@web/../tests/webclient/helpers";

QUnit.module("simple_notification");

QUnit.test("receive and display simple notification with message", async () => {
    const pyEnv = await startServer();
    addBusServicesToRegistry();
    registry.category("services").add("simple_notification", simpleNotificationService);
    await createWebClient({});
    pyEnv["bus.bus"]._sendone(pyEnv.currentPartner, "simple_notification", {
        message: "simple notification",
    });
    await contains(".o_notification_content", { text: "simple notification" });
});

QUnit.test("receive and display simple notification with title", async () => {
    const pyEnv = await startServer();
    addBusServicesToRegistry();
    registry.category("services").add("simple_notification", simpleNotificationService);
    await createWebClient({});
    pyEnv["bus.bus"]._sendone(pyEnv.currentPartner, "simple_notification", {
        message: "simple notification",
        title: "simple title",
    });
    await contains(".o_notification_title", { text: "simple title" });
});

QUnit.test("receive and display simple notification with specific type", async () => {
    const pyEnv = await startServer();
    addBusServicesToRegistry();
    registry.category("services").add("simple_notification", simpleNotificationService);
    await createWebClient({});
    pyEnv["bus.bus"]._sendone(pyEnv.currentPartner, "simple_notification", {
        message: "simple notification",
        type: "info",
    });
    await contains(".o_notification:has(.o_notification_bar.bg-info)");
});

QUnit.test("receive and display simple notification as sticky", async () => {
    const pyEnv = await startServer();
    addBusServicesToRegistry();
    registry.category("services").add("simple_notification", simpleNotificationService);
    await createWebClient({});
    patchWithCleanup(browser, {
        setTimeout(fn) {
            /**
             * Non-sticky notifications are removed after a delay. If thenotification is still
             * present when this delay is set to 0 it means it is a sticky one.
             */
            return super.setTimeout(fn, 0);
        },
    });
    pyEnv["bus.bus"]._sendone(pyEnv.currentPartner, "simple_notification", {
        message: "simple notification",
        sticky: true,
    });
    await contains(".o_notification");
});

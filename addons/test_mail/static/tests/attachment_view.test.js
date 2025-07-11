import { defineTestMailModels } from "@test_mail/../tests/test_mail_test_helpers";
import { beforeEach, describe, test, expect } from "@orj/hoot";
import { queryOne, waitUntil } from "@orj/hoot-dom";
import { animationFrame } from "@orj/hoot-mock";
import {
    click,
    contains,
    openFormView,
    registerArchs,
    start,
    startServer,
    patchUiSize,
    SIZES,
    dragenterFiles,
    dropFiles,
} from "@mail/../tests/mail_test_helpers";
import { browser } from "@web/core/browser/browser";
import { patchWithCleanup } from "@web/../tests/web_test_helpers";

describe.current.tags("desktop");
defineTestMailModels();

let popoutIframe, popoutWindow;

beforeEach(() => {
    popoutIframe = document.createElement("iframe");
    popoutWindow = {
        closed: false,
        get document() {
            const doc = popoutIframe.contentDocument;
            if (!doc) {
                return undefined;
            }
            const originalWrite = doc.write;
            doc.write = (content) => {
                // This avoids duplicating the test script in the popoutWindow
                const sanitizedContent = content.replace(
                    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
                    ""
                );
                originalWrite.call(doc, sanitizedContent);
            };
            return doc;
        },
        close: () => {
            popoutWindow.closed = true;
            popoutIframe.remove(popoutAttachmentViewBody());
        },
    };
});

patchWithCleanup(browser, {
    open: () => {
        popoutWindow.closed = false;
        queryOne(".o_popout_holder").append(popoutIframe);
        return popoutWindow;
    },
});

function popoutAttachmentViewBody() {
    return popoutWindow.document.querySelector(".o-mail-PopoutAttachmentView");
}
async function popoutIsEmpty() {
    await animationFrame();
    expect(popoutAttachmentViewBody()).toBe(null);
}
async function popoutContains(selector) {
    await animationFrame();
    await waitUntil(() => popoutAttachmentViewBody());
    const target = popoutAttachmentViewBody().querySelector(selector);
    expect(target).toBeDisplayed();
    return target;
}
async function popoutClick(selector) {
    const target = await popoutContains(selector);
    click(target);
}

test("Attachment view popout controls test", async () => {
    /*
     * This test makes sure that the attachment view controls are working in the following cases:
     * - Inside the popout window
     * - After closing the popout window
     */
    const pyEnv = await startServer();
    const recordId = pyEnv["mail.test.simple.main.attachment"].create({
        display_name: "first partner",
        message_attachment_count: 2,
    });
    pyEnv["ir.attachment"].create([
        {
            mimetype: "image/jpeg",
            res_id: recordId,
            res_model: "mail.test.simple.main.attachment",
        },
        {
            mimetype: "application/pdf",
            res_id: recordId,
            res_model: "mail.test.simple.main.attachment",
        },
    ]);
    registerArchs({
        "mail.test.simple.main.attachment,false,form": `
                <form string="Test document">
                    <div class="o_popout_holder"/>
                    <sheet>
                        <field name="name"/>
                    </sheet>
                    <div class="o_attachment_preview"/>
                    <chatter/>
                </form>`,
    });

    patchUiSize({ size: SIZES.XXL });
    await start();
    await openFormView("mail.test.simple.main.attachment", recordId);
    await click(".o_attachment_preview .o_attachment_control");
    await animationFrame();
    expect(".o_attachment_preview").not.toBeVisible();
    await popoutClick(".o_move_next");
    await popoutContains("img");
    await popoutClick(".o_move_previous");
    await popoutContains("iframe");
    popoutWindow.close();
    await contains(".o_attachment_preview:not(.d-none)");
    expect(".o_attachment_preview").toBeVisible();
    await click(".o_attachment_preview .o_move_next");
    await contains(".o_attachment_preview img");
    await click(".o_attachment_preview .o_move_previous");
    await contains(".o_attachment_preview iframe");
    await click(".o_attachment_preview .o_attachment_control");
    await animationFrame();
    expect(".o_attachment_preview").not.toBeVisible();
});

test("Chatter main attachment: can change from non-viewable to viewable", async () => {
    const pyEnv = await startServer();
    const recordId = pyEnv['mail.test.simple.main.attachment'].create({});
    const irAttachmentId = pyEnv['ir.attachment'].create({
        mimetype: 'text/plain',
        name: "Blah.txt",
        res_id: recordId,
        res_model: 'mail.test.simple.main.attachment',
    });
    pyEnv['mail.message'].create({
        attachment_ids: [irAttachmentId],
        model: 'mail.test.simple.main.attachment',
        res_id: recordId,
    });
    pyEnv['mail.test.simple.main.attachment'].write([recordId], {message_main_attachment_id : irAttachmentId});

    registerArchs({
        "mail.test.simple.main.attachment,false,form": `
            <form string="Test document">
                <sheet>
                    <field name="name"/>
                </sheet>
                <div class="o_attachment_preview"/>
                <chatter/>
            </form>`,
    });
    patchUiSize({ size: SIZES.XXL });
    await start();
    await openFormView("mail.test.simple.main.attachment", recordId);

    // Add a PDF file
    const pdfFile = new File([new Uint8Array(1)], "text.pdf", { type: "application/pdf" });
    await dragenterFiles(".o-mail-Chatter", [pdfFile]);
    await dropFiles(".o-Dropzone", [pdfFile]);
    await contains(".o_attachment_preview");
    await contains(".o-mail-Attachment > iframe", { count: 0 }); // The viewer tries to display the text file not the PDF

    // Switch to the PDF file in the viewer
    await click(".o_move_next");
    await contains(".o-mail-Attachment > iframe"); // There should be iframe for PDF viewer
});

test.skip("Attachment view / chatter popout across multiple records test", async () => {
    // skip because test has race conditions: https://runbot.orj.net/orj/runbot.build.error/109795
    const pyEnv = await startServer();
    const recordIds = pyEnv["mail.test.simple.main.attachment"].create([
        {
            display_name: "first partner",
            message_attachment_count: 1,
        },
        {
            display_name: "second partner",
            message_attachment_count: 0,
        },
        {
            display_name: "third partner",
            message_attachment_count: 1,
        },
    ]);
    pyEnv["ir.attachment"].create([
        {
            mimetype: "image/jpeg",
            res_id: recordIds[0],
            res_model: "mail.test.simple.main.attachment",
        },
        {
            mimetype: "application/pdf",
            res_id: recordIds[2],
            res_model: "mail.test.simple.main.attachment",
        },
    ]);
    registerArchs({
        "mail.test.simple.main.attachment,false,form": `
                <form string="Test document">
                    <div class="o_popout_holder"/>
                    <sheet>
                        <field name="name"/>
                    </sheet>
                    <div class="o_attachment_preview"/>
                    <chatter/>
                </form>`,
    });

    async function navigateRecords() {
        /**
         * It should be called on the first record of recordIds
         * The popout window should be open
         * It navigates recordIds as 0 -> 1 -> 2 -> 0 -> 2
         */
        await animationFrame();
        expect(".o_attachment_preview").not.toBeVisible();
        await popoutContains("img");
        await click(".o_pager_next");
        await popoutIsEmpty();
        await click(".o_pager_next");
        await popoutContains("iframe");
        await click(".o_pager_next");
        await popoutContains("img");
        await click(".o_pager_previous");
        await popoutContains("iframe");
        popoutWindow.close();
        await contains(".o_attachment_preview:not(.d-none)");
    }

    patchUiSize({ size: SIZES.XXL });
    await start();
    await openFormView("mail.test.simple.main.attachment", recordIds[0], {
        resIds: recordIds,
    });
    await click(".o_attachment_preview .o_attachment_control");
    await navigateRecords();
    await openFormView("mail.test.simple.main.attachment", recordIds[0], {
        resIds: recordIds,
    });
    await click("button i[title='Pop out Attachments']");
    await navigateRecords();
});

import { expect, test } from "@orj/hoot";
import { press } from "@orj/hoot-dom";
import { animationFrame, tick } from "@orj/hoot-mock";
import { defineModels, fields, models, serverState } from "@web/../tests/web_test_helpers";
import { setupEditor } from "./_helpers/editor";
import { getContent } from "./_helpers/selection";
import { insertText, undo } from "./_helpers/user_actions";
class ResUsers extends models.Model {
    _name = "res.users";

    signature = fields.Html();
    _records = [
        {
            id: serverState.userId,
            signature: "<h1>Hello</h1>",
        },
    ];
}
defineModels([ResUsers]);

test("apply 'Signature' command", async () => {
    const { el, editor } = await setupEditor("<p>ab[]cd</p>");
    await insertText(editor, "/signature");
    await animationFrame();
    expect(".active .o-we-command-name").toHaveText("Signature");

    await press("enter");
    await tick();
    expect(getContent(el)).toBe(
        `<p>ab</p><div class="o-signature-container"><h1>Hello[]</h1></div><p>cd</p>`
    );
});

test("undo a 'Signature' command", async () => {
    const { el, editor } = await setupEditor("<p>ab[]cd</p>");
    await insertText(editor, "test");
    await insertText(editor, "/signature");
    await press("enter");
    await tick();
    expect(getContent(el)).toBe(
        `<p>abtest</p><div class="o-signature-container"><h1>Hello[]</h1></div><p>cd</p>`
    );

    undo(editor);
    expect(getContent(el)).toBe("<p>abtest[]cd</p>");
});

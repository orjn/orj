/** @orj-module alias=@web/../tests/mobile/views/fields/many2one_barcode_field_tests default=false */

import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { browser } from "@web/core/browser/browser";
import { click, clickSave, getFixture, patchWithCleanup } from "@web/../tests/helpers/utils";
import { makeView, setupViewRegistries } from "@web/../tests/views/helpers";

import * as BarcodeScanner from "@web/core/barcode/barcode_dialog";

let serverData;
let target;

const NAME_SEARCH = "name_search";
const PRODUCT_PRODUCT = "product.product";
const SALE_ORDER_LINE = "sale_order_line";
const PRODUCT_FIELD_NAME = "product_id";

// MockRPC to allow the search in barcode too
async function barcodeMockRPC(route, args, performRPC) {
    if (args.method === NAME_SEARCH && args.model === PRODUCT_PRODUCT) {
        const result = await performRPC(route, args);
        const records = serverData.models[PRODUCT_PRODUCT].records
            .filter((record) => record.barcode === args.kwargs.name)
            .map((record) => [record.id, record.name]);
        return records.concat(result);
    }
}

QUnit.module("Fields", (hooks) => {
    hooks.beforeEach(() => {
        target = getFixture();
        serverData = {
            models: {
                [PRODUCT_PRODUCT]: {
                    fields: {
                        id: { type: "integer" },
                        name: {},
                        barcode: {},
                    },
                    records: [
                        {
                            id: 111,
                            name: "product_cable_management_box",
                            barcode: "601647855631",
                        },
                        {
                            id: 112,
                            name: "product_n95_mask",
                            barcode: "601647855632",
                        },
                        {
                            id: 113,
                            name: "product_surgical_mask",
                            barcode: "601647855633",
                        },
                    ],
                },
                [SALE_ORDER_LINE]: {
                    fields: {
                        id: { type: "integer" },
                        [PRODUCT_FIELD_NAME]: {
                            string: PRODUCT_FIELD_NAME,
                            type: "many2one",
                            relation: PRODUCT_PRODUCT,
                        },
                    },
                },
            },
            views: {
                "product.product,false,kanban": `
                    <kanban><templates><t t-name="card">
                        <field name="id"/>
                        <field name="name"/>
                        <field name="barcode"/>
                    </t></templates></kanban>
                `,
                "product.product,false,search": "<search></search>",
            },
        };

        setupViewRegistries();

        patchWithCleanup(AutoComplete, {
            delay: 0,
        });

        // simulate a environment with a camera/webcam
        patchWithCleanup(
            browser,
            Object.assign({}, browser, {
                setTimeout: (fn) => fn(),
                navigator: {
                    userAgent: "Chrome/0.0.0 (Linux; Android 13; Orj TestSuite)",
                    mediaDevices: {
                        getUserMedia: () => [],
                    },
                },
            })
        );
    });

    QUnit.module("Many2OneField Barcode (Small)");

    QUnit.test("barcode button with multiple results", async function (assert) {
        assert.expect(4);

        // The product selected (mock) for the barcode scanner
        const selectedRecordTest = serverData.models[PRODUCT_PRODUCT].records[1];

        patchWithCleanup(BarcodeScanner, {
            scanBarcode: async () => "mask",
        });

        await makeView({
            type: "form",
            resModel: SALE_ORDER_LINE,
            serverData,
            arch: `
                <form>
                    <field name="${PRODUCT_FIELD_NAME}" options="{'can_scan_barcode': True}"/>
                </form>`,
            async mockRPC(route, args, performRPC) {
                if (args.method === "web_save" && args.model === SALE_ORDER_LINE) {
                    const selectedId = args.args[1][PRODUCT_FIELD_NAME];
                    assert.equal(
                        selectedId,
                        selectedRecordTest.id,
                        `product id selected ${selectedId}, should be ${selectedRecordTest.id} (${selectedRecordTest.barcode})`
                    );
                    return performRPC(route, args, performRPC);
                }
                return barcodeMockRPC(route, args, performRPC);
            },
        });

        const scanButton = target.querySelector(".o_barcode");
        assert.containsOnce(target, scanButton, "has scanner barcode button");

        await click(target, ".o_barcode");

        const modal = target.querySelector(".modal-dialog.modal-lg");
        assert.containsOnce(target, modal, "there should be one modal opened in full screen");

        assert.containsN(
            modal,
            ".o_kanban_record:not(.o_kanban_ghost)",
            2,
            "there should be 2 records displayed"
        );

        await click(modal, ".o_kanban_record:nth-child(1)");
        await clickSave(target);
    });

    QUnit.test("many2one with barcode show all records", async function (assert) {
        // The product selected (mock) for the barcode scanner
        const selectedRecordTest = serverData.models[PRODUCT_PRODUCT].records[0];

        patchWithCleanup(BarcodeScanner, {
            scanBarcode: async () => selectedRecordTest.barcode,
        });

        await makeView({
            type: "form",
            resModel: SALE_ORDER_LINE,
            serverData,
            arch: `
                <form>
                    <field name="${PRODUCT_FIELD_NAME}" options="{'can_scan_barcode': True}"/>
                </form>`,
            mockRPC: barcodeMockRPC,
        });

        // Select one product
        await click(target, ".o_barcode");

        // Click on the input to show all records
        await click(target, ".o_input_dropdown > input");

        const modal = target.querySelector(".modal-dialog.modal-lg");
        assert.containsOnce(target, modal, "there should be one modal opened in full screen");

        assert.containsN(
            modal,
            ".o_kanban_record:not(.o_kanban_ghost)",
            3,
            "there should be 3 records displayed"
        );
    });
});

import { describe, expect, test } from "@orj/hoot";
import { setCellContent } from "@spreadsheet/../tests/helpers/commands";
import { getCellValue, getEvaluatedCell } from "@spreadsheet/../tests/helpers/getters";
import { createModelWithDataSource } from "@spreadsheet/../tests/helpers/model";
import {
    defineSpreadsheetAccountModels,
} from "@spreadsheet_account/../tests/accounting_test_data";
import { waitForDataLoaded } from "@spreadsheet/helpers/model";

describe.current.tags("headless");
defineSpreadsheetAccountModels();

test("Basic evaluation", async () => {
    const model = await createModelWithDataSource({
        mockRPC: async function (route, args) {
            if (args.method === "spreadsheet_fetch_partner_balance") {
                expect.step("spreadsheet_fetch_partner_balance");
                expect(args.args[0]).toEqual([
                    {
                        partner_ids: [
                            14, 16
                        ],
                        codes: [
                            "112",
                        ],
                        date_range: {
                            range_type: "year",
                            year: 2023,
                        },
                        company_id: 0,
                        include_unposted: false,
                    },
                ]);
                return [{ balance: 26 }];
            }
        },
    });
    setCellContent(model, "A1", `=ORJ.PARTNER.BALANCE("14, 16", "112", 2023)`);
    await waitForDataLoaded(model);
    expect.verifySteps(["spreadsheet_fetch_partner_balance"]);
    expect(getCellValue(model, "A1")).toBe(26);
});

test("with wrong date format", async () => {
    const model = await createModelWithDataSource();
    setCellContent(model, "A1", `=ORJ.PARTNER.BALANCE("14, 16", "112", "This is not a valid date")`);
    await waitForDataLoaded(model);
    expect(getEvaluatedCell(model, "A1").message).toBe(
        "'This is not a valid date' is not a valid period. Supported formats are \"21/12/2022\", \"Q1/2022\", \"12/2022\", and \"2022\"."
    );
});

test("with no date", async () => {
    const model = await createModelWithDataSource({
        mockRPC: async function (route, args) {
            if (args.method === "spreadsheet_fetch_partner_balance") {
                expect.step("spreadsheet_fetch_partner_balance");
                expect(args.args[0]).toEqual([
                    {
                        partner_ids: [
                            14, 16
                        ],
                        codes: [
                            "112",
                        ],
                        date_range: {
                            range_type: "year",
                            year: new Date().getFullYear(),
                        },
                        company_id: 0,
                        include_unposted: false,
                    },
                ]);
                return [{ balance: 26 }];
            }
        },
    });
    setCellContent(model, "A1", `=ORJ.PARTNER.BALANCE("14, 16", "112")`);
    await waitForDataLoaded(model);
    expect.verifySteps(["spreadsheet_fetch_partner_balance"]);
    expect(getCellValue(model, "A1")).toBe(26);
});

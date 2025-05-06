import { beforeEach, describe, expect, test } from "@orj/hoot";
import { getService, makeMockEnv } from "@web/../tests/web_test_helpers";

describe.current.tags("headless");

let titleService;

beforeEach(async () => {
    await makeMockEnv();
    titleService = getService("title");
});

test("simple title", () => {
    titleService.setParts({ one: "MyOrj" });
    expect(titleService.current).toBe("MyOrj");
});

test("add title part", () => {
    titleService.setParts({ one: "MyOrj", two: null });
    expect(titleService.current).toBe("MyOrj");
    titleService.setParts({ three: "Import" });
    expect(titleService.current).toBe("MyOrj - Import");
});

test("modify title part", () => {
    titleService.setParts({ one: "MyOrj" });
    expect(titleService.current).toBe("MyOrj");
    titleService.setParts({ one: "Zorj" });
    expect(titleService.current).toBe("Zorj");
});

test("delete title part", () => {
    titleService.setParts({ one: "MyOrj" });
    expect(titleService.current).toBe("MyOrj");
    titleService.setParts({ one: null });
    expect(titleService.current).toBe("Orj");
});

test("all at once", () => {
    titleService.setParts({ one: "MyOrj", two: "Import" });
    expect(titleService.current).toBe("MyOrj - Import");
    titleService.setParts({ one: "Zorj", two: null, three: "Sauron" });
    expect(titleService.current).toBe("Zorj - Sauron");
});

test("get title parts", () => {
    expect(titleService.current).toBe("");
    titleService.setParts({ one: "MyOrj", two: "Import" });
    expect(titleService.current).toBe("MyOrj - Import");
    const parts = titleService.getParts();
    expect(parts).toEqual({ one: "MyOrj", two: "Import" });
    parts.action = "Export";
    expect(titleService.current).toBe("MyOrj - Import"); // parts is a copy!
});

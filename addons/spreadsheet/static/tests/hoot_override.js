import { __debug__ } from "@orj/hoot";
import { stores } from "@orj/o-spreadsheet";
import { patch } from "@web/core/utils/patch";

const { RendererStore } = stores;

/**
 * When rendering a spreadsheet, drawing the grid in a canvas is a costly operation,
 * perhaps the most costly operation. This patch allows to skip the grid/canvas drawing
 * in standard tests, which speeds up the overall execution.
 *
 * For debugging urpose, the patch is ineffective when running tests in debug mode
 * and the grid is drawn as usual.
 */
patch(RendererStore.prototype, {
    drawLayer(ctx, layer) {
        if (__debug__.debug) {
            return super.drawLayer(ctx, layer);
        }
    },
});

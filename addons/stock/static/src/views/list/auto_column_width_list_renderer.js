/** @orj-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { useEffect } from "@orj/owl";

export class AutoColumnWidthListRenderer extends ListRenderer {
    static props = [...ListRenderer.props];
    setup() {
        super.setup();
        useEffect(
            () => {
                this.keepColumnWidths = false;
            },
            () => [this.columns]
        );
    }
}

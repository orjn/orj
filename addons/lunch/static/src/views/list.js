/** @orj-module */

import { registry } from '@web/core/registry';

import { listView } from '@web/views/list/list_view';
import { ListRenderer } from '@web/views/list/list_renderer';

import { LunchDashboard } from '../components/lunch_dashboard';
import { LunchRendererMixin } from '../mixins/lunch_renderer_mixin';

import { LunchSearchModel } from './search_model';


export class LunchListRenderer extends LunchRendererMixin(ListRenderer) {
    static template = "lunch.ListRenderer";
    static components = {
        ...LunchListRenderer.components,
        LunchDashboard,
    };

    setup() {
        super.setup();
        const { locationId } = this.env.searchModel.lunchState;
        if (!locationId) {
            this.props.list.records = [];
        }
    }

    onCellClicked(record, column) {
        this.openOrderLine(record.resId);
    }
}


registry.category('views').add('lunch_list', {
    ...listView,
    Renderer: LunchListRenderer,
    SearchModel: LunchSearchModel,
});

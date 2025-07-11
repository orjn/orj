/** @orj-module **/

import options from '@web_editor/js/editor/snippets.options';

options.registry.SearchBar = options.Class.extend({
    /**
     * @override
     */
    start() {
        this.searchInputEl = this.$target[0].querySelector(".oe_search_box");
        this.searchButtonEl = this.$target[0].querySelector(".oe_search_button");
        return this._super(...arguments);
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    setSearchType: function (previewMode, widgetValue, params) {
        const form = this.$target.parents('form');
        form.attr('action', params.formAction);

        if (!previewMode) {
            this.trigger_up('snippet_edition_request', {exec: () => {
                const widget = this._requestUserValueWidgets('order_opt')[0];
                const orderBy = widget.getValue("selectDataAttribute");
                const order = widget.$el.find("we-button[data-select-data-attribute='" + orderBy + "']")[0];
                if (order.classList.contains("d-none")) {
                    const defaultOrder = widget.$el.find("we-button[data-name='order_name_asc_opt']")[0];
                    defaultOrder.click(); // open
                    defaultOrder.click(); // close
                }
            }});

            // Reset display options.
            const displayOptions = new Set();
            for (const optionEl of this.$el[0].querySelectorAll('[data-dependencies="limit_opt"] [data-attribute-name^="display"]')) {
                displayOptions.add(optionEl.dataset.attributeName);
            }
            const scopeName = this.$el[0].querySelector(`[data-set-search-type="${widgetValue}"]`).dataset.name;
            for (const displayOption of displayOptions) {
                this.$target[0].dataset[displayOption] = this.$el[0].querySelector(
                    `[data-attribute-name="${displayOption}"][data-dependencies="${scopeName}"]`
                ) ? 'true' : '';
            }
        }
    },

    setOrderBy: function (previewMode, widgetValue, params) {
        const form = this.$target.parents('form');
        form.find(".o_search_order_by").attr("value", widgetValue);
    },
    /**
     * Sets the style of the searchbar.
     *
     * @see this.selectClass for parameters
     */
    setSearchbarStyle(previewMode, widgetValue, params) {
        const isLight = (widgetValue === "light");
        this.searchInputEl.classList.toggle("border-0", isLight);
        this.searchInputEl.classList.toggle("bg-light", isLight);
        this.searchButtonEl.classList.toggle("btn-light", isLight);
        this.searchButtonEl.classList.toggle("btn-primary", !isLight);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _computeWidgetState(methodName, params) {
        if (methodName === "setSearchbarStyle") {
            const searchInputIsLight = this.searchInputEl.matches(".border-0.bg-light");
            const searchButtonIsLight = this.searchButtonEl.matches(".btn-light");
            return searchInputIsLight && searchButtonIsLight ? "light" : "default";
        }
        return this._super(...arguments);
    },
});

export default {
    SearchBar: options.registry.SearchBar,
};

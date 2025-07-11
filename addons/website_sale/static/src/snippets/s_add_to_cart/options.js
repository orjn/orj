/** @orj-module **/

import options from '@web_editor/js/editor/snippets.options';
import { _t } from "@web/core/l10n/translation";

options.registry.AddToCart = options.Class.extend({
    events: Object.assign({}, options.Class.prototype.events || {}, {
        'click .reset-variant-picker': '_onClickResetVariantPicker',
        'click .reset-product-picker': '_onClickResetProductPicker',
    }),

    init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
    },

    async updateUI() {
        if (this.rerender) {
            this.rerender = false;
            await this._rerenderXML();
            return;
        }
        return this._super.apply(this, arguments);
    },

    _setButtonDisabled: function (isDisabled) {
        const buttonEl = this._buttonEl();

        if (isDisabled) {
            buttonEl.classList.add('disabled');
        } else {
            buttonEl.classList.remove('disabled');
        }
    },

    async setProductTemplate(previewMode, widgetValue, params) {
        this.$target[0].dataset.productTemplate = widgetValue;
        this._resetVariantChoice();
        this._resetAction();
        this._setButtonDisabled(false);

        await this._fetchProductData(widgetValue);
        this.rerender = true;
        this._updateButton();

    },

    setProductVariant(previewMode, widgetValue, params) {
        this.$target[0].dataset.productVariant = widgetValue;
        this._updateButton();
    },

    setAction(previewMode, widgetValue, params) {
        this.$target[0].dataset.action = widgetValue;
        this._updateButton();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    _onClickResetVariantPicker() {
        this._resetVariantChoice();
        this._resetAction();
        this._updateButton();
    },

    _onClickResetProductPicker() {
        this._resetProductChoice();
        this._resetVariantChoice();
        this._resetAction();
        this._updateButton();
    },

    /**
     * Fetch data about the provided product template from the server.
     *
     * More precisely, this method fetches:
     * - The template's variant ids,
     * - Whether the template is a combo product.
     *
     * @param productTemplateId The id of the product template whose data to fetch.
     */
    async _fetchProductData(productTemplateId) {
        const response = await this.orm.searchRead(
            'product.product',
            [['product_tmpl_id', '=', parseInt(productTemplateId)]],
            ['id', 'type'],
        );
        this.$target[0].dataset.variants = response.map(variant => variant.id);
        // If the template is a combo product, it has only one variant (i.e. `response` has a single
        // item).
        this.$target[0].dataset.isCombo = response.some(variant => variant.type === 'combo');
    },


    _resetProductChoice() {
        this.$target[0].dataset.productTemplate = '';
        this._buttonEl().classList.add('disabled');
    },


    _resetVariantChoice() {
        this.$target[0].dataset.productVariant = '';
    },

    _resetAction: function () {
        this.$target[0].dataset.action = "add_to_cart";
    },

    /**
     * Returns an array of variant ids from the dom
     */
    _variantIds() {
        return this.$target[0].dataset.variants.split(',').map(stringId => parseInt(stringId));
    },

    _buttonEl() {
        const buttonEl = this.$target[0].querySelector('.s_add_to_cart_btn');
        // In case the button was deleted somehow, we rebuild it.
        if (!buttonEl) {
            return this._buildButtonEl();
        }
        return buttonEl;
    },

    _buildButtonEl() {
        const buttonEl = document.createElement('button');
        buttonEl.classList.add("s_add_to_cart_btn", "btn", "btn-secondary", "mb-2");
        this.$target[0].append(buttonEl);
        return buttonEl;
    },

    /**
     * Updates the button's html
     */
    _updateButton() {
        const variantIds = this._variantIds();
        const buttonEl = this._buttonEl();

        buttonEl.dataset.productTemplateId = this.$target[0].dataset.productTemplate;
        // TODO(loti,vcr): we're aware that getting the product id this way is too simplistic, but
        // it mimics the previous logic. We'll fix this later on.
        buttonEl.dataset.productVariantId =
            variantIds.length > 1 ? this.$target[0].dataset.productVariant : variantIds[0];
        buttonEl.dataset.isCombo = this.$target[0].dataset.isCombo;
        buttonEl.dataset.action = this.$target[0].dataset.action;
        this._updateButtonContent();
    },

    _updateButtonContent() {
        let iconEl = document.createElement('i');
        const buttonContent = {
            add_to_cart: {classList: "fa fa-cart-plus me-2", text: _t("Add to Cart")},
            buy_now: {classList: "fa fa-credit-card me-2", text: _t("Buy now")},
        };
        let buttonContentElement = buttonContent[this.$target[0].dataset.action];

        iconEl.classList = buttonContentElement.classList;

        this._buttonEl().replaceChildren(iconEl, buttonContentElement.text);
    },

    /**
     * Called when the template is chosen and that we want to update the m2o variant widget with the right variants.
     */
    async _renderCustomXML(uiFragment) {
        if (this.$target[0].dataset.productTemplate) {
            // That means that a template was selected and we want to update the content of the variant picker based on the template id
            const productVariantPickerEl = uiFragment.querySelector('we-many2one[data-name="product_variant_picker_opt"]');
            productVariantPickerEl.dataset.domain = `[["product_tmpl_id", "=", ${this.$target[0].dataset.productTemplate}]]`;
        }
    },

    /**
     * @override
     */
    _computeWidgetState(methodName, params) {
        switch (methodName) {
            case 'setProductTemplate': {
                return this.$target[0].dataset.productTemplate || '';
            }
            case 'setProductVariant': {
                return this.$target[0].dataset.productVariant || '';
            }
            case 'setAction': {
                return this.$target[0].dataset.action;
            }
        }
        return this._super(...arguments);
    },

    /**
     * @override
     */
    async _computeWidgetVisibility(widgetName, params) {
        switch (widgetName) {
            case 'product_variant_picker_opt': {
                return this.$target[0].dataset.productTemplate && this._variantIds().length > 1;
            }
            case 'product_variant_reset_opt': {
                return this.$target[0].dataset.productVariant;
            }

            case 'product_template_reset_opt': {
                return this.$target[0].dataset.productTemplate;
            }
            case 'action_picker_opt': {
                if (this.$target[0].dataset.productTemplate) {
                    if (this._variantIds().length > 1) {
                        return this.$target[0].dataset.productVariant;
                    }
                    return true;
                }
                return false;
            }
        }
        return this._super(...arguments);
    },
});
export default {
    AddToCart: options.registry.AddToCart,
};

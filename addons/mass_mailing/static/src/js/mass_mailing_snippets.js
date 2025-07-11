/** @orj-module **/

import options from "@web_editor/js/editor/snippets.options";
import { loadImage } from "@web_editor/js/editor/image_processing";
const SelectUserValueWidget = options.userValueWidgetsRegistry['we-select'];
import weUtils from "@web_editor/js/common/utils";
import {
    CSS_PREFIX, BTN_SIZE_STYLES,
    DEFAULT_BUTTON_SIZE, PRIORITY_STYLES, FONT_FAMILIES,
    getFontName, normalizeFontFamily, initializeDesignTabCss,
    transformFontFamilySelector,
} from "@mass_mailing/js/mass_mailing_design_constants";
import { isCSSColor, normalizeCSSColor } from "@web/core/utils/colors";


//--------------------------------------------------------------------------
// Options
//--------------------------------------------------------------------------

// Adding compatibility for the outlook compliance of mailings.
// Commit of such compatibility : a14f89c8663c9cafecb1cc26918055e023ecbe42
options.registry.MassMailingBackgroundImage = options.registry.BackgroundImage.extend({
    start: function () {
        this._super();
        const $table_target = this.$target.find('table:first');
        if ($table_target.length) {
            this.$target = $table_target;
        }
    }
});

options.registry.MassMailingImageTools = options.registry.ImageTools.extend({

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _getCSSColorValue(color) {
        if (!color || isCSSColor(color)) {
            return color;
        }
        const doc = this.options.document;
        const tempEl = doc.body.appendChild(doc.createElement('div'));
        tempEl.className = `bg-${color}`;
        const colorValue = window.getComputedStyle(tempEl).getPropertyValue("background-color").trim();
        tempEl.parentNode.removeChild(tempEl);
        return normalizeCSSColor(colorValue).replace(/"/g, "'");
    },

    /**
     * @override
     */
    async computeShape(svgText, img) {
        const dataURL = await this._super(...arguments);
        const image = await loadImage(dataURL);
        const canvas = document.createElement("canvas");
        const imgFilename = (img.dataset.originalSrc.split("/").pop()).split(".")[0];
        img.dataset.fileName = `${imgFilename}.png`;
        img.dataset.mimetype = "image/png";
        canvas.width = image.width;
        canvas.height = image.height;
        canvas.getContext("2d").drawImage(image, 0, 0, image.width, image.height);
        return canvas.toDataURL(`image/png`, 1.0);
    }
});

options.userValueWidgetsRegistry['we-fontfamilypicker'] = SelectUserValueWidget.extend({
    /**
     * @override
     * @see FONT_FAMILIES
     */
    start: async function () {
        const res = await this._super(...arguments);
        // Populate the `we-select` with the font family buttons
        for (const fontFamily of FONT_FAMILIES) {
            const button = document.createElement('we-button');
            button.style.setProperty('font-family', fontFamily);
            button.dataset.customizeCssProperty = fontFamily;
            button.dataset.cssProperty = 'font-family';
            button.dataset.selectorText = this.el.dataset.selectorText;
            button.textContent = getFontName(fontFamily);
            this.menuEl.appendChild(button);
        };
        return res;
    },
});

options.registry.DesignTab = options.Class.extend({
    /**
     * @override
     */
    init() {
        this._super(...arguments);
        // Set the target on the whole editable so apply-to looks within it.
        this.setTarget(this.options.wysiwyg.getEditable());
    },
    /**
     * @override
     */
    async start() {
        const res = await this._super(...arguments);
        const $editable = this.options.wysiwyg.getEditable();
        this.document = $editable[0].ownerDocument;
        this.$layout = $editable.find('.o_layout');
        initializeDesignTabCss($editable);
        this.styleElement = this.document.querySelector('#design-element');
        // When editing a stylesheet, its content is not updated so it won't be
        // saved along with the mailing. Therefore we need to write its cssText
        // into it. However, when doing that we lose its reference. So we need
        // two separate style elements: one that will be saved and one to hold
        // the stylesheet. Both need to be synchronized, which will be done via
        // `_commitCss`.
        let sheetOwner = this.document.querySelector('#sheet-owner');
        if (!sheetOwner) {
            sheetOwner = document.createElement('style');
            sheetOwner.setAttribute('id', 'sheet-owner');
            this.document.head.appendChild(sheetOwner);
        }
        sheetOwner.disabled = true;
        sheetOwner.textContent = this.styleElement.textContent;
        this.styleSheet = sheetOwner.sheet;
        return res;
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Option method to set a css property in the mailing's custom stylesheet.
     * Note: marks all the styles as important to make sure they take precedence
     * on other stylesheets.
     *
     * @param {boolean|string} previewMode
     * @param {string} widgetValue
     * @param {Object} params
     * @param {string} params.selectorText the css selector for which to apply
     *                                     the css
     * @param {string} params.cssProperty the name of the property to edit
     *                                    (camel cased)
     * @param {string} [params.toggle] if 'true', will remove the property if
     *                                 its value is already the one it's being
     *                                 set to
     * @param {string} [params.activeValue] the value to set, if `widgetValue`
     *                                      is not defined.
     * @returns {Promise|undefined}
     */
    customizeCssProperty(previewMode, widgetValue, params) {
        if (!params.selectorText || !params.cssProperty) {
            return;
        }
        let value = widgetValue || params.activeValue;
        if (params.cssProperty.includes('color')) {
            value = weUtils.normalizeColor(value);
        }
        let selectors = this._getSelectors(params.selectorText);
        const firstSelector = selectors[0].replace(CSS_PREFIX, '').trim();
        if (params.cssProperty === 'font-family') {
            // Ensure font-family gets passed to all descendants and never
            // overwrite font awesome.
            const newSelectors = [];
            for (const selector of selectors) {
                newSelectors.push(...transformFontFamilySelector(selector));
            }
            selectors = [...new Set(newSelectors)];
        }
        for (const selector of selectors) {
            const priority = PRIORITY_STYLES[firstSelector].includes(params.cssProperty) ? ' !important' : '';
            const rule = this._getRule(selector);
            if (rule) {
                // The rule exists: update it.
                if (params.toggle === 'true' && rule.style.getPropertyValue(params.cssProperty) === value) {
                    rule.style.removeProperty(params.cssProperty);
                } else {
                    // Convert the style to css text and add the new style (the
                    // `style` property is readonly, we can only edit
                    // `cssText`).
                    const cssTexts = [];
                    for (const style of rule.style) {
                        const ownPriority = rule.style.getPropertyPriority(style) ? ' !important' : '';
                        if (style !== params.cssProperty) {
                            cssTexts.push(`${style}: ${rule.style[style]}${ownPriority};`);
                        }
                    }
                    cssTexts.push(`${params.cssProperty}: ${value}${priority};`);
                    rule.style.cssText = cssTexts.join('\n'); // Apply the new css text.
                }
            } else {
                // The rule doesn't exist: create it.
                this.styleSheet.insertRule(`${selector} {
                    ${params.cssProperty}: ${value}${priority};
                }`);
            }
        }
        this._commitCss();
    },
    /**
     * Option method to change the size of buttons.
     *
     * @see BTN_SIZE_STYLES
     * @param {boolean|string} previewMode
     * @param {string} widgetValue ('btn-sm'|'btn-md'|'btn-lg'|''|undefined)
     * @param {Object} params
     * @returns {Promise|undefined}
     */
     applyButtonSize(previewMode, widgetValue, params) {
        for (const [styleName, styleValue] of Object.entries(BTN_SIZE_STYLES[widgetValue || params.activeValue || DEFAULT_BUTTON_SIZE])) {
            if (styleValue) {
                this.customizeCssProperty(previewMode, styleValue, Object.assign({}, params, { cssProperty: styleName }));
            } else {
                // If the value is falsy, remove the property.
                for (const selector of this._getSelectors(params.selectorText)) {
                    const rule = this._getRule(selector);
                    if (rule) {
                        rule.style.removeProperty(styleName);
                    }
                }
            }
        }
        this._commitCss();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Apply the stylesheet's css text to the style element that will be saved.
     */
    _commitCss() {
        const cssTexts = [];
        for (const rule of this.styleSheet.cssRules || this.styleSheet.rules) {
            cssTexts.push(rule.cssText);
        }
        this.styleElement.textContent = cssTexts.join('\n');
        // Flush the rules cache for convert_inline, to make sure they are
        // recomputed to account for the change.
        this.options.wysiwyg._rulesCache = undefined;
    },
    /**
     * @override
     */
    async _computeWidgetState(methodName, params) {
        const res = await this._super(...arguments);
        if (res === undefined) {
            switch (methodName) {
                case 'applyButtonSize':
                case 'customizeCssProperty': {
                    if (!params.selectorText) {
                        return;
                    }
                    // Here we parse the selector in order to create a matching
                    // element that we inject into the DOM so we can retrieve
                    // its computed style. We then remove the element from the
                    // DOM, no harm, no foul.
                    const firstSelector = params.selectorText.split(',')[0].replace(CSS_PREFIX, '').trim();
                    const classes = firstSelector.replace(/:not\([^\)]*\)/g, '').match(/\.([\w\d-_]+)/g) || [];
                    const fakeElement = document.createElement(firstSelector.split(/[\.:, ]/)[0]);
                    for (const className of classes) {
                        fakeElement.classList.toggle(className.replace('.', ''), true);
                    }
                    this.$layout.find(CSS_PREFIX).prepend(fakeElement);
                    let res;
                    if (methodName === 'applyButtonSize') {
                        // Match a button size by its padding value.
                        const padding = getComputedStyle(fakeElement).padding;
                        const classIndex = Object.values(BTN_SIZE_STYLES).findIndex(style => style.padding === padding);
                        res = classIndex >= 0 ? Object.keys(BTN_SIZE_STYLES)[classIndex] : DEFAULT_BUTTON_SIZE;
                    } else {
                        fakeElement.style.display = 'none'; // Needed to get width in %.
                        res = getComputedStyle(fakeElement)[params.cssProperty || 'font-family'];
                        if (params.possibleValues && params.possibleValues[1] === FONT_FAMILIES[0]) {
                            // For font-family, we need to normalize it so it
                            // matches an option value.
                            res = normalizeFontFamily(res);
                        }
                        if (params.cssProperty === 'font-weight') {
                            res = parseInt(res) >= 600 ? 'bolder' : '';
                        } else if (res === 'auto') {
                            res = '100%';
                        }
                    }
                    fakeElement.remove();
                    return res;
                }
                case 'applyButtonSize':
                    // Match a button size by its padding value.
                    const rule = this._getRule(this._getSelectors(params.selectorText)[0]);
                    if (rule) {
                        const classIndex = Object.values(BTN_SIZE_STYLES).findIndex(style => style.padding === rule.style.padding);
                        return classIndex >= 0 ? Object.keys(BTN_SIZE_STYLES)[classIndex] : DEFAULT_BUTTON_SIZE;
                    } else {
                        return DEFAULT_BUTTON_SIZE;
                    }
            }
        } else {
            return res;
        }
    },
    /**
     * Take a CSS selector and split it into separate selectors, all prefixed
     * with the `CSS_PREFIX`. Return them as an array.
     *
     * @see CSS_PREFIX
     * @param {string} selectorText
     * @returns {string[]}
     */
    _getSelectors(selectorText) {
        return selectorText.split(',').map(t => `${t.startsWith(CSS_PREFIX) ? '' : CSS_PREFIX + ' '}${t.trim()}`.trim());;
    },
    /**
     * Take a CSS selector and find its matching rule in the mailing's custom
     * stylesheet, if it exists.
     *
     * @param {string} selectorText
     * @returns {CSSStyleRule|undefined}
     */
    _getRule(selectorText) {
        return [...(this.styleSheet.cssRules || this.styleSheet.rules)].find(rule => rule.selectorText === selectorText);
    },
});

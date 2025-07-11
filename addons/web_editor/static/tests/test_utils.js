/** @orj-module **/

import { MockServer } from "@web/../tests/helpers/mock_server";
import testUtils from "@web/../tests/legacy_tests/helpers/test_utils";
import { patch } from "@web/core/utils/patch";
import * as OrjEditorLib from "@web_editor/js/editor/orj-editor/src/OrjEditor";
import { Wysiwyg } from '@web_editor/js/wysiwyg/wysiwyg';
import options from "@web_editor/js/editor/snippets.options";
import { TABLE_ATTRIBUTES, TABLE_STYLES } from '@web_editor/js/backend/convert_inline';

export const COLOR_PICKER_TEMPLATE = `
    <colorpicker>
        <div class="o_colorpicker_section" data-name="theme" data-display="Theme Colors" data-icon-class="fa fa-flask">
            <button data-color="o-color-1"/>
            <button data-color="o-color-2"/>
            <button data-color="o-color-3"/>
            <button data-color="o-color-4"/>
            <button data-color="o-color-5"/>
        </div>
        <div class="o_colorpicker_section" data-name="transparent_grayscale" data-display="Transparent Colors" data-icon-class="fa fa-eye-slash">
            <button class="o_btn_transparent"/>
            <button data-color="black-25"/>
            <button data-color="black-50"/>
            <button data-color="black-75"/>
            <button data-color="white-25"/>
            <button data-color="white-50"/>
            <button data-color="white-75"/>
        </div>
        <div class="o_colorpicker_section" data-name="common" data-display="Common Colors" data-icon-class="fa fa-paint-brush">
            <button data-color="black"></button>
            <button data-color="900"></button>
            <button data-color="800"></button>
            <button data-color="700" class="d-none"></button>
            <button data-color="600"></button>
            <button data-color="500" class="d-none"></button>
            <button data-color="400"></button>
            <button data-color="300" class="d-none"></button>
            <button data-color="200"></button>
            <button data-color="100"></button>
            <button data-color="white"></button>
        </div>
    </colorpicker>
`;
const SNIPPETS_TEMPLATE = `
    <snippets id="snippet_structure">
        <div name="Separator" data-oe-type="snippet" data-oe-thumbnail="/web_editor/static/src/img/snippets_thumbs/s_hr.svg">
            <div class="s_hr pt32 pb32">
                <hr class="s_hr_1px s_hr_solid w-100 mx-auto"/>
            </div>
        </div>
        <div name="Content" data-oe-type="snippet" data-oe-thumbnail="/website/static/src/img/snippets_thumbs/s_text_block.png">
            <section name="Content+Options" class="test_option_all pt32 pb32" data-oe-type="snippet" data-oe-thumbnail="/website/static/src/img/snippets_thumbs/s_text_block.png">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-10 offset-lg-1 pt32 pb32">
                            <h2>Title</h2>
                            <p class="lead o_default_snippet_text">Content</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </snippets>
    <div id="snippet_options" class="d-none">
        <div data-js="many2one" data-selector="[data-oe-many2one-model]:not([data-oe-readonly])" data-no-check="true"/>
        <div data-js="content"
            data-selector=".s_hr, .test_option_all"
            data-drop-in=".note-editable"
            data-drop-near="p, h1, h2, h3, blockquote, .s_hr"/>
        <div data-js="sizing_y" data-selector=".s_hr, .test_option_all"/>
        <div data-selector=".test_option_all">
            <we-colorpicker string="Background Color" data-select-style="true" data-css-property="background-color" data-color-prefix="bg-"/>
        </div>
        <div data-js="BackgroundImage" data-selector=".test_option_all">
            <we-button data-choose-image="true" data-no-preview="true">
                <i class="fa fa-picture-o"/> Background Image
            </we-button>
        </div>
        <div data-js="option_test" data-selector=".s_hr">
            <we-select string="Alignment">
                <we-button data-select-class="align-items-start">Top</we-button>
                <we-button data-select-class="align-items-center">Middle</we-button>
                <we-button data-select-class="align-items-end">Bottom</we-button>
                <we-button data-select-class="align-items-stretch">Equal height</we-button>
            </we-select>
        </div>
    </div>`;

patch(MockServer.prototype, {
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     * @returns {Promise}
     */
    async _performRPC(route, args) {
        if (args.model === "ir.ui.view" && args.method === 'render_public_asset') {
            if (args.args[0] === "web_editor.colorpicker") {
                return COLOR_PICKER_TEMPLATE;
            }
            if (args.args[0] === "web_editor.snippets") {
                return SNIPPETS_TEMPLATE;
            }
        }
        if (args.model === "res.lang" && args.method === "get_installed") {
            return [["en_US", "English"]];
        }
        return super._performRPC(...arguments);
    },
});

/**
 * Options with animation and edition for test.
 */
options.registry.option_test = options.Class.extend({
    cleanForSave: function () {
        this.$target.addClass('cleanForSave');
    },
    onBuilt: function () {
        this.$target.addClass('built');
    },
    onBlur: function () {
        this.$target.removeClass('focus');
    },
    onClone: function () {
        this.$target.addClass('clone');
        this.$target.removeClass('focus');
    },
    onFocus: function () {
        this.$target.addClass('focus');
    },
    onMove: function () {
        this.$target.addClass('move');
    },
    onRemove: function () {
        this.$target.closest('.note-editable').addClass('snippet_has_removed');
    },
});

/**
 * @param {object} data
 * @returns {object}
 */
export function wysiwygData(data) {
    return Object.assign({
        'ir.ui.view': {
            fields: {
                display_name: {
                    string: "Displayed name",
                    type: "char",
                },
            },
            records: [],
            render_template(args) {
                if (args[0] === 'web_editor.colorpicker') {
                    return COLOR_PICKER_TEMPLATE;
                }
                if (args[0] === 'web_editor.snippets') {
                    return SNIPPETS_TEMPLATE;
                }
            },
        },
        'ir.attachment': {
            fields: {
                display_name: {
                    string: "display_name",
                    type: 'char',
                },
                description: {
                    string: "description",
                    type: 'char',
                },
                mimetype: {
                    string: "mimetype",
                    type: 'char',
                },
                checksum: {
                    string: "checksum",
                    type: 'char',
                },
                url: {
                    string: "url",
                    type: 'char',
                },
                type: {
                    string: "type",
                    type: 'char',
                },
                res_id: {
                    string: "res_id",
                    type: 'integer',
                },
                res_model: {
                    string: "res_model",
                    type: 'char',
                },
                public: {
                    string: "public",
                    type: 'boolean',
                },
                access_token: {
                    string: "access_token",
                    type: 'char',
                },
                image_src: {
                    string: "image_src",
                    type: 'char',
                },
                image_width: {
                    string: "image_width",
                    type: 'integer',
                },
                image_height: {
                    string: "image_height",
                    type: 'integer',
                },
                original_id: {
                    string: "original_id",
                    type: 'many2one',
                    relation: 'ir.attachment',
                },
            },
            records: [{
                id: 1,
                name: 'image',
                description: '',
                mimetype: 'image/png',
                checksum: false,
                url: '/web/image/123/transparent.png',
                type: 'url',
                res_id: 0,
                res_model: false,
                public: true,
                access_token: false,
                image_src: '/web/image/123/transparent.png',
                image_width: 256,
                image_height: 256,
            }],
            generate_access_token: function () {
                return;
            },
        },
    }, data);
}

/**
 * Perform a series of tests (`keyboardTests`) for using keyboard inputs.
 *
 * @see wysiwyg_keyboard_tests.js
 * @see wysiwyg_tests.js
 *
 * @param {jQuery} $editable
 * @param {object} assert
 * @param {object[]} keyboardTests
 * @param {string} keyboardTests.name
 * @param {string} keyboardTests.content
 * @param {object[]} keyboardTests.steps
 * @param {string} keyboardTests.steps.start
 * @param {string} [keyboardTests.steps.end] default: steps.start
 * @param {string} keyboardTests.steps.key
 * @param {object} keyboardTests.test
 * @param {string} [keyboardTests.test.content]
 * @param {string} [keyboardTests.test.start]
 * @param {string} [keyboardTests.test.end] default: steps.start
 * @param {function($editable, assert)} [keyboardTests.test.check]
 * @param {Number} addTests
 */
var testKeyboard = function ($editable, assert, keyboardTests, addTests) {
    var tests = keyboardTests.map((k) => k.test).map((x) => !!x);
    var testNumber =
        tests.map((test) => test.start).map((x) => !!x).length +
        tests.map((test) => test.content).map((x) => !!x).length +
        tests.map((test) => test.check.map((x) => !!x)).length +
        (addTests | 0);
    assert.expect(testNumber);

    function keydown(target, keypress) {
        var $target = $(target.tagName ? target : target.parentNode);
        var event = $.Event("keydown", keypress);
        $target.trigger(event);

        if (!event.defaultPrevented) {
            if (keypress.key.length === 1) {
                textInput($target[0], keypress.key);
            } else {
                console.warn('Native "' + keypress.key + '" is not supported in test');
            }
        }
        $target.trigger($.Event("keyup", keypress));
        return $target;
    }

    function _select(selector) {
        // eg: ".class:contents()[0]->1" selects the first contents of the 'class' class, with an offset of 1
        var reDOMSelection = /^(.+?)(:contents(\(\)\[|\()([0-9]+)[\]|\)])?(->([0-9]+))?$/;
        var sel = selector.match(reDOMSelection);
        var $node = $editable.find(sel[1]);
        var point = {
            node: sel[3] ? $node.contents()[+sel[4]] : $node[0],
            offset: sel[5] ? +sel[6] : 0,
        };
        if (!point.node || point.offset > (point.node.tagName ? point.node.childNodes : point.node.textContent).length) {
            assert.notOk("Node not found: '" + selector + "' " + (point.node ? "(container: '" + (point.node.outerHTML || point.node.textContent) + "')" : ""));
        }
        return point;
    }

    function selectText(start, end) {
        start = _select(start);
        var target = start.node;
        $(target.tagName ? target : target.parentNode).trigger("mousedown");
        if (end) {
            end = _select(end);
            Wysiwyg.setRange(start.node, start.offset, end.node, end.offset);
        } else {
            Wysiwyg.setRange(start.node, start.offset);
        }
        target = end ? end.node : start.node;
        $(target.tagName ? target : target.parentNode).trigger('mouseup');
    }

    function nextPoint(point) {
        var node, offset;
        if (OrjEditorLib.nodeSize(point.node) === point.offset) {
            node = point.node.parentNode;
            offset = OrjEditorLib.childNodeIndex(point.node) + 1;
        } else if (point.node.hasChildNodes()) {
            node = point.node.childNodes[point.offset];
            offset = 0;
        } else {
            node = point.node;
            offset = point.offset + 1;
        }
        return {
            node: node,
            offset: offset
        };
    }

    function endOfAreaBetweenTwoNodes(point) {
        // move the position because some browser make the caret on the end of the previous area after normalize
        if (
            !point.node.tagName &&
            point.offset === point.node.textContent.length &&
            !/\S|\u00A0/.test(point.node.textContent)
        ) {
            point = nextPoint(nextPoint(point));
            while (point.node.tagName && point.node.textContent.length) {
                point = nextPoint(point);
            }
        }
        return point;
    }

    var defPollTest = Promise.resolve();

    function pollTest(test) {
        var def = Promise.resolve();
        $editable.data('wysiwyg').setValue(test.content);

        function poll(step) {
            var def = testUtils.makeTestPromise();
            if (step.start) {
                selectText(step.start, step.end);
                if (!Wysiwyg.getRange()) {
                    throw 'Wrong range! \n' +
                        'Test: ' + test.name + '\n' +
                        'Selection: ' + step.start + '" to "' + step.end + '"\n' +
                        'DOM: ' + $editable.html();
                }
            }
            setTimeout(function () {
                if (step.key) {
                    var target = Wysiwyg.getRange().ec;
                    if (window.location.search.indexOf('notrycatch') !== -1) {
                        keydown(target, {
                            key: step.key,
                            ctrlKey: !!step.ctrlKey,
                            shiftKey: !!step.shiftKey,
                            altKey: !!step.altKey,
                            metaKey: !!step.metaKey,
                        });
                    } else {
                        try {
                            keydown(target, {
                                key: step.key,
                                ctrlKey: !!step.ctrlKey,
                                shiftKey: !!step.shiftKey,
                                altKey: !!step.altKey,
                                metaKey: !!step.metaKey,
                            });
                        } catch (e) {
                            assert.notOk(e.name + '\n\n' + e.stack, test.name);
                        }
                    }
                }
                setTimeout(function () {
                    if (step.key) {
                        var $target = $(target.tagName ? target : target.parentNode);
                        $target.trigger($.Event('keyup', {
                            key: step.key,
                            ctrlKey: !!step.ctrlKey,
                            shiftKey: !!step.shiftKey,
                            altKey: !!step.altKey,
                            metaKey: !!step.metaKey,
                        }));
                    }
                    setTimeout(def.resolve.bind(def));
                });
            });
            return def;
        }
        while (test.steps.length) {
            def = def.then(poll.bind(null, test.steps.shift()));
        }

        return def.then(function () {
            if (!test.test) {
                return;
            }

            if (test.test.check) {
                test.test.check($editable, assert);
            }

            // test content
            if (test.test.content) {
                var value = $editable.data('wysiwyg').getValue({
                    keepPopover: true,
                });
                var allInvisible = /\u200B/g;
                value = value.replace(allInvisible, '&#8203;');
                var result = test.test.content.replace(allInvisible, '&#8203;');
                assert.strictEqual(value, result, test.name);

                if (test.test.start && value !== result) {
                    assert.notOk("Wrong DOM (see previous assert)", test.name + " (carret position)");
                    return;
                }
            }

            $editable[0].normalize();

            // test carret position
            if (test.test.start) {
                var start = _select(test.test.start);
                var range = Wysiwyg.getRange();
                if ((range.sc !== range.ec || range.so !== range.eo) && !test.test.end) {
                    assert.ok(false, test.name + ": the carret is not colapsed and the 'end' selector in test is missing");
                    return;
                }
                var end = test.test.end ? _select(test.test.end) : start;
                if (start.node && end.node) {
                    range = Wysiwyg.getRange();
                    var startPoint = endOfAreaBetweenTwoNodes({
                        node: range.sc,
                        offset: range.so,
                    });
                    var endPoint = endOfAreaBetweenTwoNodes({
                        node: range.ec,
                        offset: range.eo,
                    });
                    var sameDOM = (startPoint.node.outerHTML || startPoint.node.textContent) === (start.node.outerHTML || start.node.textContent);
                    var stringify = function (obj) {
                        if (!sameDOM) {
                            delete obj.sameDOMsameNode;
                        }
                        return JSON.stringify(obj, null, 2)
                            .replace(/"([^"\s-]+)":/g, "\$1:")
                            .replace(/([^\\])"/g, "\$1'")
                            .replace(/\\"/g, '"');
                    };
                    assert.deepEqual(stringify({
                            startNode: startPoint.node.outerHTML || startPoint.node.textContent,
                            startOffset: startPoint.offset,
                            endPoint: endPoint.node.outerHTML || endPoint.node.textContent,
                            endOffset: endPoint.offset,
                            sameDOMsameNode: sameDOM && startPoint.node === start.node,
                        }),
                        stringify({
                            startNode: start.node.outerHTML || start.node.textContent,
                            startOffset: start.offset,
                            endPoint: end.node.outerHTML || end.node.textContent,
                            endOffset: end.offset,
                            sameDOMsameNode: true,
                        }),
                        test.name + " (carret position)");
                }
            }
        });
    }
    while (keyboardTests.length) {
        defPollTest = defPollTest.then(pollTest.bind(null, keyboardTests.shift()));
    }

    return defPollTest;
};


/**
 * Select a node in the dom with is offset.
 *
 * @param {String} startSelector
 * @param {String} endSelector
 * @param {jQuery} $editable
 * @returns {Object} {sc, so, ec, eo}
 */
var select = (function () {
    var __select = function (selector, $editable) {
        var sel = selector.match(/^(.+?)(:contents\(\)\[([0-9]+)\]|:contents\(([0-9]+)\))?(->([0-9]+))?$/);
        var $node = $editable.find(sel[1]);
        return {
            node: sel[2] ? $node.contents()[sel[3] ? +sel[3] : +sel[4]] : $node[0],
            offset: sel[5] ? +sel[6] : 0,
        };
    };
    return function (startSelector, endSelector, $editable) {
        var start = __select(startSelector, $editable);
        var end = endSelector ? __select(endSelector, $editable) : start;
        return {
            sc: start.node,
            so: start.offset,
            ec: end.node,
            eo: end.offset,
        };
    };
})();

/**
 * Trigger a keydown event.
 *
 * @param {String or Number} key (name or code)
 * @param {jQuery} $editable
 * @param {Object} [options]
 * @param {Boolean} [options.firstDeselect] (default: false) true to deselect before pressing
 */
var keydown = function (key, $editable, options) {
    var keyPress = {};
    keyPress.key = key;
    var range = Wysiwyg.getRange();
    if (!range) {
        console.error("Editor have not any range");
        return;
    }
    if (options && options.firstDeselect) {
        range.sc = range.ec;
        range.so = range.eo;
        Wysiwyg.setRange(range.sc, range.so, range.ec, range.eo);
    }
    var target = range.ec;
    var $target = $(target.tagName ? target : target.parentNode);
    var event = $.Event("keydown", keyPress);
    $target.trigger(event);

    if (!event.defaultPrevented) {
        if (keyPress.key.length === 1) {
            textInput($target[0], keyPress.key);
        } else {
            console.warn('Native "' + keyPress.key + '" is not supported in test');
        }
    }
};

var textInput = function (target, char) {
    var ev = new CustomEvent('textInput', {
        bubbles: true,
        cancelBubble: false,
        cancelable: true,
        composed: true,
        data: char,
        defaultPrevented: false,
        detail: 0,
        eventPhase: 3,
        isTrusted: true,
        returnValue: true,
        sourceCapabilities: null,
        type: "textInput",
        which: 0,
    });
    ev.data = char;
    target.dispatchEvent(ev);

    if (!ev.defaultPrevented) {
        document.execCommand("insertText", 0, ev.data);
    }
};

//--------------------------------------------------------------------------
// Convert Inline
//--------------------------------------------------------------------------

const tableAttributesString = Object.keys(TABLE_ATTRIBUTES).map(key => `${key}="${TABLE_ATTRIBUTES[key]}"`).join(' ');
const tableStylesString = Object.keys(TABLE_STYLES).map(key => `${key}: ${TABLE_STYLES[key]};`).join(' ');
/**
 * Take a matrix representing a grid and return an HTML string of the Bootstrap
 * grid. The matrix is an array of rows, with each row being an array of cells.
 * Each cell can be represented either by a 0 < number < 13 (col-#) or a falsy
 * value (col). Each cell has its coordinates `(row index, column index)` as
 * text content.
 * Eg: [                        // <div class="container">
 *      [                       //     <div class="row">
 *          1,                  //         <div class="col-1">(0, 0)</div>
 *          11,                 //         <div class="col-11">(0, 1)</div>
 *      ],                      //     </div>
 *      [                       //     <div class="row">
 *          false,              //         <div class="col">(1, 0)</div>
 *      ],                      //     </div>
 * ]                            // </div>
 *
 * @param {Array<Array<Number|null>>} matrix
 * @returns {string}
 */
export function getGridHtml(matrix) {
    return (
        `<div class="container">` +
        matrix.map((row, iRow) => (
            `<div class="row">` +
            row.map((col, iCol) => (
                `<div class="${col ? 'col-' + col : 'col'}">(${iRow}, ${iCol})</div>`
            )).join('') +
            `</div>`
        )).join('') +
        `</div>`
    );
}
export function getTdHtml(colspan, text, containerWidth) {
    return (
        `<td colspan="${colspan}"${
            containerWidth ? ' ' + `style="max-width: ${Math.round(containerWidth*colspan/12*100)/100}px;"`
                           : ''}>` +
            text +
        `</td>`
    );
}
/**
 * Take a matrix representing a table and return an HTML string of the table.
 * The matrix is an array of rows, with each row being an array of cells. Each
 * cell is represented by a tuple of numbers [colspan, width (in percent)]. A
 * cell can have a string as third value to represent its text content. The
 * default text content of each cell is its coordinates `(row index, column
 * index)`. If the cell has a number as third value, it will be used as the
 * max-width of the cell (in pixels).
 * Eg: [                        // <table> (note: extra attrs and styles apply)
 *      [                       //   <tr>
 *          [1, 8],             //     <td colspan="1" width="8%">(0, 0)</td>
 *          [11, 92]            //     <td colspan="11" width="92%">(0, 1)</td>
 *      ],                      //   </tr>
 *      [                       //   <tr>
 *          [2, 17, 'A'],       //     <td colspan="2" width="17%">A</td>
 *          [10, 83],           //     <td colspan="10" width="83%">(1, 1)</td>
 *      ],                      //   </tr>
 * ]                            // </table>
 *
 * @param {Array<Array<Array<[Number, Number, string?, number?]>>>} matrix
 * @param {Number} [containerWidth]
 * @returns {string}
 */
export function getTableHtml(matrix, containerWidth) {
    return (
        `<table ${tableAttributesString} style="width: 100% !important; ${tableStylesString}">` +
        matrix.map((row, iRow) => (
            `<tr>` +
            row.map((col, iCol) => (
                getTdHtml(col[0], typeof col[2] === 'string' ? col[2] : `(${iRow}, ${iCol})`, containerWidth)
            )).join('') +
            `</tr>`
        )).join('') +
        `</table>`
    );
}
/**
 * Take a number of rows and a number of columns (or number of columns per
 * individual row) and return an HTML string of the corresponding grid. Every
 * column is a regular Bootstrap "col" (no col-#).
 * Eg: [2, 3] <=> getGridHtml([[false, false, false], [false, false, false]])
 * Eg: [2, [2, 1]] <=> getGridHtml([[false, false], [false]])
 *
 * @see getGridHtml
 * @param {Number} nRows
 * @param {Number|Number[]} nCols
 * @returns {string}
 */
export function getRegularGridHtml(nRows, nCols) {
    const matrix = new Array(nRows).fill().map((_, iRow) => (
        new Array(Array.isArray(nCols) ? nCols[iRow] : nCols).fill()
    ));
    return getGridHtml(matrix);
};
/**
 * Take a number of rows, a number of columns (or number of columns per
 * individual row), a colspan (or colspan per individual row) and a width (or
 * width per individual row, in percent), and return an HTML string of the
 * corresponding table. Every cell in a row has the same colspan/width.
 * Eg: [2, 2, 6, 50] <=> getTableHtml([[[6, 50], [6, 50]], [[6, 50], [6, 50]]])
 * Eg: [2, [2, 1], [6, 12], [50, 100]] <=> getTableHtml([[[6, 50], [6, 50]], [[12, 100]]])
 *
 * @see getTableHtml
 * @param {Number} nRows
 * @param {Number|Number[]} nCols
 * @param {Number|Number[]} colspan
 * @param {Number|Number[]} width
 * @param {Number} containerWidth
 * @returns {string}
 */
export function getRegularTableHtml(nRows, nCols, colspan, width, containerWidth) {
    const matrix = new Array(nRows).fill().map((_, iRow) => (
        new Array(Array.isArray(nCols) ? nCols[iRow] : nCols).fill().map(() => ([
            Array.isArray(colspan) ? colspan[iRow] : colspan,
            Array.isArray(width) ? width[iRow] : width,
        ])))
    );
    return getTableHtml(matrix, containerWidth);
}
/**
 * Take an HTML string and returns that string stripped from any HTML comments.
 * By default, also removes the mso-hide class which is only there for outlook
 * to hide elements when we use mso conditional comments.
 *
 * @param {string} html
 * @param {boolean} [removeMsoHide=true]
 * @returns {string}
 */
export function removeComments(html, removeMsoHide=true) {
    const cleanHtml = html.replace(/<!--(.*?)-->/g, '');
    if (removeMsoHide) {
        return cleanHtml.replaceAll(' class="mso-hide"', '').replace(/\s*mso-hide/g, '').replace(/mso-hide\s*/g, '');
    } else {
        return cleanHtml;
    }
}

export default {
    wysiwygData: wysiwygData,
    testKeyboard: testKeyboard,
    select: select,
    keydown: keydown,
    getGridHtml: getGridHtml,
    getTableHtml: getTableHtml,
    getRegularGridHtml: getRegularGridHtml,
    getRegularTableHtml: getRegularTableHtml,
    getTdHtml: getTdHtml,
    removeComments: removeComments,
};

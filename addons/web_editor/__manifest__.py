# -*- coding: utf-8 -*-
# Part of Orj. See LICENSE file for full copyright and licensing details.

{
    'name': 'Web Editor',
    'category': 'Hidden',
    'description': """
Orj Web Editor widget.
==========================

""",
    'depends': ['bus', 'web', 'html_editor'],
    'data': [
        'security/ir.model.access.csv',
        'data/editor_assets.xml',
        'views/editor.xml',
        'views/snippets.xml',
    ],
    'assets': {

        #----------------------------------------------------------------------
        # MAIN BUNDLES
        #----------------------------------------------------------------------

        'web_editor.assets_snippets_menu': [
            'web_editor/static/src/js/core/owl_utils.js',
            'web_editor/static/src/js/editor/snippets.editor.js',
            'web_editor/static/src/js/editor/snippets.options.js',
        ],
        'web_editor.wysiwyg_iframe_editor_assets': [
            ('include', 'web._assets_helpers'),

            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            'web/static/lib/bootstrap/scss/_variables-dark.scss',
            'web/static/lib/bootstrap/scss/_maps.scss',

            'web/static/src/libs/fontawesome/css/font-awesome.css',
            'web/static/lib/orj_ui_icons/*',
            'web/static/src/webclient/navbar/navbar.scss',
            'web/static/src/scss/animation.scss',
            'web/static/src/core/colorpicker/colorpicker.scss',
            'web/static/src/scss/mimetypes.scss',
            'web/static/src/scss/ui.scss',
            'web/static/src/legacy/scss/ui.scss',
            'web/static/src/views/fields/translation_dialog.scss',
            'web/static/src/scss/fontawesome_overridden.scss',

            'web/static/src/module_loader.js',
            'web/static/src/session.js',
            'web/static/lib/owl/owl.js',
            'web/static/lib/owl/orj_module.js',
            'web/static/lib/jquery/jquery.js',
            'web/static/lib/popper/popper.js',
            'web/static/lib/bootstrap/js/dist/util/index.js',
            'web/static/lib/bootstrap/js/dist/dom/data.js',
            'web/static/lib/bootstrap/js/dist/dom/event-handler.js',
            'web/static/lib/bootstrap/js/dist/dom/manipulator.js',
            'web/static/lib/bootstrap/js/dist/dom/selector-engine.js',
            'web/static/lib/bootstrap/js/dist/util/config.js',
            'web/static/lib/bootstrap/js/dist/util/component-functions.js',
            'web/static/lib/bootstrap/js/dist/util/backdrop.js',
            'web/static/lib/bootstrap/js/dist/util/focustrap.js',
            'web/static/lib/bootstrap/js/dist/util/sanitizer.js',
            'web/static/lib/bootstrap/js/dist/util/scrollbar.js',
            'web/static/lib/bootstrap/js/dist/util/swipe.js',
            'web/static/lib/bootstrap/js/dist/util/template-factory.js',
            'web/static/lib/bootstrap/js/dist/base-component.js',
            'web/static/lib/bootstrap/js/dist/alert.js',
            'web/static/lib/bootstrap/js/dist/button.js',
            'web/static/lib/bootstrap/js/dist/carousel.js',
            'web/static/lib/bootstrap/js/dist/collapse.js',
            'web/static/lib/bootstrap/js/dist/dropdown.js',
            'web/static/lib/bootstrap/js/dist/modal.js',
            'web/static/lib/bootstrap/js/dist/offcanvas.js',
            'web/static/lib/bootstrap/js/dist/tooltip.js',
            'web/static/lib/bootstrap/js/dist/popover.js',
            'web/static/lib/bootstrap/js/dist/scrollspy.js',
            'web/static/lib/bootstrap/js/dist/tab.js',
            'web/static/lib/bootstrap/js/dist/toast.js',
            'web/static/src/libs/bootstrap.js',
            'web/static/src/legacy/js/libs/jquery.js',
            'web/static/src/core/utils/scrolling.js',
            'web/static/src/core/registry.js',
            'web/static/src/core/templates.js',
            'web/static/src/core/template_inheritance.js',

            # orj-editor
            'web_editor/static/src/js/editor/orj-editor/src/utils/utils.js',
            'web_editor/static/src/js/editor/orj-editor/src/utils/constants.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/align.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/commands.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/deleteBackward.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/deleteForward.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/enter.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/shiftEnter.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/shiftTab.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/tab.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/toggleList.js',

            # orj utils
            'web_editor/static/src/scss/bootstrap_overridden.scss',
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            'web/static/lib/bootstrap/scss/_variables-dark.scss',
            'web/static/lib/bootstrap/scss/_maps.scss',
            'web_editor/static/src/js/editor/orj-editor/src/style.scss',

            # integration
            'web_editor/static/src/scss/wysiwyg.scss',
            'web_editor/static/src/scss/wysiwyg_iframe.scss',
            'web_editor/static/src/scss/wysiwyg_snippets.scss',

            'web_editor/static/src/xml/editor.xml',
            'web_editor/static/src/xml/grid_layout.xml',
            'web_editor/static/src/xml/snippets.xml',
            'web_editor/static/src/xml/wysiwyg.xml',
            'web_editor/static/src/xml/wysiwyg_colorpicker.xml',
        ],
        'web_editor.assets_media_dialog': [
            'web_editor/static/src/components/**/*',
        ],
        'web_editor.assets_tests_styles': [
            ('include', 'web._assets_helpers'),
            'web_editor/static/src/js/editor/orj-editor/src/base_style.scss',
            'web_editor/static/src/js/editor/orj-editor/src/checklist.scss',
        ],
        'web_editor.assets_wysiwyg': [
            # legacy stuff that are no longer in assets_backend
            'web/static/src/legacy/js/core/class.js',
            'web/static/src/legacy/js/public/minimal_dom.js',
            'web/static/src/legacy/js/public/public_widget.js',

            # lib
            'web_editor/static/lib/cropperjs/cropper.css',
            'web_editor/static/lib/cropperjs/cropper.js',
            'web_editor/static/lib/jquery-cropper/jquery-cropper.js',
            'web_editor/static/lib/jQuery.transfo.js',
            'web_editor/static/lib/webgl-image-filter/webgl-image-filter.js',
            'web/static/lib/dompurify/DOMpurify.js',

            # orj-editor
            'web_editor/static/src/js/editor/orj-editor/src/OrjEditor.js',
            'web_editor/static/src/js/editor/orj-editor/src/utils/constants.js',
            'web_editor/static/src/js/editor/orj-editor/src/utils/sanitize.js',
            'web_editor/static/src/js/editor/orj-editor/src/utils/serialize.js',
            'web_editor/static/src/js/editor/orj-editor/src/tablepicker/TablePicker.js',
            'web_editor/static/src/js/editor/orj-editor/src/powerbox/patienceDiff.js',
            'web_editor/static/src/js/editor/orj-editor/src/powerbox/Powerbox.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/align.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/commands.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/deleteBackward.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/deleteForward.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/enter.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/shiftEnter.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/shiftTab.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/tab.js',
            'web_editor/static/src/js/editor/orj-editor/src/commands/toggleList.js',

            # utils
            'web_editor/static/src/js/editor/drag_and_drop.js',
            'web_editor/static/src/js/wysiwyg/linkDialogCommand.js',
            'web_editor/static/src/js/wysiwyg/MoveNodePlugin.js',
            'web_editor/static/src/js/wysiwyg/PeerToPeer.js',
            'web_editor/static/src/js/wysiwyg/conflict_dialog.js',
            'web_editor/static/src/js/wysiwyg/conflict_dialog.xml',
            'web_editor/static/src/js/wysiwyg/get_color_picker_template_service.js',

            # orj utils
            ('include', 'web._assets_helpers'),

            'web_editor/static/src/scss/bootstrap_overridden.scss',
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            'web/static/lib/bootstrap/scss/_variables-dark.scss',
            'web/static/lib/bootstrap/scss/_maps.scss',
            'web_editor/static/src/js/editor/orj-editor/src/style.scss',

            # integration
            'web_editor/static/src/scss/wysiwyg.scss',
            'web_editor/static/src/scss/wysiwyg_iframe.scss',
            'web_editor/static/src/scss/wysiwyg_snippets.scss',

            'web_editor/static/src/js/editor/perspective_utils.js',
            'web_editor/static/src/js/editor/image_processing.js',
            'web_editor/static/src/js/editor/custom_colors.js',

            # widgets & plugins
            'web_editor/static/src/js/wysiwyg/widgets/**/*',
            'web_editor/static/src/js/editor/toolbar.js',
            'web_editor/static/src/js/editor/add_snippet_dialog.js',

            # Launcher
            'web_editor/static/src/js/wysiwyg/wysiwyg_jquery_extention.js',
            'web_editor/static/src/js/wysiwyg/wysiwyg.js',
            'web_editor/static/src/js/wysiwyg/wysiwyg_iframe.js',

            'web_editor/static/src/xml/add_snippet_dialog.xml',
            'web_editor/static/src/xml/editor.xml',
            'web_editor/static/src/xml/grid_layout.xml',
            'web_editor/static/src/xml/snippets.xml',
            'web_editor/static/src/xml/wysiwyg.xml',
            'web_editor/static/src/xml/wysiwyg_colorpicker.xml',
        ],
        'web_editor.backend_assets_wysiwyg': [
            ('include', 'web_editor.assets_wysiwyg'),
        ],
        'web.assets_backend': [
            'web_editor/static/src/js/editor/orj-editor/src/base_style.scss',
            'web_editor/static/lib/vkbeautify/**/*',
            'web_editor/static/src/js/common/**/*',
            'web_editor/static/src/js/editor/orj-editor/src/utils/utils.js',
            'web_editor/static/src/js/wysiwyg/fonts.js',

            ('include', 'web_editor.assets_media_dialog'),

            'web_editor/static/src/scss/web_editor.common.scss',
            'web_editor/static/src/scss/web_editor.backend.scss',

            'web_editor/static/src/js/backend/**/*',
            'web_editor/static/src/xml/backend.xml',
        ],
        "web.assets_web_dark": [
            'web_editor/static/src/scss/orj-editor/powerbox.dark.scss',
            'web_editor/static/src/scss/orj-editor/tablepicker.dark.scss',
            'web_editor/static/src/scss/orj-editor/tableui.dark.scss',
            'web_editor/static/src/scss/wysiwyg.dark.scss',
            'web_editor/static/src/scss/web_editor.common.dark.scss',
        ],
        'web.assets_frontend_minimal': [
            'web_editor/static/src/js/frontend/loader_loading.js',
        ],
        'web.assets_frontend': [
            ('include', 'web_editor.assets_media_dialog'),

            'web_editor/static/src/js/editor/orj-editor/src/base_style.scss',
            'web_editor/static/src/js/common/**/*',
            'web_editor/static/src/js/core/owl_utils.js',
            'web_editor/static/src/js/editor/orj-editor/src/utils/utils.js',
            'web_editor/static/src/js/wysiwyg/fonts.js',

            'web_editor/static/src/scss/web_editor.common.scss',
            'web_editor/static/src/scss/web_editor.frontend.scss',

            'web_editor/static/src/js/frontend/loadWysiwygFromTextarea.js',
        ],
        'web.report_assets_common': [
            'web_editor/static/src/js/editor/orj-editor/src/base_style.scss',
            'web_editor/static/src/scss/bootstrap_overridden.scss',
            'web_editor/static/src/scss/web_editor.common.scss',
        ],

        #----------------------------------------------------------------------
        # SUB BUNDLES
        #----------------------------------------------------------------------

        'web._assets_primary_variables': [
            'web_editor/static/src/scss/web_editor.variables.scss',
            'web_editor/static/src/scss/wysiwyg.variables.scss',
        ],
        'web._assets_secondary_variables': [
            'web_editor/static/src/scss/secondary_variables.scss',
        ],
        'web._assets_backend_helpers': [
            'web_editor/static/src/scss/bootstrap_overridden_backend.scss',
            'web_editor/static/src/scss/bootstrap_overridden.scss',
        ],
        'web._assets_frontend_helpers': [
            ('prepend', 'web_editor/static/src/scss/bootstrap_overridden.scss'),
        ],

        # ----------------------------------------------------------------------
        # TESTS BUNDLES
        # ----------------------------------------------------------------------

        'web.qunit_suite_tests': [
            ('include', 'web_editor.assets_snippets_menu'),
            ('include', 'web_editor.backend_assets_wysiwyg'),

            'web_editor/static/tests/**/*',
            'web_editor/static/src/js/editor/orj-editor/test/utils.js'
        ],
        'web_editor.mocha_tests': [
            'web/static/src/module_loader.js',
            # insert module dependencies here
            'web/static/src/core/utils/concurrency.js',

            'web_editor/static/src/js/editor/orj-editor/src/**/*js',
            'web_editor/static/src/js/editor/orj-editor/test/spec/*js',
            'web_editor/static/src/js/editor/orj-editor/test/*js',

            'web/static/lib/dompurify/DOMpurify.js',
        ],
    },
    'auto_install': True,
    'license': 'LGPL-3',
}

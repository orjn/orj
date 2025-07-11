/** @orj-module **/

/* global YT, Vimeo */

    import publicWidget from '@web/legacy/js/public/public_widget';
    import { renderToElement } from "@web/core/utils/render";
    import { session } from "@web/session";
    import { Quiz } from '@website_slides/js/slides_course_quiz';
    import { SlideCoursePage } from '@website_slides/js/slides_course_page';
    import { unhideConditionalElements } from '@website/js/content/inject_dom';
    import { SlideShareDialog } from './public/components/slide_share_dialog/slide_share_dialog';
    import '@website_slides/js/slides_course_join';
    import { SIZES, utils as uiUtils } from "@web/core/ui/ui_service";
    import { rpc } from "@web/core/network/rpc";

    import { markup } from "@orj/owl";

    /**
     * Helper: Get the slide dict matching the given criteria
     *
     * @private
     * @param {Array<Object>} slideList List of dict reprensenting a slide
     * @param {[string] : any} matcher
     */
    var findSlide = function (slideList, matcher) {
        return slideList.find((slide) => {
            return Object.keys(matcher).every((key) => matcher[key] === slide[key]);
        });
    };

    /**
     * This widget is responsible of display Youtube Player
     *
     * The widget will trigger an event `change_slide` when the video is at
     * its end, and `slide_completed` when the player is at 30 sec before the
     * end of the video (30 sec before is considered as completed).
     */
    var VideoPlayerYouTube = publicWidget.Widget.extend({
        template: 'website.slides.fullscreen.video.youtube',
        youtubeUrl: 'https://www.youtube.com/iframe_api',

        init: function (parent, slide) {
            this.slide = slide;
            return this._super.apply(this, arguments);
        },
        start: function (){
            var self = this;
            return Promise.all([this._super.apply(this, arguments), this._loadYoutubeAPI()]).then(function() {
                self._setupYoutubePlayer();
            });
        },
        _loadYoutubeAPI: function () {
            var self = this;
            var prom = new Promise(function (resolve, reject) {
                if ($(document).find('script[src="' + self.youtubeUrl + '"]').length === 0) {
                    var $youtubeElement = $('<script/>', {src: self.youtubeUrl});
                    $(document.head).append($youtubeElement);

                    // function called when the Youtube asset is loaded
                    // see https://developers.google.com/youtube/iframe_api_reference#Requirements
                    window.onYouTubeIframeAPIReady = function () {
                        resolve();
                    };
                } else {
                    resolve();
                }
            });
            return prom;
        },
        /**
         * Links the youtube api to the iframe present in the template
         *
         * @private
         */
        _setupYoutubePlayer: function (){
            this.player = new YT.Player('youtube-player' + this.slide.id, {
                playerVars: {
                    'autoplay': 1,
                    'origin': window.location.origin
                },
                events: {
                    'onStateChange': this._onPlayerStateChange.bind(this)
                }
            });
        },
        /**
         * Specific method of the youtube api.
         * Whenever the player starts playing/pausing/buffering/..., a setinterval is created.
         * This setinterval is used to check te user's progress in the video.
         * Once the user reaches a particular time in the video (30s before end), the slide will be considered as completed
         * if the video doesn't have a mini-quiz.
         * This method also allows to automatically go to the next slide (or the quiz associated to the current
         * video) once the video is over
         *
         * @private
         * @param {*} event
         */
        _onPlayerStateChange: function (event){
            var self = this;

            if (self.slide.completed) {
                return;
            }

            if (event.data !== YT.PlayerState.ENDED) {
                if (!event.target.getCurrentTime) {
                    return;
                }

                if (self.tid) {
                    clearInterval(self.tid);
                }

                self.currentVideoTime = event.target.getCurrentTime();
                self.totalVideoTime = event.target.getDuration();
                self.tid = setInterval(function (){
                    self.currentVideoTime += 1;
                    if (self.totalVideoTime && self.currentVideoTime > self.totalVideoTime - 30){
                        clearInterval(self.tid);
                        if (self.slide.isMember && !self.slide.hasQuestion && !self.slide.completed){
                            self.trigger_up('slide_mark_completed', self.slide);
                        }
                    }
                }, 1000);
            } else {
                if (self.tid) {
                    clearInterval(self.tid);
                }
                this.player = undefined;
                if (this.slide.hasNext) {
                    this.trigger_up('slide_go_next');
                }
            }
        },
    });

    /**
     * This widget is responsible of loading the Vimeo video.
     *
     * Similarly to the YouTube implementation, the widget will trigger an event `change_slide` when
     * the video is at its end, and `slide_completed` when the player is at 30 sec before the end of
     * the video (30 sec before is considered as completed).
     *
     * See https://developer.vimeo.com/player/sdk/reference for all the API documentation.
     */
    var VideoPlayerVimeo = publicWidget.Widget.extend({
        template: 'website.slides.fullscreen.video.vimeo',
        vimeoScriptUrl: 'https://player.vimeo.com/api/player.js',

        init: function (parent, slide) {
            this.slide = slide;
            return this._super.apply(this, arguments);
        },

        /**
         * Loads the Vimeo JS API that allows interfacing with the iframe viewer.
         * (We only load the API if not already loaded).
         *
         * @returns {Promise}
         */
        willStart: function () {
            var self = this;
            var vimeoAPIPromise = new Promise(function (resolve, reject) {
                if ($(document).find('script[src="' + self.vimeoScriptUrl + '"]').length === 0) {
                    $.ajax({
                        url: self.vimeoScriptUrl,
                        dataType: 'script',
                        success: function () {resolve();}
                    });
                } else {
                    resolve();
                }
            });

            return Promise.all([this._super.apply(this, arguments), vimeoAPIPromise]);
        },

        start: function () {
            return this._super.apply(arguments).then(this._setupVideoPlayer.bind(this));
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Instantiate the Vimeo player and register the various events.
         */
        _setupVideoPlayer: async function () {
            this.player = new Vimeo.Player(this.$('iframe')[0]);
            this.videoDuration = await this.player.getDuration();
            this.player.on('timeupdate', this._onVideoTimeUpdate.bind(this));
            this.player.on('ended', this._onVideoEnded.bind(this));
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * When the player triggers the 'ended' event, we go to the next slide if there is one.
         *
         * See https://developer.vimeo.com/player/sdk/reference#ended for more information
         */
        _onVideoEnded: function () {
            if (this.slide.hasNext) {
                this.trigger_up('slide_go_next', this.slide);
            }
        },

        /**
         * Every time the video changes position, both while viewing and also when seeking manually,
         * Vimeo triggers this handy 'timeupdate' event.
         * We use it to set the slide as completed as soon as we reach the end (30 last seconds).
         *
         * See https://developer.vimeo.com/player/sdk/reference#timeupdate for more information
         *
         * @param {Object} eventData the 'timeupdate' event data
         */
         _onVideoTimeUpdate: async function (eventData) {
            if (eventData.seconds > (this.videoDuration - 30)) {
                if (this.slide.isMember && !this.slide.hasQuestion && !this.slide.completed){
                    this.trigger_up('slide_mark_completed', this.slide);
                }
            }
        }
    });


    /**
     * This widget is responsible of navigation for one slide to another:
     *  - by clicking on any slide list entry
     *  - by mouse click (next / prev)
     *  - by recieving the order to go to prev/next slide (`goPrevious` and `goNext` public methods)
     *
     * The widget will trigger an event `change_slide` with
     * the `slideId` and `isMiniQuiz` as data.
     */
    var Sidebar = publicWidget.Widget.extend({
        events: {
            'click .o_wslides_fs_sidebar_list_item .o_wslides_fs_slide_name': '_onClickTab',
        },
        init: function (parent, slideList, defaultSlide) {
            var result = this._super.apply(this, arguments);
            this.slideEntries = slideList;
            this._slideEntry = defaultSlide;
            return result;
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                $(document).keydown(self._onKeyDown.bind(self));
            });
        },
        destroy: function () {
            $(document).unbind('keydown', this._onKeyDown.bind(this));
            return this._super.apply(this, arguments);
        },
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------
        /**
         * Change the current slide with the next one (if there is one).
         *
         * @public
         */
        goNext: function () {
            var currentIndex = this._getCurrentIndex();
            if (currentIndex < this.slideEntries.length-1) {
                this._updateSlideEntry(this.slideEntries[currentIndex + 1]);
            }
        },
        /**
         * Change the current slide with the previous one (if there is one).
         *
         * @public
         */
        goPrevious: function () {
            var currentIndex = this._getCurrentIndex();
            if (currentIndex >= 1) {
                this._updateSlideEntry(this.slideEntries[currentIndex - 1]);
            }
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
        /**
         * Get the index of the current slide entry (slide and/or quiz)
         */
        _getCurrentIndex: function () {
            const slide = this._slideEntry;
            var currentIndex = this.slideEntries.findIndex(entry =>{
                return entry.id === slide.id && entry.isQuiz === slide.isQuiz;
            });
            return currentIndex;
        },
        //--------------------------------------------------------------------------
        // Handler
        //--------------------------------------------------------------------------
        /**
         * Handler called whenever the user clicks on a sub-quiz which is linked to a slide.
         * This does NOT handle the case of a slide of category "quiz".
         * By going through this handler, the widget will be able to determine that it has to render
         * the associated quiz and not the main content.
         *
         * @private
         * @param {*} ev
         */
        _onClickMiniQuiz: function (ev) {
            var slideID = parseInt($(ev.currentTarget).data().slide_id);
            this._updateSlideEntry({
                slideID: slideID,
                isMiniQuiz: true
            });
            this.trigger_up('change_slide', this._slideEntry);
        },
        /**
         * Handler called when the user clicks on a normal slide tab
         *
         * @private
         * @param {*} ev
         */
        _onClickTab: function (ev) {
            ev.stopPropagation();
            const $elem = $(ev.currentTarget).closest('.o_wslides_fs_sidebar_list_item');
            if ($elem.data('canAccess') === 'True') {
                var isQuiz = $elem.data('isQuiz');
                var slideID = parseInt($elem.data('id'));
                var slide = findSlide(this.slideEntries, {id: slideID, isQuiz: isQuiz});
                this._updateSlideEntry(slide);
            }
        },
        /**
         * Actively changes the active tab in the sidebar so that it corresponds
         * the slide currently displayed
         *
         * @private
         * @param {Object} slide
         */
        _updateSlideEntry: function (slide) {
            if (this._slideEntry === slide) {
                return;
            }
            this._slideEntry = slide;
            this.$('.o_wslides_fs_sidebar_list_item.active').removeClass('active');
            var selector = '.o_wslides_fs_sidebar_list_item[data-id='+slide.id+'][data-is-quiz!="1"]';

            this.$(selector).addClass('active');
            this.trigger_up('change_slide', this._slideEntry);
        },

        /**
         * Binds left and right arrow to allow the user to navigate between slides
         *
         * @param {*} ev
         * @private
         */
        _onKeyDown: function (ev){
            switch (ev.key){
                case "ArrowLeft":
                    this.goPrevious();
                    break;
                case "ArrowRight":
                    this.goNext();
                    break;
            }
        },
    });

    /**
     * This widget's purpose is to show content of a course, naviguating through contents
     * and correclty display it. It also handle slide completion, course progress, ...
     *
     * This widget is rendered sever side, and attached to the existing DOM.
     */
    var Fullscreen = SlideCoursePage.extend({
        events: Object.assign({}, SlideCoursePage.prototype.events, {
            'click .o_wslides_fs_toggle_sidebar': '_onClickToggleSidebar',
            'click .o_wslides_fs_share': '_onClickShareSlide',
        }),
        custom_events: Object.assign({}, SlideCoursePage.prototype.custom_events, {
            'change_slide': '_onChangeSlideRequest',
            'slide_go_next': '_onSlideGoToNext',
        }),
        /**
        * @override
        * @param {Object} el
        * @param {Object} slides Contains the list of all slides of the course
        * @param {integer} defaultSlideId Contains the ID of the slide requested by the user
        */
        init: function (parent, slides, defaultSlideId, channelData) {
            var result = this._super.apply(this,arguments);
            this.initialSlideID = defaultSlideId;
            this.slides = this._preprocessSlideData(slides);
            this.channel = channelData;
            var slide;
            const urlParams = new URL(window.location).searchParams;
            if (defaultSlideId) {
                slide = findSlide(this.slides, {id: defaultSlideId, isQuiz: String(urlParams.get("quiz")) === "1" });
            } else {
                slide = this.slides[0];
            }

            this._slideValue = slide;

            this.sidebar = new Sidebar(this, this.slides, slide);
            return result;
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            this._toggleSidebar();
            const backendNavEl = document.querySelector('.o_frontend_to_backend_nav');
            if (backendNavEl) {
                backendNavEl.remove();
            }
            return this._super.apply(this, arguments).then(function () {
                return self._onChangeSlide(); // trigger manually once DOM ready, since slide content is not rendered server side
            });
        },
        /**
         * Extended to attach sub widget to sub DOM. This might be experimental but
         * seems working fine.
         *
         * @override
         */
        attachTo: function (){
            var defs = [this._super.apply(this, arguments)];
            defs.push(this.sidebar.attachTo(this.$('.o_wslides_fs_sidebar')));
            return $.when.apply($, defs);
        },
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
        /**
         * Fetches content with an rpc call for slides of category "article"
         *
         * @private
         */
        _fetchHtmlContent: function () {
            const currentSlide = this._slideValue;
            return rpc("/slides/slide/get_html_content", {
                'slide_id': currentSlide.id
            }).then(function (data){
                if (data.html_content) {
                    currentSlide.htmlContent = data.html_content;
                }
            });
        },
        /**
        * Fetches slide content depending on its category.
        * If the slide doesn't need to fetch any content, return a resolved deferred
        *
        * @private
        */
        _fetchSlideContent: function () {
            const slide = this._slideValue;
            if (slide.category === 'article' && !slide.isQuiz) {
                return this._fetchHtmlContent();
            }
            return Promise.resolve();
        },
        getDocumentMaxPage() {
            const iframe = document.querySelector("iframe.o_wslides_iframe_viewer");
            const iframeDocument = iframe.contentWindow.document;
            return parseInt(iframeDocument.querySelector("#page_count").innerText);
        },
        /**
         * Extend the slide data list to add informations about rendering method, and other
         * specific values according to their slide_category.
         */
        _preprocessSlideData: function (slidesDataList) {
            slidesDataList.forEach(function (slideData, index) {
                // compute hasNext slide
                slideData.hasNext = index < slidesDataList.length-1;
                // compute embed url
                if (slideData.category === 'video' && slideData.videoSourceType !== 'vimeo') {
                    slideData.embedCode = $(slideData.embedCode).attr('src') || ""; // embedCode contains an iframe tag, where src attribute is the url (youtube or embed document from orj)
                    var separator = slideData.embedCode.indexOf("?") !== -1 ? "&" : "?";
                    var scheme = slideData.embedCode.indexOf('//') === 0 ? 'https:' : '';
                    var params = { rel: 0, enablejsapi: 1, origin: window.location.origin };
                    if (slideData.embedCode.indexOf("//drive.google.com") === -1) {
                        params.autoplay = 1;
                    }
                    slideData.embedUrl = slideData.embedCode ? scheme + slideData.embedCode + separator + $.param(params) : "";
                } else if (slideData.category === 'video' && slideData.videoSourceType === 'vimeo') {
                    slideData.embedCode = markup(slideData.embedCode);
                } else if (slideData.category === 'infographic') {
                    slideData.embedUrl = `/web/image/slide.slide/${encodeURIComponent(slideData.id)}/image_1024`;
                } else if (slideData.category === 'document') {
                    slideData.embedUrl = $(slideData.embedCode).attr('src');
                }
                // fill empty property to allow searching on it with list.filter(matcher)
                slideData.isQuiz = !!slideData.isQuiz;
                slideData.hasQuestion = !!slideData.hasQuestion;
                // technical settings for the Fullscreen to work
                var autoSetDone = false;
                if (!slideData.hasQuestion) {
                    if (['infographic', 'document', 'article'].includes(slideData.category)) {
                        autoSetDone = true;  // images, documents (local + external) and articles are marked as completed when opened
                    } else if (slideData.category === 'video' && slideData.videoSourceType === 'google_drive') {
                        autoSetDone = true;  // google drive videos do not benefit from the YouTube integration and are marked as completed when opened
                    }
                }
                slideData._autoSetDone = autoSetDone;
            });
            return slidesDataList;
        },
        /**
         * Changes the url whenever the user changes slides.
         * This allows the user to refresh the page and stay on the right slide
         *
         * @private
         */
        _pushUrlState: function () {
            var urlParts = window.location.pathname.split('/');
            urlParts[urlParts.length - 1] = this._slideValue.slug;
            var url =  urlParts.join('/');
            this.$('.o_wslides_fs_exit_fullscreen').attr('href', url);
            var params = {'fullscreen': 1 };
            if (this._slideValue.isQuiz) {
                params.quiz = 1;
            }
            var fullscreenUrl = `${url}?${$.param(params)}`;
            history.pushState(null, '', fullscreenUrl);
        },
        /**
         * Render the current slide content using specific mecanism according to slide category:
         * - simply append content (for article)
         * - template rendering (for image, document, ....)
         * - using a sub widget (quiz and video)
         *
         * @private
         * @returns Deferred
         */
        _renderSlide: async function () {
            // Avoid concurrent execution of the slide rendering as it writes the content at the same place anyway.
            if (this._renderSlideRunning) { return; }
            this._renderSlideRunning = true;
            try {
                const slide = this._slideValue;
                var $content = this.$('.o_wslides_fs_content');
                $content.empty();
                if (this.websiteAnimateWidget) {
                    this.websiteAnimateWidget.destroy()
                    this.websiteAnimateWidget = null;
                }

                // display quiz slide, or quiz attached to a slide
                if (slide.category === 'quiz' || slide.isQuiz) {
                    $content.addClass('bg-white');
                    var QuizWidget = new Quiz(this, slide, this.channel);
                    return await QuizWidget.appendTo($content);
                }

                // render slide content
                if (['document', 'infographic'].includes(slide.category)) {
                    $content.empty().append(renderToElement('website.slides.fullscreen.content', {widget: this}));
                } else if (slide.category === 'video' && slide.videoSourceType === 'youtube') {
                    this.videoPlayer = new VideoPlayerYouTube(this, slide);
                    return await this.videoPlayer.appendTo($content);
                } else if (slide.category === 'video' && slide.videoSourceType === 'vimeo') {
                    this.videoPlayer = new VideoPlayerVimeo(this, slide);
                    return await this.videoPlayer.appendTo($content);
                } else if (slide.category === 'video' && slide.videoSourceType === 'google_drive') {
                    $content.empty().append(renderToElement('website.slides.fullscreen.video.google_drive', {widget: this}));
                } else if (slide.category === 'article'){
                    this.websiteAnimateWidget = new publicWidget.registry.WebsiteAnimate();
                    var $wpContainer = $('<div>').addClass('o_wslide_fs_article_content bg-white block w-100 overflow-auto p-3');
                    $wpContainer.html(slide.htmlContent);
                    $content.append($wpContainer);
                    this.trigger_up('widgets_start_request', {
                        $target: $content,
                    });
                    this.websiteAnimateWidget.attachTo($wpContainer);
                }
                unhideConditionalElements();
            } finally {
                this._renderSlideRunning = false;
            }
        },
        /**
         * @private
         */
        _updateSlideValue: function (slide) {
            if (this._slideValue === slide) {
                return;
            }
            this._slideValue = slide;
            this._onChangeSlide();
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
        /**
         * Triggered whenever the user changes slides.
         * When the current slide is changed, widget will be automatically updated
         * and allowed to: fetch the content if needed, render it, update the url,
         * and set slide as "completed" according to its category requirements. In
         * mobile case (i.e. limited screensize), sidebar will be toggled since
         * sidebar will block most or all of new slide visibility.
         *
         * @private
         */
        _onChangeSlide: function () {
            var self = this;
            const slide = this._slideValue;
            self._pushUrlState();
            return this._fetchSlideContent().then(function() { // render content
                var websiteName = document.title.split(" | ")[1]; // get the website name from title
                document.title =  (websiteName) ? slide.name + ' | ' + websiteName : slide.name;
                if  (uiUtils.getSize() < SIZES.MD) {
                    self._toggleSidebar(); // hide sidebar when small device screen
                }
                return self._renderSlide();
            }).then(function() {
                if (slide._autoSetDone && !session.is_website_user) {  // no useless RPC call
                    if (slide.category === 'document') {
                        // only set the slide as completed after iFrame is loaded to avoid concurrent execution with 'embedUrl' controller
                        self.el.querySelector('iframe.o_wslides_iframe_viewer').addEventListener('load', () => self._toggleSlideCompleted(slide));
                    } else {
                           return self._toggleSlideCompleted(slide);
                    }
                }
            });
        },
        /**
         * Changes current slide when receiving custom event `change_slide` with
         * its id and if it's its quizz or not we need to display.
         *
         * @private
         */
        _onChangeSlideRequest: function (ev) {
            var slideData = ev.data;
            var newSlide = findSlide(this.slides, {
                id: slideData.id,
                isQuiz: slideData.isQuiz || false,
            });
            this._updateSlideValue(newSlide);
        },
        /**
         * After a slide has been marked as completed / uncompleted, update the state
         * of this widget and reload the slide if needed (e.g. to re-show the questions
         * of a quiz).
         *
         * We might need to set multiple slide as completed, because of "isQuiz"
         * set to True / False
         *
         * @private
         * @param {Object} slide: slide to set as completed
         * @param {Boolean} completed: true to mark the slide as completed
         *     false to mark the slide as not completed
         */
        _toggleSlideCompleted: async function (slide, completed = true) {
            await this._super(...arguments);

            const fsSlides = this.slides.filter(_slide => _slide.id === slide.id);

            fsSlides.forEach(slide => slide.completed = completed);

            const currentSlide = this._slideValue;
            if (currentSlide.id === slide.id) {
                currentSlide.completed = completed;
                this._updateSlideValue(currentSlide);

                if ((currentSlide.hasQuestion || currentSlide.type === 'quiz') && !completed) {
                    // Reload the quiz
                    this._renderSlide();
                }
            }
        },
        /**
         * Go the next slide
         *
         * @private
         */
        _onSlideGoToNext: function (ev) {
            this.sidebar.goNext();
        },
        /**
         * Called when the sidebar toggle is clicked -> toggles the sidebar visibility.
         *
         * @private
         */
        _onClickToggleSidebar: function (ev){
            ev.preventDefault();
            this._toggleSidebar();
        },

        _onClickShareSlide: function (ev) {
            const slide = this._slideValue;
            this.call("dialog", "add", SlideShareDialog, {
                category: slide.category,
                documentMaxPage: slide.category == 'document' && this.getDocumentMaxPage(),
                emailSharing: slide.emailSharing === 'True',
                embedCode: slide.embedCode || '',
                id: slide.id,
                isFullscreen: true,
                name: slide.name,
                url: slide.websiteShareUrl,
            });
        },

        /**
         * Toggles sidebar visibility.
         *
         * @private
         */
        _toggleSidebar: function () {
            this.$('.o_wslides_fs_sidebar').toggleClass('o_wslides_fs_sidebar_hidden');
            this.$('.o_wslides_fs_toggle_sidebar').toggleClass('active');
        },
    });

    publicWidget.registry.websiteSlidesFullscreenPlayer = publicWidget.Widget.extend({
        selector: '.o_wslides_fs_main',
        start: function (){
            var proms = [this._super.apply(this, arguments)];
            var fullscreen = new Fullscreen(this, this._getSlides(), this._getCurrentSlideID(), this._extractChannelData());
            proms.push(fullscreen.attachTo(".o_wslides_fs_main"));
            // To prevent double scrollbar due to footer overflow
            document.querySelector('.o_footer')?.classList.add('d-none');
            return proms;
        },
        _extractChannelData: function (){
            return this.$el.data();
        },
        _getCurrentSlideID: function (){
            return parseInt(this.$('.o_wslides_fs_sidebar_list_item.active').data('id'));
        },
        /**
         * @private
         * Creates slides objects from every slide-list-cells attributes
         */
        _getSlides: function (){
            var $slides = this.$('.o_wslides_fs_sidebar_list_item[data-can-access="True"]');
            var slideList = [];
            $slides.each(function () {
                var slideData = $(this).data();
                slideList.push(slideData);
            });
            return slideList;
        },
    });

    export default Fullscreen;

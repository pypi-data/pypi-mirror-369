/* global CopyButtonPlugin */

// Load the required libraries
import hljs from '../libs/highlightjs/11.10.0/es/highlight.min.js';

$(document).ready(() => {
    'use strict';

    /**
     * Extend links to external website.
     * » add target="_blank"
     * » add rel="noopener noreferer"
     */
    const externalLinks = () => {
        // Get the current location hostname
        const internalHost = [location.hostname];

        // Regex pattern to match HTTP and HTTPS
        const protocolPattern = /^https?:\/\//i;

        // Walk through all links on the current page.
        $('a').each((index, element) => {
            // Get the href attribute of the link
            const href = $(element).attr('href');

            // Check if it's an HTTP link
            if (protocolPattern.test(href)) {
                // Get the hostname of the link
                const hrefHostname = $(new URL(href)).attr('hostname');

                // Check if the hostname is not in the internalHost array and add the target and rel attributes to the link element.
                if ($.inArray(hrefHostname, internalHost) === -1) {
                    $(element).attr('target', '_blank');
                    $(element).attr('rel', 'noopener noreferer');
                }
            }
        });
    };


    /**
     * Render a JS clock for EVE time.
     *
     * @param {Element} element The HTML element to display the time
     */
    const renderClock = (element) => {
        const date = new Date();

        /**
         * Date
         * @type {string} 2021-01-01
         */
        // const year = date.getUTCFullYear();
        // const month = String(date.getUTCMonth() + 1).padStart(2, '0');
        // const day = String(date.getUTCDate()).padStart(2, '0');

        /**
         * Time
         * @type {string} 00:00:00
         */
        const hour = String(date.getUTCHours()).padStart(2, '0');
        const minute = String(date.getUTCMinutes()).padStart(2, '0');
        const second = String(date.getUTCSeconds()).padStart(2, '0');

        element.html(hour + ':' + minute + ':' + second);
    };


    /**
     * Check if an element has CSS overflow.
     *
     * Usage:
     * ```js
     * const element = $('#element');
     * const {
     *     overflow, horizontal, vertical
     * } = elementHasOverflow(element);
     * ```
     *
     * @param {Element} element The element to check
     * @returns {{overflow: boolean, horizontal: boolean, vertical: boolean}} An object with the results.
     * `overflow` is true if the element has overflow,
     * `horizontal` is true if the element has horizontal overflow,
     * and `vertical` is true if the element has vertical overflow.
     */
    const elementHasOverflow = (element) => {
        const clientHeight = element[0].clientHeight;
        const scrollHeight = element[0].scrollHeight;
        const clientWidth = element[0].clientWidth;
        const scrollWidth = element[0].scrollWidth;

        return {
            overflow: clientHeight < scrollHeight || clientWidth < scrollWidth,
            horizontal: clientWidth < scrollWidth,
            vertical: clientHeight < scrollHeight
        };
    };


    /**
     * Add classes to elements that have CSS overflow.
     *
     * @param {Element} element The element to check
     */
    const addOverflowClasses = (element) => {
        if (element.length > 0) {
            // Check if the element has overflow
            const {
                overflow, horizontal, vertical
            } = elementHasOverflow(element);

            if (overflow) {
                // Add the overflowing class
                element.addClass(
                    `overflowing${vertical ? ' overflowing-vertically' : ''}${horizontal ? ' overflow-horizontally' : ''}`
                );
            }
        }
    };


    /**
     * Inject a blurred background to the body.
     */
    const injectBlurBodyBackground = () => {
        $('<div class="blur-background"></div>').prependTo('body');
    };


    /**
     * Functions that need to be executed on successful ajax events.
     */
    $(document).ajaxSuccess(() => {
        externalLinks();
    });


    /**
     * Functions that need to be executed when the page is loaded.
     */
    (() => {
        injectBlurBodyBackground();

        // Start the Eve-time clock in the top menu bar.
        setInterval(() => {
            renderClock($('.eve-time-wrapper .eve-time-clock'));
        }, 500);

        externalLinks();

        // Highlight code blocks with highlight.js
        if (typeof hljs !== 'undefined' && typeof hljs.highlightElement === 'function') {
            // Add the copy button plugin to highlight.js
            hljs.addPlugin(new CopyButtonPlugin());

            // Get all code blocks
            const codeBlocks = document.querySelectorAll('pre code');

            // Check if there are code blocks
            if (codeBlocks.length > 0) {
                // Regex to split the language class
                const regexSplit = /^language-/;

                // Loop through all code blocks
                codeBlocks.forEach((block) => {
                    // Get the language of the code block
                    const language = block.className.split(' ')
                        .find(
                            (elementClass) => regexSplit.test(elementClass)
                        ).split('-')[1];

                    // Check if the language is found
                    if (language) {
                        // Highlight the code block
                        hljs.highlightElement(block, {language: language});
                    }
                });
            }
        }

        // Add overflowing CSS classes to the Characters panel on the dashboard.
        addOverflowClasses(
            $('#aa-dashboard-panel-characters div.card-body > div:nth-child(2) > div')
        );

        // Add overflowing CSS classes to the Membership panel on the dashboard.
        addOverflowClasses(
            $('#aa-dashboard-panel-membership div.card-body > div:nth-child(2) > div')
        );

        console.log('Terra Nanotech JS: Loaded');
    })();
});

// ==UserScript==
// @name         Microsoft Learn Focus Mode
// @namespace    http://tampermonkey.net/
// @version      2025-08-24
// @description  Enhances Microsoft Learn with a configurable, movable focus mode button.
// @author       You
// @match        https://learn.microsoft.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=microsoft.com
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // --- CONFIGURATION ---
    // You can easily change the styles applied in focus mode here.
    const styleProfiles = {
        p1: {
            fontFamily: 'MATH, "Cambria Math", serif',
            /*lineHeight: '20px',*/
            /*letterSpacing: '0px',*/
            wordSpacing: '1.5px'
        },
        p2: {
            fontFamily: 'MONOSPACE, "Courier New", monospace',
            /*lineHeight: '20px',*/
            /*letterSpacing: '0px',*/
            wordSpacing: '-1px'
        },
        p3: {
            fontFamily: 'serif, Georgia, "Times New Roman"',
            /*lineHeight: '20px',*/
            /*letterSpacing: '0px',*/
            /*wordSpacing: '1px'*/
        },
        p4: {
            fontFamily: 'Minion Pro',
            font-size: 16px,
            /*lineHeight: '20px',*/
            /*letterSpacing: '0px',*/
            /*wordSpacing: '1px'*/
        }
    };

    // --- EDIT THIS LINE TO CHANGE THE ACTIVE STYLE ---
    const activeProfileName = 'p4'; // Options are: 'p1', 'p2', 'p3'
    // --------------------------------------------------


    setTimeout(() => {
        const activeProfile = styleProfiles[activeProfileName];

        // Dynamically generate the CSS for focus mode
        const cssStyles = `
        body.focus-mode-active {
            display: flex;
        }

        /* Dynamically applied styles for focus mode */
        body.focus-mode-active * {
            font-family: ${activeProfile.fontFamily} !important;
            line-height: ${activeProfile.lineHeight} !important;
            letter-spacing: ${activeProfile.letterSpacing} !important;
            word-spacing: ${activeProfile.wordSpacing} !important;
        }

        .focus-mode-fab {
            position: fixed;
            width: 50px;
            height: 50px;
            background-color: #0078D4;
            color: #FFFFFF;
            border-radius: 50%;
            text-align: center;
            font-size: 24px;
            line-height: 50px;
            cursor: grab;
            z-index: 1000;
            box-shadow: 0 2px 5px 0 rgba(0,0,0,0.26);
            user-select: none;
        }
    `;
        const styleElement = document.createElement('style');
        styleElement.textContent = cssStyles;
        document.head.appendChild(styleElement);

        const focusModeButton = document.querySelector('#ms--focus-mode-button');

        const fab = document.createElement('div');
        fab.classList.add('focus-mode-fab');
        fab.textContent = 'F';
        document.body.appendChild(fab);

        // --- Draggable, Persistent, and Viewport-Aware Position Logic ---
        const ensureFabIsInViewport = () => {
            const rect = fab.getBoundingClientRect();
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            let left = Math.max(0, Math.min(rect.left, viewportWidth - rect.width));
            let top = Math.max(0, Math.min(rect.top, viewportHeight - rect.height));
            fab.style.left = `${left}px`;
            fab.style.top = `${top}px`;
        };

        const savedPosition = JSON.parse(sessionStorage.getItem('fabPosition'));
        if (savedPosition) {
            fab.style.top = savedPosition.top;
            fab.style.left = savedPosition.left;
        } else {
            fab.style.top = '50%';
            fab.style.left = `calc(100% - 60px)`;
        }
        ensureFabIsInViewport();
        window.addEventListener('resize', ensureFabIsInViewport);

        let isDragging = false;
        let hasDragged = false;
        let offsetX, offsetY;

        const startDrag = (e) => {
            isDragging = true;
            hasDragged = false;
            fab.style.cursor = 'grabbing';
            const rect = fab.getBoundingClientRect();
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            document.addEventListener('mousemove', onDrag);
            document.addEventListener('mouseup', stopDrag);
        };

        const onDrag = (e) => {
            if (!isDragging) return;
            hasDragged = true;
            let newLeft = e.clientX - offsetX;
            let newTop = e.clientY - offsetY;
            newLeft = Math.max(0, Math.min(newLeft, window.innerWidth - fab.offsetWidth));
            newTop = Math.max(0, Math.min(newTop, window.innerHeight - fab.offsetHeight));
            fab.style.left = `${newLeft}px`;
            fab.style.top = `${newTop}px`;
        };

        const stopDrag = () => {
            isDragging = false;
            fab.style.cursor = 'grab';
            document.removeEventListener('mousemove', onDrag);
            document.removeEventListener('mouseup', stopDrag);
            if (hasDragged) {
                sessionStorage.setItem('fabPosition', JSON.stringify({ top: fab.style.top, left: fab.style.left }));
            }
        };
        fab.addEventListener('mousedown', startDrag);

        // --- Event Listeners for Focus Mode ---
        if (focusModeButton) {
            const toggleFocusMode = () => document.body.classList.toggle('focus-mode-active');
            focusModeButton.addEventListener('click', toggleFocusMode);
            fab.addEventListener('click', () => !hasDragged && focusModeButton.click());
            document.addEventListener('keydown', (event) => {
                if (event.key === 'f' && !['INPUT', 'TEXTAREA'].includes(event.target.tagName)) {
                    focusModeButton.click();
                }
            });
        }
    }, 1000);
})();

// ==UserScript==
// @name         dotnet tutorial left meny pane
// @namespace    http://tampermonkey.net/
// @version      2024-10-21
// @description  try to take over the world!
// @author       You
// @match        https://dotnettutorials.net/lesson/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=dotnettutorials.net
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    const className = 'current-lesson';
    const listItem = document.querySelector(`ul.${className}`);
    if (listItem) {
        listItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
})();

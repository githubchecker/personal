// ==UserScript==
// @name         Page Search Highlighter
// @namespace    http://tampermonkey.net/
// @version      1.10
// @description  Enable search feature on the current web page and highlight matches
// @author       Your Name
// @match        *://*/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    let searchInput;
    let currentMatchIndex = -1;
    let matches = [];
    let debounceTimeout;

    // Function to create and style the search input
    function createSearchInput(initialValue) {
        searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search...';
        searchInput.style.position = 'fixed';
        searchInput.style.top = '10px';
        searchInput.style.right = '10px';
        searchInput.style.zIndex = '10000';
        searchInput.style.padding = '5px';
        searchInput.style.fontSize = '16px';
        searchInput.style.border = '1px solid #ccc';
        searchInput.style.borderRadius = '4px';
        searchInput.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.2)';
        document.body.appendChild(searchInput);

        // Set initial value and trigger search
        searchInput.value = '';
        debounce(() => highlightMatches(searchInput.value), 300);

        // Handle search input with debounce
        searchInput.addEventListener('input', () => {
            debounce(() => highlightMatches(searchInput.value), 300);
        });

        // Handle Enter key to focus on next match
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                focusNextMatch();
            }
        });

        // Focus the input
        searchInput.focus();
    }

    // Debounce function to delay execution
    function debounce(func, delay) {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(func, delay);
    }

    // Function to highlight matches
    function highlightMatches(query) {
        // Remove existing highlights
        const highlights = document.querySelectorAll('.highlight');
        highlights.forEach(highlight => {
            const parent = highlight.parentNode;
            parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
            parent.normalize();
        });

        matches = [];
        currentMatchIndex = -1;

        if (!query) return;

        // Highlight new matches
        const regex = new RegExp(query, 'gi');
        traverseDOM(document.body, regex);

        // Scroll to the first match
        if (matches.length > 0) {
            focusNextMatch();
        }
    }

    // Recursive function to traverse the DOM and highlight matches
    function traverseDOM(node, regex) {
        if (node.nodeType === Node.TEXT_NODE) {
            let match;
            while ((match = regex.exec(node.nodeValue)) !== null) {
                const span = document.createElement('span');
                span.className = 'highlight';
                span.style.backgroundColor = 'yellow';
                span.style.border = '2px solid red';
                span.textContent = match[0];

                const part1 = document.createTextNode(node.nodeValue.substring(0, match.index));
                const part2 = document.createTextNode(node.nodeValue.substring(match.index + match[0].length));

                const parent = node.parentNode;
                parent.insertBefore(part1, node);
                parent.insertBefore(span, node);
                parent.insertBefore(part2, node);
                parent.removeChild(node);

                matches.push(span);
                node = part2;
                regex.lastIndex = 0; // Reset regex index for the next match in the same node
            }
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            for (let child = node.firstChild; child; child = child.nextSibling) {
                traverseDOM(child, regex);
            }
        }
    }

    // Function to focus on the next match
    function focusNextMatch() {
        if (matches.length === 0) return;
        currentMatchIndex = (currentMatchIndex + 1) % matches.length;
        const match = matches[currentMatchIndex];
        match.scrollIntoView({ behavior: 'smooth', block: 'center' });
        match.style.outline = '2px solid red';
        setTimeout(() => {
            match.style.outline = '';
        }, 1000);
    }

    // Handle keydown event to show search input
    document.addEventListener('keydown', (e) => {
        const activeElement = document.activeElement;
        const isInputFocused = activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA' || activeElement.isContentEditable);
        const isKeyCombination = e.ctrlKey || e.altKey || e.shiftKey;

        if (!searchInput && !isInputFocused && !isKeyCombination && /^[a-z0-9]$/i.test(e.key)) {
            createSearchInput(e.key);
        } else if (e.key === 'Escape' && searchInput) {
            searchInput.value = '';
            highlightMatches('');
            searchInput.remove();
            searchInput = null;
        }
    });
})();

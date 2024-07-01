// ==UserScript==
// @name         Google Photos Auto Delete
// @namespace    http://tampermonkey.net/
// @version      1.3
// @description  Automatically delete Google Photos items based on URL fragment
// @author       Eiko Wagenknecht (eiko-wagenknecht.de)
// @match        *://photos.google.com/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    // Check for the URL fragment
    console.log('Tampermonkey script running');
    const fragment = new URL(window.location.href).hash;
    const deleteFlag = fragment.includes('#delete=');
    console.log(`URL fragment: ${fragment}, deleteFlag: ${deleteFlag}`);

    if (deleteFlag) {
        const expectedPhotoId = fragment.split('=')[1];
        console.log(`Expected Photo ID from URL fragment: ${expectedPhotoId}`);

        // Wait for the page to fully load
        window.addEventListener('load', function () {
            console.log('Page loaded');

            // Extract the actual photo ID from the URL
            const actualPhotoId = new URL(window.location.href).pathname.split('/').pop();
            console.log(`Actual Photo ID from URL: ${actualPhotoId}`);

            // Verify if the actual photo ID matches the expected photo ID
            if (actualPhotoId === expectedPhotoId) {
                console.log('Photo ID matches, proceeding with deletion process');

                // Click the delete button
                const deleteButton = document.querySelector('button[aria-label="Delete"]');
                if (deleteButton) {
                    deleteButton.click();
                    console.log('Delete button clicked');

                    // Wait for the confirmation dialog and click "Move to bin"
                    setTimeout(() => {
                        const moveToBinButton = [...document.querySelectorAll('button')].find(button => button.innerText === 'Move to bin');
                        if (moveToBinButton) {
                            // Clear the URL fragment
                            window.location.hash = '';
                            moveToBinButton.click();
                            console.log('Move to bin button clicked');

                            // Close the tab after deletion
                            setTimeout(() => {
                                window.close();
                            }, 2000);
                        } else {
                            console.error('Move to bin button not found');
                        }
                    }, 2000);  // Adjust timeout as necessary
                } else {
                    console.error('Delete button not found');
                }
            } else {
                console.error('Photo ID does not match, aborting deletion process');
            }
        });
    }
})();

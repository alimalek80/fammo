(function() {
    'use strict';

    // Wait for the DOM to be fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        // Wait a bit for markdownx to initialize
        setTimeout(initMarkdownxSideBySide, 500);
    });

    function initMarkdownxSideBySide() {
        // Find the content field (MarkdownX field)
        const contentField = document.querySelector('textarea[name="content"]');
        if (!contentField) {
            console.log('MarkdownX side-by-side: content field not found');
            return; // Not on a page with the content field
        }

        // Find the markdownx container
        const markdownxOriginal = contentField.closest('.markdownx');
        if (!markdownxOriginal) {
            console.log('MarkdownX side-by-side: .markdownx container not found');
            return;
        }

        // Find the existing markdownx preview element
        const existingPreview = markdownxOriginal.querySelector('.markdownx-preview');
        if (!existingPreview) {
            console.log('MarkdownX side-by-side: preview element not found, will create one');
        }

        // Get the parent container
        const fieldWrapper = markdownxOriginal.parentElement;
        if (!fieldWrapper) {
            console.log('MarkdownX side-by-side: field wrapper not found');
            return;
        }

        // Create the new side-by-side structure
        const container = document.createElement('div');
        container.className = 'markdownx-container';

        // Create sync controls
        const syncControls = document.createElement('div');
        syncControls.className = 'markdownx-sync-controls';
        syncControls.innerHTML = `
            <span class="markdownx-sync-label">Scroll Sync:</span>
            <button type="button" class="markdownx-sync-toggle active" id="markdownx-sync-btn">
                Sync Enabled
            </button>
        `;

        // Create editor wrapper
        const editorWrapper = document.createElement('div');
        editorWrapper.className = 'markdownx-editor-wrapper';

        // Create preview wrapper
        const previewWrapper = document.createElement('div');
        previewWrapper.className = 'markdownx-preview-wrapper';

        // Create or clone the preview
        let newPreview;
        if (existingPreview) {
            newPreview = existingPreview.cloneNode(true);
            newPreview.className = 'markdownx-preview';
        } else {
            newPreview = document.createElement('div');
            newPreview.className = 'markdownx-preview';
            newPreview.innerHTML = '<p><em>Preview will appear here as you type...</em></p>';
        }

        // Add editor class to textarea
        contentField.classList.add('markdownx-editor');

        // Insert container into DOM first (before moving elements)
        fieldWrapper.insertBefore(container, markdownxOriginal);
        
        // Build the structure
        previewWrapper.appendChild(syncControls);
        previewWrapper.appendChild(newPreview);
        
        editorWrapper.appendChild(markdownxOriginal);
        container.appendChild(editorWrapper);
        container.appendChild(previewWrapper);
        
        // Hide the original preview if it exists
        if (existingPreview) {
            existingPreview.style.display = 'none';
        }

        // Setup scroll sync
        let syncEnabled = true;
        const syncBtn = document.getElementById('markdownx-sync-btn');
        let isScrolling = false;
        let scrollTimeout;

        // Toggle sync
        syncBtn.addEventListener('click', function() {
            syncEnabled = !syncEnabled;
            if (syncEnabled) {
                syncBtn.textContent = 'Sync Enabled';
                syncBtn.classList.add('active');
            } else {
                syncBtn.textContent = 'Sync Disabled';
                syncBtn.classList.remove('active');
            }
        });

        // Sync scrolling from editor to preview
        contentField.addEventListener('scroll', function() {
            if (!syncEnabled || isScrolling) return;
            
            isScrolling = true;
            clearTimeout(scrollTimeout);

            const scrollPercentage = contentField.scrollTop / (contentField.scrollHeight - contentField.clientHeight);
            const previewScrollTop = scrollPercentage * (newPreview.scrollHeight - newPreview.clientHeight);
            newPreview.scrollTop = previewScrollTop;

            scrollTimeout = setTimeout(function() {
                isScrolling = false;
            }, 100);
        });

        // Sync scrolling from preview to editor
        newPreview.addEventListener('scroll', function() {
            if (!syncEnabled || isScrolling) return;
            
            isScrolling = true;
            clearTimeout(scrollTimeout);

            const scrollPercentage = newPreview.scrollTop / (newPreview.scrollHeight - newPreview.clientHeight);
            const editorScrollTop = scrollPercentage * (contentField.scrollHeight - contentField.clientHeight);
            contentField.scrollTop = editorScrollTop;

            scrollTimeout = setTimeout(function() {
                isScrolling = false;
            }, 100);
        });

        // Update preview on content change
        contentField.addEventListener('input', function() {
            updatePreview();
        });

        function updatePreview() {
            // The markdownx library handles the preview update automatically
            // We just need to ensure our cloned preview stays in sync with the hidden one
            if (existingPreview) {
                setTimeout(function() {
                    if (existingPreview.innerHTML !== newPreview.innerHTML) {
                        newPreview.innerHTML = existingPreview.innerHTML;
                    }
                }, 100);
            }
        }

        // Monitor for changes to the hidden preview and sync to our visible preview
        if (existingPreview) {
            const observer = new MutationObserver(function(mutations) {
                if (existingPreview.innerHTML !== newPreview.innerHTML) {
                    newPreview.innerHTML = existingPreview.innerHTML;
                }
            });

            observer.observe(existingPreview, {
                childList: true,
                subtree: true,
                characterData: true
            });
        }

        // Initial preview update
        updatePreview();
        
        console.log('MarkdownX side-by-side: initialized successfully');
    }
})();

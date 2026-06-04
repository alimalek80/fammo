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

        // Activate the SEO image-upload modal for this textarea
        initImageUploadModal(contentField);
    }

    // ---------------------------------------------------------------------------
    // SEO Image Upload Modal
    // Intercepts drag-and-drop / paste / button-click image uploads so the user
    // can set a custom SEO-friendly filename AND alt text before the file is sent.
    // ---------------------------------------------------------------------------
    function initImageUploadModal(textarea) {
        // Prefer the URL injected by the admin template (has the correct locale prefix).
        // Falls back to a relative path that still works if LocaleMiddleware isn't active.
        var UPLOAD_URL = (window.BLOG_INLINE_UPLOAD_URL) || '/blog/dashboard/uploads/inline-image/';

        // ---- Build modal DOM (only once) ----
        if (document.getElementById('seo-img-modal')) return; // already exists

        var modal = document.createElement('div');
        modal.id = 'seo-img-modal';
        modal.style.cssText = [
            'display:none', 'position:fixed', 'inset:0',
            'background:rgba(0,0,0,0.55)', 'z-index:999999',
            'align-items:center', 'justify-content:center'
        ].join(';');
        modal.innerHTML = [
            '<div id="seo-img-box" style="background:#fff;border-radius:10px;padding:28px 32px;',
                'width:480px;max-width:92vw;box-shadow:0 24px 64px rgba(0,0,0,0.32);">',
              '<h3 style="margin:0 0 20px;font-size:16px;font-weight:700;color:#111;">',
                '📸 Insert Image with SEO Filename</h3>',
              '<div id="seo-img-preview" style="display:none;text-align:center;margin-bottom:16px;">',
                '<img id="seo-img-preview-img" style="max-height:110px;max-width:100%;',
                    'border-radius:6px;border:1px solid #e0e0e0;">',
              '</div>',
              '<div style="margin-bottom:14px;">',
                '<label style="display:block;font-size:12px;font-weight:700;color:#555;',
                    'text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px;">',
                  'SEO Filename <span style="font-weight:400;color:#888;">(no extension · hyphens only)</span>',
                '</label>',
                '<input id="seo-img-filename" type="text" required ',
                    'placeholder="e.g. golden-retriever-puppy-park" ',
                    'style="width:100%;padding:9px 12px;border:1px solid #ccc;border-radius:6px;',
                        'font-size:14px;box-sizing:border-box;outline:none;">',
                '<p style="margin:5px 0 0;font-size:11px;color:#999;">',
                  'Becomes the URL path — keep it descriptive &amp; keyword-rich.</p>',
              '</div>',
              '<div style="margin-bottom:22px;">',
                '<label style="display:block;font-size:12px;font-weight:700;color:#555;',
                    'text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px;">',
                  'Alt Text',
                '</label>',
                '<input id="seo-img-alt" type="text" ',
                    'placeholder="Describe the image for screen readers &amp; SEO" ',
                    'style="width:100%;padding:9px 12px;border:1px solid #ccc;border-radius:6px;',
                        'font-size:14px;box-sizing:border-box;outline:none;">',
              '</div>',
              '<div id="seo-img-error" style="display:none;margin-bottom:14px;padding:8px 12px;',
                  'background:#fff0f0;border:1px solid #f5c6c6;border-radius:6px;',
                  'font-size:13px;color:#c0392b;"></div>',
              '<div style="display:flex;gap:10px;justify-content:flex-end;">',
                '<button id="seo-img-cancel" type="button" ',
                    'style="padding:9px 20px;border:1px solid #d0d0d0;background:#fff;',
                        'border-radius:6px;cursor:pointer;font-size:14px;color:#444;">',
                  'Cancel',
                '</button>',
                '<button id="seo-img-submit" type="button" ',
                    'style="padding:9px 20px;background:#1971c2;color:#fff;border:none;',
                        'border-radius:6px;cursor:pointer;font-size:14px;font-weight:700;">',
                  'Upload &amp; Insert',
                '</button>',
              '</div>',
            '</div>'
        ].join('');
        document.body.appendChild(modal);

        var currentFile = null;
        var currentTextarea = null;

        function slugify(str) {
            return str
                .replace(/\.[^.]+$/, '')        // strip extension
                .toLowerCase()
                .replace(/[^a-z0-9]+/g, '-')    // non-alphanumeric → hyphen
                .replace(/^-+|-+$/g, '');
        }

        function getCsrf() {
            var m = document.cookie.match(/csrftoken=([^;]+)/);
            return m ? m[1] : (document.querySelector('[name=csrfmiddlewaretoken]') || {}).value || '';
        }

        function showError(msg) {
            var el = document.getElementById('seo-img-error');
            el.textContent = msg;
            el.style.display = 'block';
        }

        function clearError() {
            var el = document.getElementById('seo-img-error');
            el.style.display = 'none';
            el.textContent = '';
        }

        function openModal(file, ta) {
            currentFile = file;
            currentTextarea = ta;
            document.getElementById('seo-img-filename').value = slugify(file.name);
            document.getElementById('seo-img-alt').value = '';
            clearError();
            document.getElementById('seo-img-submit').disabled = false;
            document.getElementById('seo-img-submit').textContent = 'Upload & Insert';

            // Image preview
            var reader = new FileReader();
            reader.onload = function (e) {
                document.getElementById('seo-img-preview-img').src = e.target.result;
                document.getElementById('seo-img-preview').style.display = 'block';
            };
            reader.readAsDataURL(file);

            modal.style.display = 'flex';
            setTimeout(function () {
                document.getElementById('seo-img-filename').focus();
            }, 60);
        }

        function closeModal() {
            modal.style.display = 'none';
            document.getElementById('seo-img-preview').style.display = 'none';
            currentFile = null;
            currentTextarea = null;
        }

        function insertAtCursor(ta, text) {
            var start = ta.selectionStart || 0;
            var end = ta.selectionEnd || 0;
            ta.value = ta.value.slice(0, start) + text + ta.value.slice(end);
            ta.selectionStart = ta.selectionEnd = start + text.length;
            ta.dispatchEvent(new Event('input'));
            ta.focus();
        }

        function doUpload() {
            clearError();
            var filename = document.getElementById('seo-img-filename').value.trim();
            var altText  = document.getElementById('seo-img-alt').value.trim();
            if (!filename) {
                showError('Please enter an SEO filename.');
                document.getElementById('seo-img-filename').focus();
                return;
            }
            if (!currentFile) return;

            var btn = document.getElementById('seo-img-submit');
            btn.disabled = true;
            btn.textContent = 'Uploading…';

            var fd = new FormData();
            fd.append('image', currentFile);
            fd.append('custom_filename', filename);

            fetch(UPLOAD_URL, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrf() },
                body: fd
            })
            .then(function (r) {
                if (!r.ok) throw new Error('Server error ' + r.status);
                return r.json();
            })
            .then(function (data) {
                if (data.error) throw new Error(data.error);
                var alt = altText || filename;
                insertAtCursor(currentTextarea, '![' + alt + '](' + data.url + ')');
                closeModal();
            })
            .catch(function (err) {
                showError('Upload failed: ' + err.message);
                btn.disabled = false;
                btn.textContent = 'Upload & Insert';
            });
        }

        // Wire buttons
        document.getElementById('seo-img-cancel').addEventListener('click', closeModal);
        document.getElementById('seo-img-submit').addEventListener('click', doUpload);

        // Close on backdrop click
        modal.addEventListener('click', function (e) {
            if (e.target === modal) closeModal();
        });

        // Keyboard shortcuts inside modal
        modal.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') { closeModal(); }
            if (e.key === 'Enter' && document.activeElement !== document.getElementById('seo-img-cancel')) {
                e.preventDefault();
                doUpload();
            }
        });

        // ---- Intercept drop on the markdownx textarea (capture phase) ----
        textarea.addEventListener('drop', function (e) {
            var files = e.dataTransfer ? e.dataTransfer.files : null;
            if (!files || !files.length) return;
            var images = Array.prototype.filter.call(files, function (f) {
                return f.type.startsWith('image/');
            });
            if (!images.length) return;
            e.preventDefault();
            e.stopPropagation();
            openModal(images[0], textarea);
        }, true); // capture = true beats markdownx listeners

        // ---- Intercept paste on the markdownx textarea (capture phase) ----
        textarea.addEventListener('paste', function (e) {
            var files = e.clipboardData ? e.clipboardData.files : null;
            if (!files || !files.length) return;
            var images = Array.prototype.filter.call(files, function (f) {
                return f.type.startsWith('image/');
            });
            if (!images.length) return;
            e.preventDefault();
            e.stopPropagation();
            openModal(images[0], textarea);
        }, true);

        // ---- Add "Insert Image (SEO)" button above the editor ----
        var fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.style.display = 'none';
        fileInput.addEventListener('change', function () {
            if (fileInput.files && fileInput.files[0]) {
                openModal(fileInput.files[0], textarea);
                fileInput.value = '';
            }
        });

        var insertBtn = document.createElement('button');
        insertBtn.type = 'button';
        insertBtn.innerHTML = '&#128247;';
        insertBtn.title = 'Insert Image (SEO) — set a custom filename & alt text';
        insertBtn.style.cssText = [
            'display:inline-flex', 'align-items:center', 'gap:4px',
            'padding:3px 8px', 'background:#1971c2', 'color:#fff',
            'border:none', 'border-radius:4px', 'cursor:pointer',
            'font-size:15px', 'line-height:1', 'white-space:nowrap',
            'width:auto'
        ].join(';');
        insertBtn.addEventListener('click', function () { fileInput.click(); });

        // Wrap in a slim bar that only spans the editor half (left side)
        var btnBar = document.createElement('div');
        btnBar.style.cssText = [
            'display:flex', 'align-items:center',
            'margin-bottom:4px', 'gap:6px'
        ].join(';');
        btnBar.appendChild(fileInput);
        btnBar.appendChild(insertBtn);

        var editorWrapperEl = textarea.closest('.markdownx-editor-wrapper') ||
                              textarea.closest('.markdownx-container') ||
                              textarea.closest('.markdownx') ||
                              textarea.parentElement;
        if (editorWrapperEl && editorWrapperEl.parentElement) {
            editorWrapperEl.parentElement.insertBefore(btnBar, editorWrapperEl);
        }
    }
})();

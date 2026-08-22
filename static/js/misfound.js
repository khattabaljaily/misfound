/**
 * Reads a translated UI string from window.MF_I18N (populated by base.html
 * via {% trans %} for the active session language), falling back to the
 * Arabic literal if the key is missing.
 */
function mfI18n(key, fallback) {
    return (window.MF_I18N && window.MF_I18N[key]) || fallback;
}

/* =================================================================
   Toasts
   ================================================================= */
var MF_TOAST_ICONS = {
    success: 'bi-check-circle-fill',
    error: 'bi-x-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    info: 'bi-info-circle-fill',
};

function mfToastContainer() {
    var el = document.querySelector('.mf-toast-container');
    if (!el) {
        el = document.createElement('div');
        el.className = 'mf-toast-container';
        document.body.appendChild(el);
    }
    return el;
}

function showToast(type, message) {
    type = MF_TOAST_ICONS[type] ? type : 'info';
    var container = mfToastContainer();

    var toast = document.createElement('div');
    toast.className = 'mf-toast mf-toast--' + type;
    toast.innerHTML =
        '<i class="bi ' + MF_TOAST_ICONS[type] + ' mf-toast__icon"></i>' +
        '<div class="mf-toast__body"></div>' +
        '<button type="button" class="mf-toast__close" aria-label="' + mfI18n('close', 'إغلاق') + '">&times;</button>';
    toast.querySelector('.mf-toast__body').textContent = message;

    container.appendChild(toast);
    requestAnimationFrame(function () { toast.classList.add('mf-toast--show'); });

    function dismiss() {
        toast.classList.remove('mf-toast--show');
        setTimeout(function () { toast.remove(); }, 250);
    }

    toast.querySelector('.mf-toast__close').addEventListener('click', dismiss);
    setTimeout(dismiss, 5000);
}

/** Picks up Django messages rendered as JSON by base.html and shows them as toasts. */
function mfShowServerMessages() {
    var el = document.getElementById('django-messages-data');
    if (!el) return;
    try {
        var messages = JSON.parse(el.textContent);
    } catch (e) {
        return;
    }
    var typeMap = { debug: 'info', info: 'info', success: 'success', warning: 'warning', error: 'error' };
    messages.forEach(function (m, i) {
        setTimeout(function () { showToast(typeMap[m.tags] || 'info', m.text); }, i * 150);
    });
}

/* =================================================================
   Confirm modal
   ================================================================= */
function mfConfirm(options) {
    var modalEl = document.getElementById('mfConfirmModal');
    if (!modalEl) return;

    modalEl.querySelector('.mf-confirm-title').textContent = options.title || mfI18n('confirmTitle', 'تأكيد العملية');
    modalEl.querySelector('.mf-confirm-message').textContent = options.message || mfI18n('confirmMessage', 'هل أنت متأكد؟');

    var confirmBtn = modalEl.querySelector('.mf-confirm-btn');
    confirmBtn.textContent = options.confirmLabel || mfI18n('confirmLabel', 'تأكيد');
    confirmBtn.className = 'btn mf-confirm-btn ' + (options.confirmVariant || 'btn-primary');

    var modal = bootstrap.Modal.getOrCreateInstance(modalEl);

    var newBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newBtn, confirmBtn);
    newBtn.addEventListener('click', function () {
        modal.hide();
        options.onConfirm && options.onConfirm();
    });

    modal.show();
}

/* =================================================================
   Global page loader — the centered ring overlay. Ref-counted so several
   concurrent operations don't hide it prematurely, and shown after a short
   delay rather than instantly so a fast operation never just flashes it
   (the same reasoning ELINK's version uses). Reserved for real full-page
   navigations and genuinely significant waits (report submission, the
   kind of AI-matching call that can take seconds) — deliberately NOT
   wired to every small, frequent action (sending a chat message, opening
   the notifications dropdown, tweaking a Browse filter), which keep their
   own local button-spinner/dimming feedback instead so the screen isn't
   blurred out for something that settles in well under a second.
   ================================================================= */
var mfPageLoader = (function () {
    var SHOW_DELAY = 150;
    var activeCount = 0;
    var showTimer = null;

    function el() {
        return document.getElementById('mf-page-loader');
    }

    function start() {
        activeCount++;
        if (activeCount > 1) return;
        clearTimeout(showTimer);
        showTimer = setTimeout(function () {
            var overlay = el();
            if (overlay) overlay.classList.add('is-visible');
        }, SHOW_DELAY);
    }

    function done() {
        activeCount = Math.max(0, activeCount - 1);
        if (activeCount > 0) return;
        clearTimeout(showTimer);
        var overlay = el();
        if (overlay) overlay.classList.remove('is-visible');
    }

    /** Forces the counter and overlay back to idle, regardless of how many
     * start() calls are outstanding. Used as the bfcache/pageshow safety net. */
    function reset() {
        activeCount = 0;
        clearTimeout(showTimer);
        var overlay = el();
        if (overlay) overlay.classList.remove('is-visible');
    }

    return { start: start, done: done, reset: reset };
})();

/* =================================================================
   AJAX helpers
   ================================================================= */
function mfGetCookie(name) {
    var match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? decodeURIComponent(match[2]) : null;
}

/**
 * Puts a button into (or out of) a loading state: swaps its content for the
 * branded spinner and disables it so it can't be double-submitted. Also
 * arms a watchdog timeout so that if some code path forgets to call this
 * with `loading: false` (a bug class this exists specifically to contain),
 * the button un-sticks itself instead of spinning forever.
 *
 * This is purely local to the button — it does not touch the big overlay
 * (see mfPageLoader above for why). Callers that represent a real
 * navigation-like transition (ajaxForm) trigger the overlay themselves
 * alongside this.
 */
function mfSetButtonLoading(btn, loading) {
    if (!btn) return;
    clearTimeout(btn._mfWatchdog);
    if (loading) {
        btn.dataset.originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="mf-spinner"></span> ' + (btn.dataset.loadingText || mfI18n('loading', 'جاري التنفيذ...'));
        btn._mfWatchdog = setTimeout(function () { mfSetButtonLoading(btn, false); }, 20000);
    } else {
        btn.disabled = false;
        if (btn.dataset.originalHtml) btn.innerHTML = btn.dataset.originalHtml;
    }
}

/**
 * Submits a <form> via fetch instead of a full page load.
 *  - On a JSON {success:true, redirect} response, navigates to `redirect`.
 *  - On a JSON {success:true, message} response (no redirect), shows a toast
 *    and calls onSuccess(data).
 *  - On any other (non-JSON / error) response, swaps the form's parent
 *    container innerHTML with the returned HTML (re-rendered form with
 *    Django's validation errors) and re-runs `afterSwap` so widgets like
 *    Choices.js get re-initialised on the fresh markup.
 */
function ajaxForm(form, options) {
    options = options || {};
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        var submitBtn = form.querySelector('button[type="submit"], button:not([type])');
        mfSetButtonLoading(submitBtn, true);
        // These forms (login, register, "I think this is mine", report
        // creation — the last one can genuinely take a few seconds for its
        // AI matching call) represent a real transition, unlike the small
        // frequent actions mfSetButtonLoading otherwise covers on its own,
        // so the overlay is opted into explicitly here.
        mfPageLoader.start();

        fetch(form.action || window.location.href, {
            method: form.method || 'POST',
            body: new FormData(form),
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
            .then(function (response) {
                var contentType = response.headers.get('content-type') || '';
                if (contentType.indexOf('application/json') !== -1) {
                    return response.json().then(function (data) { return { data: data }; });
                }
                return response.text().then(function (html) { return { html: html }; });
            })
            .then(function (result) {
                mfSetButtonLoading(submitBtn, false);
                if (result.data) {
                    if (result.data.success) {
                        if (result.data.redirect) {
                            // Leave the overlay showing — a real navigation is
                            // about to happen, and the destination page picks
                            // up showing it itself from its own first paint.
                            window.location = result.data.redirect;
                        } else {
                            mfPageLoader.done();
                            if (result.data.message) showToast('success', result.data.message);
                            options.onSuccess && options.onSuccess(result.data);
                        }
                    } else {
                        mfPageLoader.done();
                        if (result.data.message) showToast('error', result.data.message);
                        options.onError && options.onError(result.data);
                    }
                    return;
                }
                mfPageLoader.done();
                var container = options.swapTarget ? document.querySelector(options.swapTarget) : form.parentElement;
                container.innerHTML = result.html;
                options.afterSwap && options.afterSwap(container);
                showToast('error', mfI18n('reviewNeeded', 'توجد بيانات تحتاج إلى مراجعة، يرجى التحقق من الحقول أدناه.'));
            })
            .catch(function () {
                mfSetButtonLoading(submitBtn, false);
                mfPageLoader.done();
                showToast('error', mfI18n('connectionError', 'حدث خطأ في الاتصال، يرجى المحاولة مرة أخرى.'));
            });
    });
}

/* =================================================================
   Searchable selects (Choices.js) + country -> city cascade
   ================================================================= */
function misfoundChoicesConfig() {
    return {
        searchEnabled: true,
        shouldSort: false,
        itemSelectText: '',
        searchPlaceholderValue: mfI18n('searchPlaceholder', 'اكتب للبحث...'),
        noResultsText: mfI18n('noResults', 'لا توجد نتائج'),
        noChoicesText: mfI18n('noChoices', 'لا توجد خيارات'),
        loadingText: mfI18n('loadingText', 'جاري التحميل...'),
        removeItemButton: false,
    };
}

/**
 * Choices.js ships full RTL styling (arrow side, text padding, dropdown
 * alignment) but only activates it when the `.choices` wrapper itself has
 * dir="rtl" — it doesn't inherit that from an ancestor like normal CSS, so
 * we set it explicitly on every instance we create, matching the page's
 * actual direction rather than assuming RTL.
 */
function mfNewChoices(selectEl, config) {
    var instance = new Choices(selectEl, config || misfoundChoicesConfig());
    var wrapper = selectEl.closest('.choices');
    if (wrapper) wrapper.setAttribute('dir', document.documentElement.dir || 'rtl');
    return instance;
}

function initChoicesOn(root) {
    if (typeof Choices === 'undefined') return;
    (root || document).querySelectorAll('select[data-choices]').forEach(function (el) {
        mfNewChoices(el);
    });
}

/**
 * Wires a country <select> to a dependent city <select>: on country change,
 * fetches that country's cities from `citiesUrl` and repopulates the city
 * list (searchable via Choices.js if available).
 */
function initCityCascade(countrySelectId, citySelectId, citiesUrl, emptyLabel) {
    var countryEl = document.getElementById(countrySelectId);
    var cityEl = document.getElementById(citySelectId);
    if (!countryEl || !cityEl) return;
    emptyLabel = emptyLabel || mfI18n('chooseCity', 'اختر المدينة');

    var initialCountry = countryEl.value;
    var initialCity = cityEl.value;

    var hasChoices = typeof Choices !== 'undefined';
    var countryChoices = hasChoices ? mfNewChoices(countryEl) : null;
    var cityChoices = hasChoices ? mfNewChoices(cityEl) : null;

    function setCityDisabled(disabled) {
        if (cityChoices) {
            disabled ? cityChoices.disable() : cityChoices.enable();
        } else {
            cityEl.disabled = disabled;
        }
    }

    function setCityOptions(cities, selectedId) {
        var options = [{ value: '', label: emptyLabel, selected: !selectedId }];
        cities.forEach(function (city) {
            options.push({
                value: String(city.id),
                label: city.name,
                selected: String(city.id) === String(selectedId),
            });
        });

        if (cityChoices) {
            cityChoices.clearStore();
            cityChoices.setChoices(options, 'value', 'label', true);
        } else {
            cityEl.innerHTML = '';
            options.forEach(function (opt) {
                var el = document.createElement('option');
                el.value = opt.value;
                el.textContent = opt.label;
                el.selected = opt.selected;
                cityEl.appendChild(el);
            });
        }
        setCityDisabled(cities.length === 0);
    }

    function loadCities(countryId, selectedCityId) {
        if (!countryId) {
            setCityOptions([]);
            return;
        }
        fetch(citiesUrl + '?country=' + encodeURIComponent(countryId))
            .then(function (r) { return r.json(); })
            .then(function (cities) { setCityOptions(cities, selectedCityId); })
            .catch(function () {
                showToast('error', mfI18n('connectionError', 'حدث خطأ في الاتصال، يرجى المحاولة مرة أخرى.'));
            });
    }

    countryEl.addEventListener('change', function () { loadCities(this.value); });

    if (initialCountry) {
        loadCities(initialCountry, initialCity);
    } else {
        setCityDisabled(true);
    }
}

/**
 * Wires up drag-and-drop multi-image uploaders (report create/edit form).
 * Keeps a JS-side list of newly selected File objects (since a native
 * <input type=file> FileList can't be edited in place), rebuilds the
 * input's FileList via DataTransfer on every add/remove so the right files
 * still go out with the form submit, and lets existing (already-uploaded)
 * images be deleted immediately via AJAX rather than waiting for submit.
 */
function mfInitImageUploader(root) {
    (root || document).querySelectorAll('[data-mf-uploader]').forEach(function (uploader) {
        if (uploader.dataset.mfUploaderInit) return;
        uploader.dataset.mfUploaderInit = '1';

        var max = parseInt(uploader.dataset.max, 10) || 3;
        var input = uploader.querySelector('[data-mf-uploader-input]');
        var dropzone = uploader.querySelector('[data-mf-uploader-dropzone]');
        var previews = uploader.querySelector('[data-mf-uploader-previews]');
        var countEl = uploader.querySelector('[data-mf-uploader-count]');
        var existingEl = uploader.querySelector('[data-mf-uploader-existing]');

        var existingCount = existingEl ? existingEl.querySelectorAll('[data-existing-image]').length : 0;
        var selectedFiles = [];

        function updateCount() {
            var total = existingCount + selectedFiles.length;
            if (countEl) countEl.textContent = total;
            dropzone.classList.toggle('is-full', total >= max);
        }

        function syncInput() {
            var dt = new DataTransfer();
            selectedFiles.forEach(function (f) { dt.items.add(f); });
            input.files = dt.files;
        }

        function renderPreviews() {
            previews.innerHTML = '';
            selectedFiles.forEach(function (file, index) {
                var thumb = document.createElement('div');
                thumb.className = 'mf-uploader__thumb';
                var img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.alt = '';
                var removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'mf-uploader__remove';
                removeBtn.setAttribute('aria-label', mfI18n('removeImage', 'حذف الصورة'));
                removeBtn.innerHTML = '<i class="bi bi-x-lg"></i>';
                removeBtn.addEventListener('click', function () {
                    selectedFiles.splice(index, 1);
                    syncInput();
                    renderPreviews();
                });
                thumb.appendChild(img);
                thumb.appendChild(removeBtn);
                previews.appendChild(thumb);
            });
            updateCount();
        }

        function addFiles(fileList) {
            var room = max - existingCount - selectedFiles.length;
            var files = Array.prototype.slice.call(fileList);
            var accepted = [];
            var rejectedType = false;
            files.forEach(function (f) {
                if (!f.type || f.type.indexOf('image/') !== 0) {
                    rejectedType = true;
                    return;
                }
                accepted.push(f);
            });
            if (rejectedType) showToast('error', mfI18n('invalidImageType', 'يرجى اختيار صور فقط.'));
            if (accepted.length > Math.max(room, 0)) {
                showToast('error', mfI18n('maxImages', 'يمكن رفع 3 صور كحد أقصى.'));
                accepted = accepted.slice(0, Math.max(room, 0));
            }
            selectedFiles = selectedFiles.concat(accepted);
            syncInput();
            renderPreviews();
        }

        input.addEventListener('change', function () {
            addFiles(input.files);
        });

        ['dragover', 'dragenter'].forEach(function (evt) {
            dropzone.addEventListener(evt, function (e) {
                e.preventDefault();
                dropzone.classList.add('is-dragover');
            });
        });
        ['dragleave', 'dragend'].forEach(function (evt) {
            dropzone.addEventListener(evt, function () { dropzone.classList.remove('is-dragover'); });
        });
        dropzone.addEventListener('drop', function (e) {
            e.preventDefault();
            dropzone.classList.remove('is-dragover');
            if (e.dataTransfer && e.dataTransfer.files) addFiles(e.dataTransfer.files);
        });

        if (existingEl) {
            existingEl.querySelectorAll('.mf-existing-image-delete-btn').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    btn.disabled = true;
                    fetch(btn.dataset.url, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': mfGetCookie('csrftoken'),
                        },
                    })
                        .then(function (r) { return r.json(); })
                        .then(function (data) {
                            if (data.success) {
                                btn.closest('[data-existing-image]').remove();
                                existingCount -= 1;
                                updateCount();
                            } else {
                                btn.disabled = false;
                                showToast('error', mfI18n('connectionError', 'حدث خطأ في الاتصال، يرجى المحاولة مرة أخرى.'));
                            }
                        })
                        .catch(function () {
                            btn.disabled = false;
                            showToast('error', mfI18n('connectionError', 'حدث خطأ في الاتصال، يرجى المحاولة مرة أخرى.'));
                        });
                });
            });
        }

        updateCount();
    });
}

/* =================================================================
   Sitewide navigation feedback
   ================================================================= */

/**
 * Shows the page loader overlay for a real, full-page navigation triggered
 * by clicking an <a>. Deliberately skips links a page has already handled
 * itself (checked via e.defaultPrevented, which will already be true by the
 * time this runs if a closer listener — e.g. AJAX pagination — called
 * preventDefault(), since bubbling always reaches the target's own
 * listeners before this document-level one), new-tab opens, in-page
 * anchors, and non-http(s) links.
 */
document.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var link = e.target.closest('a[href]');
    if (!link || link.target === '_blank' || link.hasAttribute('download')) return;

    var href = link.getAttribute('href');
    if (!href || href.charAt(0) === '#' || /^(mailto|tel|javascript):/i.test(href)) return;
    if (link.origin && link.origin !== window.location.origin) return;

    mfPageLoader.start();
});

/**
 * Same idea for plain (non-AJAX) form submits — every AJAX form in this app
 * calls preventDefault() in its own submit handler before this document-level
 * one runs, so this only ever fires for forms that are genuinely about to
 * navigate the page away (e.g. the ownership-verify and rating forms).
 */
document.addEventListener('submit', function (e) {
    if (e.defaultPrevented) return;
    mfPageLoader.start();
});

/**
 * `pageshow` fires on every page display — a fresh load, AND a browser
 * back/forward restore from bfcache. That second case is exactly the bug
 * this exists to close: bfcache freezes the DOM (and any spinner/dimmed
 * state) exactly as it was the moment the user navigated away, and nothing
 * else in this app would ever re-run to clear it. This is the single
 * recovery point for that — plus a general safety net for anything left
 * mid-loading for any other reason.
 */
window.addEventListener('pageshow', function () {
    mfPageLoader.reset();

    document.querySelectorAll('button[disabled]').forEach(function (btn) {
        if (btn.dataset.originalHtml) mfSetButtonLoading(btn, false);
    });

    document.querySelectorAll('.mf-loading').forEach(function (el) {
        el.classList.remove('mf-loading');
    });

    document.querySelectorAll('.mf-filter-spinner').forEach(function (spinner) {
        spinner.classList.add('d-none');
    });
    document.querySelectorAll('.mf-filter-label').forEach(function (label) {
        label.classList.remove('d-none');
    });
});

document.addEventListener('DOMContentLoaded', function () {
    initChoicesOn(document);
    mfShowServerMessages();
});

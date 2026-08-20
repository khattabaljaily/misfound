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
        '<button type="button" class="mf-toast__close" aria-label="إغلاق">&times;</button>';
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

    modalEl.querySelector('.mf-confirm-title').textContent = options.title || 'تأكيد العملية';
    modalEl.querySelector('.mf-confirm-message').textContent = options.message || 'هل أنت متأكد؟';

    var confirmBtn = modalEl.querySelector('.mf-confirm-btn');
    confirmBtn.textContent = options.confirmLabel || 'تأكيد';
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
   AJAX helpers
   ================================================================= */
function mfGetCookie(name) {
    var match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? decodeURIComponent(match[2]) : null;
}

function mfSetButtonLoading(btn, loading) {
    if (!btn) return;
    if (loading) {
        btn.dataset.originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="mf-spinner"></span> ' + (btn.dataset.loadingText || 'جاري التنفيذ...');
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
                            window.location = result.data.redirect;
                        } else {
                            if (result.data.message) showToast('success', result.data.message);
                            options.onSuccess && options.onSuccess(result.data);
                        }
                    } else {
                        if (result.data.message) showToast('error', result.data.message);
                        options.onError && options.onError(result.data);
                    }
                    return;
                }
                var container = options.swapTarget ? document.querySelector(options.swapTarget) : form.parentElement;
                container.innerHTML = result.html;
                options.afterSwap && options.afterSwap(container);
                showToast('error', 'توجد بيانات تحتاج إلى مراجعة، يرجى التحقق من الحقول أدناه.');
            })
            .catch(function () {
                mfSetButtonLoading(submitBtn, false);
                showToast('error', 'حدث خطأ في الاتصال، يرجى المحاولة مرة أخرى.');
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
        searchPlaceholderValue: 'اكتب للبحث...',
        noResultsText: 'لا توجد نتائج',
        noChoicesText: 'لا توجد خيارات',
        loadingText: 'جاري التحميل...',
        removeItemButton: false,
    };
}

/**
 * Choices.js ships full RTL styling (arrow side, text padding, dropdown
 * alignment) but only activates it when the `.choices` wrapper itself has
 * dir="rtl" — it doesn't inherit that from an ancestor like normal CSS, so
 * we set it explicitly on every instance we create.
 */
function mfNewChoices(selectEl, config) {
    var instance = new Choices(selectEl, config || misfoundChoicesConfig());
    var wrapper = selectEl.closest('.choices');
    if (wrapper) wrapper.setAttribute('dir', 'rtl');
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
    emptyLabel = emptyLabel || 'اختر المدينة';

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
                label: city.name_ar,
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
            .then(function (cities) { setCityOptions(cities, selectedCityId); });
    }

    countryEl.addEventListener('change', function () { loadCities(this.value); });

    if (initialCountry) {
        loadCities(initialCountry, initialCity);
    } else {
        setCityDisabled(true);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    initChoicesOn(document);
    mfShowServerMessages();
});

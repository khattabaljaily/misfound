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
    var countryChoices = hasChoices ? new Choices(countryEl, misfoundChoicesConfig()) : null;
    var cityChoices = hasChoices ? new Choices(cityEl, misfoundChoicesConfig()) : null;

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
    if (typeof Choices === 'undefined') return;
    document.querySelectorAll('select[data-choices]').forEach(function (el) {
        new Choices(el, misfoundChoicesConfig());
    });
});

// ===== i18n Engine =====
(function () {
  const STORAGE_KEY = 'qo-locale';
  const SUPPORTED = ['th', 'en'];
  const DEFAULT = 'th';

  let currentLocale = DEFAULT;
  let translations = {};
  let priceDisplay = '';

  // --- Locale resolution ---
  function resolveLocale() {
    // 1. localStorage
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && SUPPORTED.includes(stored)) return stored;

    // 2. Browser language
    const lang = (navigator.language || '').slice(0, 2).toLowerCase();
    if (lang === 'th') return 'th';

    // 3. Timezone
    try {
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      if (tz === 'Asia/Bangkok') return 'th';
    } catch (e) { /* ignore */ }

    // 4. Default
    return DEFAULT;
  }

  // --- Load translations ---
  async function loadTranslations(locale) {
    try {
      const res = await fetch(`locales/${locale}.json`);
      if (!res.ok) throw new Error(res.status);
      translations = await res.json();
    } catch (err) {
      console.error(`i18n: failed to load ${locale}.json`, err);
      translations = {};
    }
  }

  // --- Get nested key ---
  function getKey(key) {
    return key.split('.').reduce((obj, k) => (obj && obj[k] !== undefined ? obj[k] : null), translations);
  }

  // --- Public t() ---
  function t(key) {
    const val = getKey(key);
    if (typeof val !== 'string') return key;
    return val.replace('{price}', priceDisplay);
  }

  // --- Apply translations to DOM ---
  function applyTranslations() {
    // data-i18n: set textContent
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      var val = getKey(key);
      if (typeof val === 'string') {
        el.textContent = val.replace('{price}', priceDisplay);
      }
    });

    // data-i18n-html: set innerHTML
    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-html');
      var val = getKey(key);
      if (typeof val === 'string') {
        el.innerHTML = val.replace('{price}', priceDisplay);
      }
    });

    // data-i18n-list: replace <li> children from array
    document.querySelectorAll('[data-i18n-list]').forEach(function (ul) {
      var key = ul.getAttribute('data-i18n-list');
      var arr = getKey(key);
      if (!Array.isArray(arr)) return;
      var items = ul.querySelectorAll('li');
      arr.forEach(function (text, i) {
        if (items[i]) items[i].textContent = text;
      });
    });

    // data-i18n-group: container whose children have data-i18n-field
    document.querySelectorAll('[data-i18n-group]').forEach(function (group) {
      var baseKey = group.getAttribute('data-i18n-group');
      var items = getKey(baseKey);
      if (!Array.isArray(items)) return;
      var children = group.querySelectorAll('[data-i18n-index]');
      children.forEach(function (child) {
        var idx = parseInt(child.getAttribute('data-i18n-index'), 10);
        var field = child.getAttribute('data-i18n-field');
        if (items[idx] && items[idx][field] !== undefined) {
          child.textContent = items[idx][field];
        }
      });
    });

    // Update <title> from data-i18n-title on <html>
    var titleKey = document.documentElement.getAttribute('data-i18n-title');
    if (titleKey) {
      var metaTitle = getKey(titleKey);
      if (metaTitle) document.title = metaTitle;
    }

    // Update <meta description> from data-i18n-desc on <html>
    var descKey = document.documentElement.getAttribute('data-i18n-desc');
    if (descKey) {
      var metaDesc = getKey(descKey);
      if (metaDesc) {
        var descTag = document.querySelector('meta[name="description"]');
        if (descTag) descTag.setAttribute('content', metaDesc);
      }
    }

    // Update <html lang>
    document.documentElement.lang = currentLocale;

    // Update body class for locale-specific styles
    document.body.classList.remove('locale-th', 'locale-en');
    document.body.classList.add('locale-' + currentLocale);

    // Update locale switcher label
    updateSwitcherLabel();

    // Remove anti-FOUC class
    document.documentElement.classList.remove('i18n-loading');
  }

  // --- Switcher label ---
  function updateSwitcherLabel() {
    document.querySelectorAll('.locale-switch').forEach(function (btn) {
      btn.textContent = currentLocale === 'th' ? 'EN' : 'TH';
    });
  }

  // --- Set locale ---
  async function setLocale(locale) {
    if (!SUPPORTED.includes(locale)) return;
    currentLocale = locale;
    localStorage.setItem(STORAGE_KEY, locale);
    await loadTranslations(locale);
    applyTranslations();
  }

  // --- Set price display (called by script.js after pricing API) ---
  function setPriceDisplay(display) {
    priceDisplay = display || '';
    // Re-apply only price-related elements
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      var val = getKey(key);
      if (typeof val === 'string' && val.indexOf('{price}') !== -1) {
        el.textContent = val.replace('{price}', priceDisplay);
      }
    });
  }

  // --- Init ---
  async function init() {
    currentLocale = resolveLocale();
    await loadTranslations(currentLocale);
    applyTranslations();

    // Bind locale switcher clicks
    document.querySelectorAll('.locale-switch').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var next = currentLocale === 'th' ? 'en' : 'th';
        setLocale(next);
      });
    });
  }

  // --- Expose API ---
  window.i18n = {
    t: t,
    setLocale: setLocale,
    getLocale: function () { return currentLocale; },
    setPriceDisplay: setPriceDisplay,
  };

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

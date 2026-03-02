// ===== Config =====
const API_URL = '';

// ===== Locale currency detection =====
const TIMEZONE_CURRENCY_MAP = {
  'Asia/Bangkok': 'thb',
  'Asia/Ho_Chi_Minh': 'vnd',
  'Asia/Saigon': 'vnd',
  'Asia/Singapore': 'sgd',
  'Asia/Kuala_Lumpur': 'myr',
  'Asia/Manila': 'php',
  'Asia/Jakarta': 'idr',
  'Asia/Tokyo': 'jpy',
  'Asia/Seoul': 'krw',
  'Europe/London': 'gbp',
  'Europe/Paris': 'eur',
  'Europe/Berlin': 'eur',
  'Europe/Amsterdam': 'eur',
  'Europe/Rome': 'eur',
  'Europe/Madrid': 'eur',
  'Europe/Brussels': 'eur',
  'Europe/Vienna': 'eur',
  'Europe/Dublin': 'eur',
  'Europe/Helsinki': 'eur',
  'Europe/Lisbon': 'eur',
};

function detectCurrency() {
  try {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    return TIMEZONE_CURRENCY_MAP[tz] || 'usd';
  } catch {
    return 'usd';
  }
}

let detectedCurrency = detectCurrency();

async function loadLocalPricing() {
  try {
    const res = await fetch(`${API_URL}/pricing?currency=${detectedCurrency}`);
    const data = await res.json();
    detectedCurrency = data.currency;

    document.querySelectorAll('.product__price').forEach(el => {
      el.textContent = data.display;
    });

    if (window.i18n) {
      window.i18n.setPriceDisplay(data.display);
    } else {
      document.querySelectorAll('[data-checkout]').forEach(btn => {
        btn.textContent = `Get the Playbook — ${data.display}`;
      });
    }
  } catch (err) {
    console.error('Failed to load local pricing:', err);
  }
}

loadLocalPricing();

// ===== Scroll animations =====
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      observer.unobserve(e.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

// ===== Nav scroll state =====
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

// ===== Smooth scroll for anchor links =====
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const href = a.getAttribute('href');
    if (href === '#' || href.length < 2) return;
    const target = document.querySelector(href);
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  });
});

// ===== Stripe Checkout =====
document.querySelectorAll('[data-checkout]').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    e.preventDefault();
    const originalText = btn.textContent;
    btn.textContent = window.i18n ? window.i18n.t('checkout.redirecting') : 'Redirecting…';
    btn.style.pointerEvents = 'none';

    const locale = window.i18n ? window.i18n.getLocale() : 'en';

    try {
      const res = await fetch(`${API_URL}/create-checkout-session/playbook`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ currency: detectedCurrency, locale }),
      });
      const data = await res.json();

      if (data.url) {
        window.location.href = data.url;
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (err) {
      console.error('Checkout error:', err);
      alert(window.i18n ? window.i18n.t('checkout.error') : 'Something went wrong. Please try again.');
      btn.textContent = originalText;
      btn.style.pointerEvents = '';
    }
  });
});

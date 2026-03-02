// ===== Config =====
const API_URL = 'https://a5692388-7de2-4b0a-a5ac-eb6998583c8b-00-2cugbbxqp58qp.pike.replit.dev:3000';

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
    btn.textContent = 'Redirecting…';
    btn.style.pointerEvents = 'none';

    try {
      const res = await fetch(`${API_URL}/create-checkout-session/playbook`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await res.json();

      if (data.url) {
        window.location.href = data.url;
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (err) {
      console.error('Checkout error:', err);
      alert('Something went wrong. Please try again.');
      btn.textContent = 'Get the Playbook — $29';
      btn.style.pointerEvents = '';
    }
  });
});

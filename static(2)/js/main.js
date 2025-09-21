// Theme toggle
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('themeToggle');
  const year = document.getElementById('year');
  const mobileBtn = document.getElementById('mobileMenuBtn');
  const mobileMenu = document.getElementById('mobileMenu');

  if (year) year.textContent = new Date().getFullYear().toString();

  if (toggle) {
    toggle.addEventListener('click', () => {
      const isDark = document.documentElement.classList.toggle('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
  }

  if (mobileBtn && mobileMenu) {
    mobileBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
  }

  // Simple lightbox
  document.querySelectorAll('[data-lightbox]')?.forEach((img) => {
    img.addEventListener('click', () => openLightbox(img.getAttribute('src')));
  });
});

function openLightbox(src) {
  const overlay = document.createElement('div');
  overlay.className = 'fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50';
  const img = document.createElement('img');
  img.src = src || '';
  img.className = 'max-h-[85vh] max-w-[90vw] rounded-xl shadow-2xl';
  overlay.appendChild(img);
  overlay.addEventListener('click', () => overlay.remove());
  document.body.appendChild(overlay);
}

// Minimal carousel utility (auto + buttons)
window.initCarousel = function(containerId, intervalMs = 5000) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const slides = container.querySelectorAll('[data-slide]');
  const dots = container.querySelectorAll('[data-dot]');
  let index = 0;

  function show(i) {
    slides.forEach((s, si) => s.classList.toggle('hidden', si !== i));
    dots.forEach((d, di) => d.classList.toggle('bg-primary-600', di === i));
  }
  function next() { index = (index + 1) % slides.length; show(index); }
  function prev() { index = (index - 1 + slides.length) % slides.length; show(index); }

  container.querySelector('[data-next]')?.addEventListener('click', next);
  container.querySelector('[data-prev]')?.addEventListener('click', prev);
  dots.forEach((d, di) => d.addEventListener('click', () => { index = di; show(index); }));
  show(0);
  if (intervalMs > 0) setInterval(next, intervalMs);
};



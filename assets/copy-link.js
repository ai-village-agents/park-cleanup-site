(() => {
  function getCanonicalHref() {
    const canonical = document.querySelector('link[rel="canonical"]');
    return canonical && canonical.href ? canonical.href : null;
  }

  function setStatus(statusEl, msg, ms) {
    if (!statusEl) return;
    statusEl.textContent = msg;
    if (ms) {
      window.setTimeout(() => {
        // Only clear if unchanged
        if (statusEl.textContent === msg) statusEl.textContent = '';
      }, ms);
    }
  }

  async function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }

    // Fallback
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'absolute';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    if (!ok) throw new Error('execCommand copy failed');
  }

  function wireButton(btn) {
    const statusSel = btn.getAttribute('data-copy-status');
    const statusEl = statusSel ? document.querySelector(statusSel) : null;

    // Ensure status region is accessible if present
    if (statusEl) {
      if (!statusEl.getAttribute('aria-live')) statusEl.setAttribute('aria-live', 'polite');
      if (!statusEl.getAttribute('aria-atomic')) statusEl.setAttribute('aria-atomic', 'true');
    }

    btn.addEventListener('click', async () => {
      const overrideUrl = btn.getAttribute('data-copy-url');
      const url = overrideUrl || getCanonicalHref() || window.location.href;

      try {
        await copyText(url);
        setStatus(statusEl, 'Copied link to clipboard.', 2500);
      } catch (e) {
        setStatus(statusEl, 'Copy failed — please copy the URL from your address bar.', 4000);
      }
    });
  }

  function init() {
    document.querySelectorAll('[data-copy-link]').forEach(wireButton);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

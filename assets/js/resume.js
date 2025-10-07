/* enhanced-resume.js
   Improved version of your resume UI helpers:
   - safer element access
   - aria + keyboard support
   - debounce/raf for scroll handlers
   - respects system color-scheme by default
   - fixed icon/theme logic
   - robust html2pdf generation (waits for .save() completion)
   - optional black-and-white PDF mode for small devices
*/

(() => {
  'use strict';

  /* Utility helpers */
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const safeAddEvent = (el, ev, fn) => { if (el) el.addEventListener(ev, fn); };

  /* ==================== SHOW / HIDE MENU ==================== */
  const showMenu = (toggleId, navId) => {
    const toggle = document.getElementById(toggleId);
    const nav = document.getElementById(navId);

    if (!toggle || !nav) return;

    // ARIA initial state
    toggle.setAttribute('aria-controls', navId);
    toggle.setAttribute('aria-expanded', 'false');

    const openMenu = () => {
      nav.classList.add('show-menu');
      toggle.setAttribute('aria-expanded', 'true');
      // trap focus if needed (simple approach)
      toggle.classList.add('is-open');
    };
    const closeMenu = () => {
      nav.classList.remove('show-menu');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.classList.remove('is-open');
    };
    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      nav.classList.toggle('show-menu');
      const expanded = nav.classList.contains('show-menu');
      toggle.setAttribute('aria-expanded', expanded.toString());
      if (expanded) toggle.classList.add('is-open'); else toggle.classList.remove('is-open');
    });

    // Close menu if click outside
    document.addEventListener('click', (e) => {
      if (!nav.contains(e.target) && !toggle.contains(e.target) && nav.classList.contains('show-menu')) {
        closeMenu();
      }
    });

    // Close on ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && nav.classList.contains('show-menu')) closeMenu();
    });
  };
  showMenu('nav-toggle', 'nav-menu');

  /* ==================== REMOVE MENU ON MOBILE NAV LINK CLICK ==================== */
  const navLinks = $$('.nav__link');
  function linkAction() {
    const navMenu = document.getElementById('nav-menu');
    if (navMenu && navMenu.classList.contains('show-menu')) {
      navMenu.classList.remove('show-menu');
      const toggle = $('#nav-toggle');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    }
  }
  navLinks.forEach(n => safeAddEvent(n, 'click', linkAction));

  /* ==================== SCROLL SECTIONS ACTIVE LINK (debounced via rAF) ==================== */
  const sections = $$('section[id]');
  let ticking = false;

  function updateActiveLinks() {
    const scrollY = window.pageYOffset;
    sections.forEach(current => {
      const sectionHeight = current.offsetHeight;
      const sectionTop = current.offsetTop - 50;
      const sectionId = current.getAttribute('id');
      const selector = `.nav__menu a[href*="${sectionId}"]`;
      const link = document.querySelector(selector);

      if (!link) return; // safe-guard if link missing

      if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
        link.classList.add('active-link');
        link.setAttribute('aria-current', 'true');
      } else {
        link.classList.remove('active-link');
        link.removeAttribute('aria-current');
      }
    });
    ticking = false;
  }

  function scrollActive() {
    if (!ticking) {
      window.requestAnimationFrame(updateActiveLinks);
      ticking = true;
    }
  }
  window.addEventListener('scroll', scrollActive, { passive: true });

  /* ==================== SHOW SCROLL TOP ==================== */
  function scrollTop() {
    const scrollTopEl = document.getElementById('scroll-top');
    if (!scrollTopEl) return;
    if (window.scrollY >= 200) {
      scrollTopEl.classList.add('show-scroll');
      scrollTopEl.setAttribute('aria-hidden', 'false');
    } else {
      scrollTopEl.classList.remove('show-scroll');
      scrollTopEl.setAttribute('aria-hidden', 'true');
    }
  }
  window.addEventListener('scroll', scrollTop, { passive: true });

  /* ==================== DARK / LIGHT THEME ==================== */
  const themeButton = document.getElementById('theme-button');
  const darkTheme = 'dark-theme';
  const iconTheme = 'bx-sun'; // CSS class used for the 'sun' icon on the button

  // safe getters (return 'dark' or 'light', and icon name)
  const getCurrentTheme = () => document.body.classList.contains(darkTheme) ? 'dark' : 'light';
  const getCurrentIcon = () => (themeButton && themeButton.classList.contains(iconTheme)) ? 'bx-sun' : 'bx-moon';

  // Load saved preferences
  const savedTheme = localStorage.getItem('selected-theme');
  const savedIcon = localStorage.getItem('selected-icon');

  // Prefer system preference if no saved setting
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (savedTheme) {
    document.body.classList[savedTheme === 'dark' ? 'add' : 'remove'](darkTheme);
    if (themeButton) themeButton.classList[savedIcon === 'bx-sun' ? 'add' : 'remove'](iconTheme);
  } else {
    // Respect system setting by default
    if (prefersDark) {
      document.body.classList.add(darkTheme);
      if (themeButton) themeButton.classList.add(iconTheme);
    } else {
      document.body.classList.remove(darkTheme);
      if (themeButton) themeButton.classList.remove(iconTheme);
    }
  }

  if (themeButton) {
    themeButton.setAttribute('role', 'button');
    themeButton.setAttribute('aria-pressed', getCurrentTheme() === 'dark' ? 'true' : 'false');
    themeButton.addEventListener('click', () => {
      document.body.classList.toggle(darkTheme);
      themeButton.classList.toggle(iconTheme);
      const currentTheme = getCurrentTheme();
      localStorage.setItem('selected-theme', currentTheme);
      localStorage.setItem('selected-icon', getCurrentIcon());
      themeButton.setAttribute('aria-pressed', currentTheme === 'dark' ? 'true' : 'false');
    });
  }

  /* ==================== SCALE FOR PRINT / PDF ==================== */
  function scaleCv() {
    document.body.classList.add('scale-cv');
  }
  function removeScale() {
    document.body.classList.remove('scale-cv');
  }

  /* Optional: apply a black-and-white stylesheet class for phone-sized devices
     This can be toggled before PDF generation to ensure legible B/W printouts */
  function applyBlackAndWhite(enable = true) {
    const cls = 'bw-cv';
    if (enable) document.body.classList.add(cls); else document.body.classList.remove(cls);
  }

  /* ==================== PDF GENERATION (html2pdf) ==================== */
  // Elements - safely fetch
  const areaCv = document.getElementById('area-cv');
  // NOTE: some versions of your HTML may have a typo 'resume-botton' - we try both
  const resumeButton = document.getElementById('resume-button') || document.getElementById('resume-botton');

  // html2pdf options (tweak as required)
  const defaultOpt = {
    margin: 0,
    filename: 'Resume.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 4, useCORS: true },
    jsPDF: { format: 'a4', orientation: 'portrait' }
  };

  // generate PDF and return promise that resolves when done (or rejects)
  function generatePdf(options = defaultOpt, bwForSmall = true, bwBreakpointPx = 420) {
    if (!areaCv) return Promise.reject(new Error('PDF area element not found'));

    // If requested: use black & white for small devices
    const shouldUseBW = bwForSmall && window.innerWidth <= bwBreakpointPx;
    if (shouldUseBW) applyBlackAndWhite(true);

    // apply scale class before capture
    scaleCv();

    // Use html2pdf API: html2pdf().from(element).set(opt).save()
    // Wrap in Promise so we can cleanup after completion.
    try {
      const worker = html2pdf().set(options).from(areaCv);
      // html2pdf's save returns a promise-like. We attach then/catch.
      return new Promise((resolve, reject) => {
        // add a timeout fallback (in case html2pdf doesn't call back)
        let finished = false;
        const fallback = setTimeout(() => {
          if (!finished) {
            finished = true;
            // best-effort cleanup
            removeScale();
            if (shouldUseBW) applyBlackAndWhite(false);
            resolve({ ok: true, timeout: true });
          }
        }, 20000); // 20s fallback

        worker.save().then(() => {
          if (finished) return;
          finished = true;
          clearTimeout(fallback);
          removeScale();
          if (shouldUseBW) applyBlackAndWhite(false);
          resolve({ ok: true, timeout: false });
        }).catch((err) => {
          if (finished) return;
          finished = true;
          clearTimeout(fallback);
          removeScale();
          if (shouldUseBW) applyBlackAndWhite(false);
          reject(err);
        });
      });
    } catch (err) {
      // cleanup and rethrow
      removeScale();
      if (shouldUseBW) applyBlackAndWhite(false);
      return Promise.reject(err);
    }
  }

  /* Attach click handler for resume download if button exists */
  if (resumeButton) {
    resumeButton.setAttribute('aria-label', 'Download resume as PDF');
    resumeButton.addEventListener('click', async (e) => {
      e.preventDefault();
      // Optionally disable button so user can't click repeatedly
      resumeButton.disabled = true;
      resumeButton.classList.add('is-busy');

      // Choose filename dynamically if you want (example uses data-name attr)
      const name = areaCv && areaCv.getAttribute('data-filename') ? areaCv.getAttribute('data-filename') : 'Resume';
      const options = { ...defaultOpt, filename: `${name}.pdf` };

      try {
        const result = await generatePdf(options, true, 420);
        // Optionally show a little toast or console log
        console.log('PDF generation result', result);
      } catch (err) {
        console.error('PDF generation failed', err);
        // fallback: remove scale if something went wrong
        removeScale();
        applyBlackAndWhite(false);
      } finally {
        // Re-enable button after a short delay so user sees the result
        setTimeout(() => {
          resumeButton.disabled = false;
          resumeButton.classList.remove('is-busy');
        }, 1200);
      }
    });
  } else {
    console.warn('Resume button not found - PDF feature disabled.');
  }

  /* ==================== Accessibility niceties: keyboard shortcuts ==================== */
  // Press 't' to toggle theme, 'p' to print/download resume (if button exists)
  document.addEventListener('keydown', (e) => {
    // Ignore if user is typing in input/textarea
    const tag = (document.activeElement && document.activeElement.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || document.activeElement.isContentEditable) return;

    if (e.key === 't' || e.key === 'T') {
      if (themeButton) themeButton.click();
    } else if ((e.key === 'p' || e.key === 'P') && resumeButton) {
      resumeButton.click();
    }
  });

  /* ==================== End of module ==================== */
})();

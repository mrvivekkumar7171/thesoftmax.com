/**
 * TheSoftMax & PrivacyFirst Shared Theme & Navigation Controller
 * Synchronizes user theme (dark / light) across:
 * - thesoftmax.com
 * - privacyfirst.thesoftmax.com
 * - missile.thesoftmax.com (and all future subdomains)
 * using cross-subdomain cookie scoped to .thesoftmax.com + localStorage fallback.
 */

(function () {
  'use strict';

  var COOKIE_NAME = 'thesoftmax_theme';

  function getDomainScope() {
    var host = window.location.hostname;
    if (host === 'thesoftmax.com' || host.endsWith('.thesoftmax.com')) {
      return '; domain=.thesoftmax.com';
    }
    return '';
  }

  function getStoredTheme() {
    // 1. Check shared cookie
    var match = document.cookie.match(new RegExp('(?:^|;\\s*)' + COOKIE_NAME + '=([^;]+)'));
    if (match) {
      var val = decodeURIComponent(match[1]);
      if (val === 'dark' || val === 'light') return val;
    }
    // 2. Check localStorage
    try {
      var local = localStorage.getItem(COOKIE_NAME) || localStorage.getItem('theme');
      if (local === 'dark' || local === 'light') return local;
    } catch (e) {}

    // 3. Fallback to system preference or default dark
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return 'light';
    }
    return 'dark'; // Default to dark (true-black aesthetic)
  }

  function setStoredTheme(theme) {
    // Write localStorage
    try {
      localStorage.setItem(COOKIE_NAME, theme);
      localStorage.setItem('theme', theme);
    } catch (e) {}

    // Write cross-subdomain cookie valid for 1 year
    var cookieStr = COOKIE_NAME + '=' + encodeURIComponent(theme) + getDomainScope() + '; path=/; max-age=31536000; SameSite=Lax';
    document.cookie = cookieStr;
  }

  function updateIcons(isDark) {
    var lightIcons = document.querySelectorAll('.theme-icon-light');
    var darkIcons = document.querySelectorAll('.theme-icon-dark');

    lightIcons.forEach(function (icon) {
      if (isDark) {
        icon.classList.remove('hidden');
      } else {
        icon.classList.add('hidden');
      }
    });

    darkIcons.forEach(function (icon) {
      if (isDark) {
        icon.classList.add('hidden');
      } else {
        icon.classList.remove('hidden');
      }
    });
  }

  function applyTheme(theme) {
    var isDark = theme === 'dark';
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    updateIcons(isDark);
  }

  function toggleTheme() {
    var current = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    var next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    setStoredTheme(next);
  }

  // Initialize on DOM ready
  document.addEventListener('DOMContentLoaded', function () {
    var currentTheme = getStoredTheme();
    applyTheme(currentTheme);

    // Setup Theme Toggle Buttons
    var toggleBtns = document.querySelectorAll('#theme-toggle, .theme-toggle-btn');
    toggleBtns.forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        toggleTheme();
      });
    });

    // Mobile Hamburger
    var hamburger = document.getElementById('hamburger');
    var navMobile = document.getElementById('navMobile');
    if (hamburger && navMobile) {
      hamburger.addEventListener('click', function () {
        var isOpen = navMobile.classList.toggle('open');
        hamburger.classList.toggle('open', isOpen);
        hamburger.setAttribute('aria-expanded', isOpen);
      });
    }

    // Auto-update copyright year
    var yearEl = document.getElementById('year');
    if (yearEl) {
      yearEl.textContent = new Date().getFullYear();
    }
  });

  // Listen for storage events (sync across multiple open tabs)
  window.addEventListener('storage', function (e) {
    if (e.key === COOKIE_NAME || e.key === 'theme') {
      if (e.newValue === 'dark' || e.newValue === 'light') {
        applyTheme(e.newValue);
      }
    }
  });
})();

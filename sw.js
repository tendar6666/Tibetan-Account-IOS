/**
 * ༄༅། །བོད་ཀྱི་རྩིས་དེབ། • Tibetan Account Book
 * Service Worker: Cache-First Offline Engine & Tibetan Font Caching
 * Version: tibetan-account-v8
 */

const CACHE_NAME = 'tibetan-account-v8';
const FONT_CACHE_NAME = 'tibetan-account-fonts-v1';

// Core static application shell assets
const CORE_ASSETS = [
  '/',
  '/index.html',
  '/app.js',
  '/styles.css',
  '/manifest.json'
];

// Scope-relative assets for subdirectory deployments (/ios/, /android/)
const RELATIVE_ASSETS = [
  './',
  './index.html',
  './app.js',
  './styles.css',
  './manifest.json'
];

const GOOGLE_FONT_CSS =
  'https://fonts.googleapis.com/css2?family=Noto+Sans+Tibetan:wght@400;600;700;800&display=swap';

// 1. Install Event: Cache static assets & preload Google Fonts CSS
self.addEventListener('install', event => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then(async cache => {
        // Cache core assets safely
        const allAssets = Array.from(new Set([...CORE_ASSETS, ...RELATIVE_ASSETS]));
        for (const asset of allAssets) {
          try {
            await cache.add(asset);
          } catch (err) {
            // Skip assets that do not resolve under current scope (e.g., subpaths)
          }
        }

        // Pre-cache Google Fonts Tibetan CSS if online during install
        try {
          const fontCache = await caches.open(FONT_CACHE_NAME);
          const fontRes = await fetch(GOOGLE_FONT_CSS);
          if (fontRes && (fontRes.ok || fontRes.type === 'opaque')) {
            await fontCache.put(GOOGLE_FONT_CSS, fontRes);
          }
        } catch (e) {
          // Offline during install: will cache on first online font load
        }
      })
      .then(() => self.skipWaiting())
  );
});

// 2. Activate Event: Delete obsolete caches & claim active clients
self.addEventListener('activate', event => {
  event.waitUntil(
    caches
      .keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (
              cacheName.startsWith('tibetan-account-') &&
              cacheName !== CACHE_NAME &&
              cacheName !== FONT_CACHE_NAME
            ) {
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => self.clients.claim())
  );
});

// 3. Fetch Event: Cache-First Strategy for App Shell & Fonts
self.addEventListener('fetch', event => {
  const request = event.request;

  // Only intercept HTTP/HTTPS GET requests
  if (request.method !== 'GET') {
    return;
  }

  const url = new URL(request.url);

  // Strategy A: Google Fonts CSS and WOFF2 glyph binaries
  if (url.origin === 'https://fonts.googleapis.com' || url.origin === 'https://fonts.gstatic.com') {
    event.respondWith(
      caches.open(FONT_CACHE_NAME).then(async cache => {
        const cached = await cache.match(request);
        if (cached) {
          return cached;
        }
        try {
          const networkRes = await fetch(request);
          if (networkRes && (networkRes.status === 200 || networkRes.type === 'opaque')) {
            cache.put(request, networkRes.clone());
          }
          return networkRes;
        } catch (err) {
          return cached || Response.error();
        }
      })
    );
    return;
  }

  // Strategy B: App Shell & Local Static Assets (Cache-First)
  if (url.origin === self.location.origin) {
    event.respondWith(
      caches.match(request).then(async cachedResponse => {
        if (cachedResponse) {
          return cachedResponse;
        }
        try {
          const networkResponse = await fetch(request);
          if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
          }
          return networkResponse;
        } catch (err) {
          // Offline fallback for page navigation
          if (request.mode === 'navigate') {
            return (
              (await caches.match('./index.html')) ||
              (await caches.match('/index.html')) ||
              (await caches.match('/'))
            );
          }
          throw err;
        }
      })
    );
    return;
  }
});

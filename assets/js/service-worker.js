const CACHE_NAME = 'softmax-cache-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/your-music-files.mp3', // optional: add actual files or load dynamically
  '/assets/favicon192.png', // 192-192 png
  '/assets/favicon512.png' // 512-512 png
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
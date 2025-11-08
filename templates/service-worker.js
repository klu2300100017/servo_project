self.addEventListener('install', e => {
  e.waitUntil(
    caches.open('ev-app').then(cache => {
      return cache.addAll(['/', '/manifest.json']);
    })
  );
});
self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(resp => resp || fetch(e.request))
  );
});

/* 선원 유급휴가 계산기 — 오프라인용 서비스 워커 (판: f047a11efd)
   - 계산기 페이지: 인터넷이 되면 새로 받고(4초 안에 안 오면 저장본), 안 되면 저장본
   - 아이콘·manifest: 저장본 먼저
   - 다른 사이트(GitHub 자료 파일, 글꼴)는 건드리지 않음 */
var CACHE = 'leave-calc-f047a11efd';
var FILES = ['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILES); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
function withTimeout(p, ms) {
  return new Promise(function (resolve, reject) {
    var t = setTimeout(function () { reject(new Error('timeout')); }, ms);
    p.then(function (v) { clearTimeout(t); resolve(v); }, function (err) { clearTimeout(t); reject(err); });
  });
}
self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;            /* 바깥 사이트는 그대로 */
  var isPage = req.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('/index.html');
  if (isPage) {
    e.respondWith(
      withTimeout(fetch(req), 4000).then(function (res) {
        if (res && res.ok) { var copy = res.clone(); caches.open(CACHE).then(function (c) { c.put('index.html', copy); }); }
        return res;
      }).catch(function () {
        return caches.match('index.html').then(function (hit) { return hit || caches.match('./'); });
      })
    );
    return;
  }
  e.respondWith(
    caches.match(req).then(function (hit) {
      return hit || fetch(req).then(function (res) {
        if (res && res.ok) { var copy = res.clone(); caches.open(CACHE).then(function (c) { c.put(req, copy); }); }
        return res;
      });
    })
  );
});

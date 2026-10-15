/* 선원 유급휴가 계산기 — 오프라인용 서비스 워커 (판: d63f1ecd64)
   - 계산기·아이콘: 저장본을 바로 줌 (인터넷을 기다리지 않음). 새 판은 sw.js가 바뀌면 설치되고, 페이지가 "새 판 준비됨" 띠를 보여 줌
   - 글꼴(fonts.googleapis.com·fonts.gstatic.com): 저장본 있으면 저장본, 없으면 5초만 기다려 받고 저장
   - GitHub 자료 파일(raw.githubusercontent.com) 등 나머지는 건드리지 않음 */
var CACHE = 'leave-calc-d63f1ecd64';
var FONTS = 'leave-calc-fonts-v1';
var FILES = ['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILES); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE && k !== FONTS; }).map(function (k) { return caches.delete(k); }));
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
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.open(FONTS).then(function (c) {
      return c.match(req).then(function (hit) {
        if (hit) return hit;
        return withTimeout(fetch(req), 5000).then(function (res) {
          if (res && (res.ok || res.type === 'opaque')) c.put(req, res.clone());
          return res;
        }).catch(function () { return Response.error(); });
      });
    }));
    return;
  }
  if (url.origin !== self.location.origin) return;
  var isPage = req.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('/index.html') || url.pathname.endsWith('/404.html');
  e.respondWith(
    caches.match(isPage ? 'index.html' : req).then(function (hit) {
      if (hit) return hit;
      return fetch(req).then(function (res) {
        if (res && res.ok) { var copy = res.clone(); caches.open(CACHE).then(function (c) { c.put(isPage ? 'index.html' : req, copy); }); }
        return res;
      }).catch(function () { return isPage ? caches.match('./') : Response.error(); });
    })
  );
});

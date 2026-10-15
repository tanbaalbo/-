# 웹앱(홈 화면에 추가해서 쓰는 판) 만들기 → 저장소의 docs/ 폴더 (GitHub Pages가 여기를 보여 줌)
#   사용법: python3 build_pwa.py <계산기 HTML 경로>
#   만드는 것: docs/index.html, docs/manifest.webmanifest, docs/sw.js, docs/icons/*.png, docs/404.html
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_icon import draw

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(os.path.dirname(HERE), 'docs')
src_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'seafarer-leave.html')
src = open(src_path, encoding='utf8').read()
ver = hashlib.sha1(src.encode('utf8')).hexdigest()[:10]   # 계산기 내용이 바뀌면 캐시 이름도 바뀜

os.makedirs(os.path.join(DOCS, 'icons'), exist_ok=True)
draw(192).save(os.path.join(DOCS, 'icons', 'icon-192.png'))
draw(512).save(os.path.join(DOCS, 'icons', 'icon-512.png'))
draw(180, square=True).save(os.path.join(DOCS, 'icons', 'apple-touch-icon.png'))

HEAD = '''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#F1F4F7">
<meta name="application-name" content="유급휴가 계산기">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="유급휴가">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<style>[hidden]{display:none!important}body{margin:0}
@supports (padding: env(safe-area-inset-top)) { body { padding-top: calc(28px + env(safe-area-inset-top)); padding-bottom: calc(48px + env(safe-area-inset-bottom)); } }
</style>
</head><body>'''
TAIL = '''
<div id="swUpdate" hidden style="position:fixed;left:16px;right:16px;bottom:16px;z-index:9;display:flex;gap:10px;align-items:center;justify-content:space-between;padding:12px 14px;border-radius:10px;background:#13233A;color:#fff;font-size:14px;box-shadow:0 6px 20px rgba(0,0,0,.25)">
  <span>새 판이 준비됐어요.</span>
  <button type="button" id="swReload" style="font:inherit;font-weight:600;padding:6px 12px;border-radius:8px;border:0;background:#fff;color:#13233A">새로고침</button>
</div>
<script>
/* 오프라인용 서비스 워커: 저장해 둔 계산기를 먼저 띄우고(즉시), 인터넷이 되면 뒤에서 새 판을 받아 둠 */
if ('serviceWorker' in navigator) {
  var hadController = !!navigator.serviceWorker.controller;   /* 이미 설치된 상태에서 열었는지 */
  navigator.serviceWorker.addEventListener('controllerchange', function () {
    if (!hadController) return;                                 /* 처음 설치는 알림 없음 */
    var bar = document.getElementById('swUpdate'); if (bar) bar.hidden = false;
  });
  var reload = document.getElementById('swReload');
  if (reload) reload.addEventListener('click', function () { location.reload(); });
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('sw.js').then(function (reg) {
      try { reg.update(); } catch (e) {}
      window.addEventListener('online', function () { try { reg.update(); } catch (e) {} });
    }).catch(function () {});
  });
}
</script>
</body></html>'''
open(os.path.join(DOCS, 'index.html'), 'w', encoding='utf8').write(HEAD + src + TAIL)
open(os.path.join(DOCS, '404.html'), 'w', encoding='utf8').write(HEAD + src + TAIL)   # 주소를 잘못 쳐도 계산기

manifest = {
    "name": "선원 유급휴가 계산기",
    "short_name": "유급휴가",
    "description": "승선일·하선일로 유급휴가 일수, 휴가 기간, 조기승선 수당 계산",
    "id": "./",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "lang": "ko",
    "background_color": "#F1F4F7",
    "theme_color": "#F1F4F7",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
    ]
}
open(os.path.join(DOCS, 'manifest.webmanifest'), 'w', encoding='utf8').write(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

SW = '''/* 선원 유급휴가 계산기 — 오프라인용 서비스 워커 (판: __VER__)
   - 계산기·아이콘: 저장본을 바로 줌 (인터넷을 기다리지 않음). 새 판은 sw.js가 바뀌면 설치되고, 페이지가 "새 판 준비됨" 띠를 보여 줌
   - 글꼴(fonts.googleapis.com·fonts.gstatic.com): 저장본 있으면 저장본, 없으면 5초만 기다려 받고 저장
   - GitHub 자료 파일(raw.githubusercontent.com) 등 나머지는 건드리지 않음 */
var CACHE = 'leave-calc-__VER__';
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
'''.replace('__VER__', ver)
open(os.path.join(DOCS, 'sw.js'), 'w', encoding='utf8').write(SW)
open(os.path.join(DOCS, '.nojekyll'), 'w').write('')   # GitHub Pages가 파일을 그대로 내보내게
print('docs/ 만듦 — 판', ver, '| index.html', len(HEAD + src + TAIL), '바이트')

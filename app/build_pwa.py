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
<script>
/* 오프라인용 서비스 워커 등록 (한 번 열어 두면 인터넷 없이도 열림) */
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('sw.js').catch(function () {});
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
   - 계산기 페이지: 인터넷이 되면 새로 받고(4초 안에 안 오면 저장본), 안 되면 저장본
   - 아이콘·manifest: 저장본 먼저
   - 다른 사이트(GitHub 자료 파일, 글꼴)는 건드리지 않음 */
var CACHE = 'leave-calc-__VER__';
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
'''.replace('__VER__', ver)
open(os.path.join(DOCS, 'sw.js'), 'w', encoding='utf8').write(SW)
open(os.path.join(DOCS, '.nojekyll'), 'w').write('')   # GitHub Pages가 파일을 그대로 내보내게
print('docs/ 만듦 — 판', ver, '| index.html', len(HEAD + src + TAIL), '바이트')

#!/bin/bash
# APK 조립 스크립트 (Ubuntu apt의 aapt·dalvik-exchange·zipalign·apksigner + JDK 사용)
#   사용법: ./build.sh <계산기 HTML 경로> <keystore 경로> <keystore 비밀번호>
#   결과:  build/vacation_calculator.apk (자바 도구는 한글 파일 이름을 못 쓰므로 영문 이름으로 만든 뒤 복사)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
HTML="${1:?계산기 HTML 경로}"; KS="${2:?keystore 경로}"; KSPASS="${3:?keystore 비밀번호}"
SDK=/usr/lib/android-sdk/platforms/android-23/android.jar
DX=$(command -v dalvik-exchange || command -v dx)
cd "$HERE"
rm -rf build && mkdir -p build/classes build/gen

# 1) 계산기 HTML을 완전한 문서로 감싸서 assets/index.html로, 자료 파일은 저장소의 data.json 그대로
python3 - "$HTML" <<'EOF'
import sys, os
src = open(sys.argv[1], encoding='utf8').read()
here = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
open(os.path.join('assets', 'index.html'), 'w', encoding='utf8').write(
  '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
  '<meta name="viewport" content="width=device-width,initial-scale=1">'
  '<style>[hidden]{display:none!important}body{margin:0}</style></head><body>' + src + '</body></html>')
EOF
cp ../data.json assets/data.json
python3 - <<'EOF'
import json; json.load(open('assets/data.json', encoding='utf8')); print('assets/data.json OK')
EOF

# 2) 리소스 → R.java, 자바 컴파일, dex
aapt package -f -m -J build/gen -M AndroidManifest.xml -S res -I "$SDK"
javac --release 8 -Xlint:-options -cp "$SDK" -d build/classes build/gen/com/tanbaalbo/vacationcalculator/R.java src/com/tanbaalbo/vacationcalculator/MainActivity.java
"$DX" --dex --min-sdk-version=21 --output=build/classes.dex build/classes

# 3) APK 묶기 → 정렬 → 서명
aapt package -f -M AndroidManifest.xml -S res -A assets -I "$SDK" -F build/app.unsigned.apk
(cd build && aapt add app.unsigned.apk classes.dex >/dev/null)
zipalign -f 4 build/app.unsigned.apk build/app.aligned.apk
apksigner sign --ks "$KS" --ks-pass "pass:$KSPASS" --out build/vacation_calculator.apk build/app.aligned.apk
apksigner verify --verbose build/vacation_calculator.apk
rm -f build/app.unsigned.apk build/app.aligned.apk
ls -la build/vacation_calculator.apk

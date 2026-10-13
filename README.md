# 선원 유급휴가 계산기 — 자료 파일

계산기 앱이 인터넷이 될 때 이 저장소의 `data.json`을 받아서 임금표와 공휴일을 최신으로 바꿉니다.
인터넷이 안 되면 앱에 들어 있는 자료를 그대로 씁니다.

앱이 받아 가는 주소:
`https://raw.githubusercontent.com/tanbaalbo/vacation_calculator/main/data.json`

## data.json 안의 내용

| 항목 | 내용 |
|---|---|
| `dataVersion` | 자료를 고친 날짜 (고칠 때마다 바꿔 주기) |
| `wage` | 임금표 — 직책별 통상임금(`base`, 원), 호봉 1개당 단가(`step`, 원), 최대 호봉(`maxStep`) |
| `holidays` | 대한민국 관공서 공휴일 — 확정 발표된 해(`years`)와 날짜별 이름(`days`). 일요일은 계산기가 알아서 처리 |

## 매년 할 일

- **공휴일**: 다음 해 공휴일(한국천문연구원 월력요항, 보통 6월쯤)이 발표되면 `years`에 그 해를 넣고 `days`에 날짜를 추가
- **임금표**: 새 임금표가 나오면 `wage`의 금액·제목·시행일을 바꿈
- 고친 뒤 `dataVersion`을 고친 날짜로 바꿈

GitHub 화면에서 `data.json` → 연필 버튼(Edit)으로 직접 고치고 **Commit changes**를 눌러도 됩니다.
쉼표·따옴표가 하나라도 틀리면 앱이 자료를 못 읽고 기존 자료를 계속 쓰니, 고친 뒤 꼭 계산기에서 확인하세요.

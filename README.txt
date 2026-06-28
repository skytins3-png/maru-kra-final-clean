MARU KRA GOOGLE SHEET URL INPUT FIX

수정:
- 깨진 구글시트 주소를 기본 링크로 고정하지 않음
- Streamlit Secrets의 SHEET_ID를 우선 사용
- PC 화면에서 실제 구글시트 주소/SHEET_ID를 붙여넣어 화면 연결값으로 사용할 수 있음
- 사이드바 구글시트 버튼도 현재 연결값 기준으로 표시
- 저장 확인센터 유지

주의:
- 앱 화면 입력값은 화면 연결 표시용입니다.
- 실제 구글시트 저장은 Streamlit Secrets의 SHEET_ID + SERVICE_ACCOUNT_JSON + 시트 공유 권한이 필요합니다.

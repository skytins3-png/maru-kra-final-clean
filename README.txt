MARU KRA DUPLICATE KEY SEQ FIX

수정:
- StreamlitDuplicateElementKey: seq_step_count_* 중복 오류 해결
- 같은 26개 API 순차수집센터가 한 화면에서 두 번 호출되어도 위젯 key가 겹치지 않게 caller line number를 key에 추가
- 기존 멈춤방지 자동 진행 유지
- HTTP 404/500은 실패 저장 후 다음 API 진행 유지

적용:
ZIP 안의 app.py, requirements.txt를 GitHub 루트에 덮어쓰기.

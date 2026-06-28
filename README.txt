MARU KRA SEQ STUCK AUTO CONTINUE FIX

수정:
- 26개 API 순차수집이 12/26 같은 중간 지점에서 멈춘 것처럼 보이는 문제 보강
- 자동 순차 진행 ON이면 화면 렌더링마다 1개 API 진행 후 st.rerun
- Streamlit 자동 rerun이 막히는 환경 대비 브라우저 meta refresh 추가
- HTTP 404/500도 실패로 저장하고 다음 API로 계속 진행
- 수동 버튼: 다음 API 1개 즉시 진행 / 선택 개수 진행 / 처음부터 다시

적용:
ZIP 안의 app.py, requirements.txt를 GitHub 루트에 덮어쓰기.

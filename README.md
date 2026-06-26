# MARU V13.4.4.3.2 통합 자동화 AI

오늘 대화 기준 통합본입니다. 기존 기능을 제거하지 않고 V12.3까지의 기능에 HTML 카드 코드노출 수정, 경마시간 추천없음 표시 보정 패치를 추가했습니다.

## 포함
- 경마앱/토토앱 ZIP 등록
- AI 코드생성기
- 로그 붙여넣기/로그파일 분석
- 사진 첨부/명령 입력
- 구글시트 저장
- 승인 패치
- GitHub 자동반영
- 모바일 사용
- HTML agent-card 코드노출 수정 패치
- 경마시간인데 추천 없음 표시 보정 패치
- 자동구매/자동결제 차단

## 올릴 파일
app.py
requirements.txt
README.md
ai_memory.json

Streamlit Cloud Main file path: app.py


## V13.4.4.3.2 추가

- 기본설정 자동불러오기
- 프로젝트 이름/배포주소/API KEY/API URL/GitHub owner/repo/branch 저장
- 등록 탭 자동 입력
- GitHub 자동반영 탭 자동 입력
- 모바일 재입력 불편 개선
- GitHub 토큰은 파일 저장하지 않고 Streamlit Secrets `GITHUB_TOKEN` 자동 사용 지원

Streamlit Secrets 예시:

```toml
GITHUB_TOKEN = "github_pat_..."
```


## V13.4.4.3 추가

- 프로젝트 이름 칸을 직접입력만 하지 않고 선택식으로 개선
- 경마앱 / 토토앱 / AI 코드 생성기 / 직접입력 선택 가능
- 선택하면 프로젝트 이름, 배포 앱 주소, GitHub owner/repo/branch 자동 변경
- 등록 탭과 GitHub 자동반영 탭에서 같은 선택 구조 적용
- 모바일에서 프로젝트 이름/API/GitHub repo 반복 입력 불편 개선


## V13.4.4 추가

- GitHub 토큰 매번 입력 불편 개선
- API KEY 매번 입력 불편 개선
- Streamlit Secrets에서 자동 불러오기
- 경마앱/토토앱 선택 시 기본 API URL 자동 채움

### Streamlit Secrets 권장값

```toml
GITHUB_TOKEN = "github_pat_..."
KRA_API_KEY = "공공데이터_API_KEY"
PUBLIC_DATA_API_KEY = "공공데이터_API_KEY"
SPORTMONKS_TOKEN = "스포츠_API_TOKEN"
TOTO_API_KEY = "토토_API_KEY"
```

토큰/API 키는 공개 GitHub 파일에 저장하지 마세요.


## V13.4 추가

- GitHub 자동 업로드 404 Not Found 보정
- 기존 파일이 없으면 실패가 아니라 새 파일 생성(create)으로 처리
- 기존 파일이 있으면 sha 기반 수정(update)
- app.py / README.md / requirements.txt / ai_memory.json 첫 업로드 실패 문제 수정


## V13.5 긴급 수정

- `NameError: default_api_key_for` 오류 수정
- 누락된 자동 API 키/URL 함수 상단 고정
- 프로젝트 선택 자동변경 유지
- GitHub 토큰/API 키 Secrets 자동불러오기 유지
- GitHub 404 Not Found → 새 파일 생성 처리 유지


## V13.6 긴급 안정화

- `default_api_key_for` NameError 재발 방지
- 기존 함수명을 쓰는 코드와 새 함수명을 모두 호환 처리
- 화면 코드에서 안전 함수 직접 사용
- GitHub 404 새 파일 생성 처리 유지
- 프로젝트 선택/토큰/API 자동불러오기 유지


## V13.7 화면 정리

- Streamlit 도움말/dir(streamlit) 디버그 출력 제거
- 앱 상단에 길게 나오던 Streamlit 설명문 제거
- V13.6 NameError 호환 수정 유지
- GitHub 토큰/API 키 Secrets 자동감지 유지
- 프로젝트 선택/자동반영 유지


## V13.8 완전 화면 정리

- Streamlit 도움말 원문 출력 제거
- `st.help(st)`, `st.write(st)`, `dir(streamlit)` 계열 출력 제거
- 혹시 남은 도움말/디버그 덤프도 화면에 표시되지 않도록 안전 가드 추가
- V13.6 NameError 호환 수정 유지
- V13.7 화면정리 유지
- GitHub 토큰/API 키 Secrets 자동감지 유지


## V13.9 긴급 화면 고정

- `st.help(st)` / `st.help(streamlit)` 출력 차단
- Streamlit 도움말/명령어 목록 출력 하드 차단
- V13.8 화면정리 유지
- V13.6 NameError 호환 수정 유지
- GitHub 토큰/API 키 Secrets 자동감지 유지


## V14 프로젝트 보관소 자동반영

- 경마앱 / 토토앱 / AI 코드 생성기 최신파일을 보관소에 저장
- 이후 등록 반복 없이 프로젝트 클릭으로 최신파일 자동 불러오기
- 보관소에서 불러온 파일 기준으로 패치/검사/GitHub 자동반영
- 프로젝트 이름/앱 주소/GitHub repo/branch 자동 적용
- 토큰/API 키 Secrets 자동감지 유지
- 기존 V13.9 화면정리, V13.6 NameError 방지, GitHub 404 새 파일 생성 처리 유지


## V14.1 연속자동화 루프

- 보관소 최신파일 불러오기
- 자동 테스트
- 로그분석
- 테스트 통과 시 GitHub 자동반영
- 실패 시 재패치 대기 기록
- 패치 → 반영 → 테스트 → 로그분석 → 재패치 흐름을 한 화면에서 연결
- 연속자동화 기록 저장

주의: 실제 코드 수정 패치는 승인 기반으로 유지합니다. 자동구매/자동결제는 계속 차단합니다.


## V14.2 개선 요구사항 승인 후 진행

- 개선 요구사항을 바로 패치하지 않고 승인대기함에 저장
- 승인 / 보류 / 거절 선택 가능
- 승인된 항목만 패치 대기열로 이동
- 패치 대기열 기준으로 패치 → 반영 → 테스트 → 로그분석 루프 진행
- 자동화는 유지하되 승인 없는 임의 진행은 차단
- 기존 V14 보관소, V14.1 연속자동화 루프 유지


## V14.3 승인 후 무승인 패치 루프

- 개선 요구사항은 최초 승인 필요
- 승인된 뒤에는 패치마다 추가 승인 없이 연속 진행
- 흐름: 테스트 → 로그분석 → 안전 자동패치 → 재테스트 → GitHub 자동반영
- 안전 자동패치 범위:
  - requirements.txt 누락 생성
  - README.md 누락 생성
  - ai_memory.json 누락 생성
- 위험한 코드 수정은 자동으로 밀어붙이지 않고 로그 기록 후 재패치 필요로 멈춤
- 기존 보관소, 연속자동화, GitHub 자동반영, Secrets 자동감지 유지


## V14.4 KST 보관소 긴급 수정

- `NameError: KST` 오류 수정
- 보관소 최신파일 불러오기에서 한국시간 기록 가능
- KST가 누락되어도 fallback으로 한국시간 사용
- V14 보관소 자동반영 유지
- V14.1 연속자동화 유지
- V14.2 개선승인 유지
- V14.3 승인 후 무승인 패치루프 유지


## V14.5 KST 최종 안정화

- `NameError: KST` 재발 방지
- `datetime.now(KST)` 직접 호출 제거
- `maru_now_kst_text()` 안전 함수로 통일
- KST 변수가 없어도 한국시간 fallback 사용
- 보관소 저장/불러오기 시간 기록 안정화
- V14 보관소, V14.1 연속자동화, V14.2 개선승인, V14.3 무승인 패치루프 유지


## V14.6 저장 함수 긴급 수정

- `NameError: save_memory` 오류 수정
- 보관소/연속루프에서 메모리 저장 함수가 없어도 안전하게 저장
- `MEM` 경로가 있으면 그 파일에 저장
- `MEM` 경로가 없으면 `ai_memory.json`에 저장
- V14.5 KST 안전시간 수정 유지
- V14 보관소, V14.1 연속자동화, V14.2 개선승인, V14.3 무승인 패치루프 유지


## V15 풀자동화 통합판

기존 기능을 제거하지 않고 풀자동화 엔진을 추가했습니다.

유지 기능:
- 프로젝트 보관소
- 개선 요구사항 승인
- 승인 후 무승인 패치 루프
- 자동 테스트
- 로그분석
- GitHub 자동반영
- 구글시트
- 사진/명령 분석
- 패치/검사/버전 기록
- 토큰/API Secrets 자동감지
- 자동구매/자동결제 차단

추가 기능:
- 🤖 풀자동화 탭
- 누락파일 자동생성
- NameError 자동수정
- KST/save_memory/default_api 계열 누락 자동삽입
- 안전한 문법오류 자동수정
- 재테스트 반복
- 통과 시 GitHub 자동반영


## V15.1 Streamlit 경고 제거

- `use_container_width=True` → `width="stretch"` 변경
- `use_container_width=False` → `width="content"` 변경
- 변경 개수: True 41개, False 0개
- V15 풀자동화 엔진 유지
- 프로젝트 보관소 유지
- 개선승인 / 무승인 패치루프 / 로그분석 / GitHub 자동반영 유지
- 자동구매/자동결제 차단 유지

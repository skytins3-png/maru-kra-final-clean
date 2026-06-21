# -*- coding: utf-8 -*-
"""
MARU KRA FINAL ALL-IN-ONE APP - STABLE BET INTEGRATED
- 덮어쓰기용 단일 app.py
- 기존 핵심 기능 유지형: 기존 19개 + 추가 7개 = 26개 KRA/기상 API URL 자동 내장/고정, API별 ON/OFF, 전체 실시간 ON/OFF
- HTTP 500/SSL 인증서 오류/무응답/0건이어도 앱 중단 없이 최근 캐시/샘플로 계속 분석
- 실시간 분석, 허브 저장, API 진단, 시간표/빅데이터, 10초 수동구매 모드 포함
- 추가 통합: 마권 승식 설명 + 18,000원 삼쌍승 18장 + 예상 배당/환급/손익 계산
- 자동구매/자동결제 없음: 더비온 등록완료 모드 + 공식 구매표 이동 + 사용자가 직접 입력/확정
- 모바일 상단 3추천창 + 삼쌍승 18장(3묶음×6순서) / 18,000원 수동구매 대시보드
"""

from __future__ import annotations

import os
import re
import json
import time
import random
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from typing import Dict, List, Tuple, Any, Optional

import pandas as pd
import requests

# HOTFIX_LOADING_FAST: 첫 화면 10분 로딩 방지 · 초기 API 자동호출 OFF · 버튼 클릭 시만 실시간 수집
import urllib3
import streamlit as st
import streamlit.components.v1 as components

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------------------------------------------------------
# Streamlit basic
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MARU KRA 실전 대시보드 ALL-IN-ONE",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="collapsed",
)

KST = ZoneInfo("Asia/Seoul")
DATA_DIR = Path("maru_kra_data")
DATA_DIR.mkdir(exist_ok=True)
LOCAL_HUB_FILE = DATA_DIR / "maru_kra_hub_records.csv"
API_STATUS_FILE = DATA_DIR / "maru_kra_api_status.csv"
LOCAL_SETTINGS_FILE = DATA_DIR / "maru_kra_local_settings.json"
SCHEDULE_HUB_FILE = DATA_DIR / "maru_kra_schedule_hub.csv"
BIGDATA_FILE = DATA_DIR / "maru_kra_bigdata_result_log.csv"
AUTO_RUN_STATE_FILE = DATA_DIR / "maru_kra_auto_run_state.json"
LIVE_CACHE_FILE = DATA_DIR / "maru_kra_last_live_cache.json"
SMART_API_CACHE_DIR = DATA_DIR / "smart_api_cache"
SMART_API_CACHE_DIR.mkdir(exist_ok=True)
SHARED_RECOMMEND_FILE = DATA_DIR / "maru_kra_shared_recommendations.csv"
MOBILE_RECOMMEND_FILE = DATA_DIR / "mobile_recommend.json"  # 모바일은 이 작은 JSON 1개만 우선 읽어서 버벅임 방지
AUTO_ANALYSIS_LOG_FILE = DATA_DIR / "maru_kra_auto_analysis_log.csv"
STRATEGY_BIGDATA_FILE = DATA_DIR / "maru_kra_strategy_bigdata.csv"
BACKGROUND_RUN_STATE_FILE = DATA_DIR / "maru_kra_background_runner_state.json"

# -----------------------------------------------------------------------------
# 26 default API URLs
# -----------------------------------------------------------------------------
FORCE_DEFAULT_URLS: Dict[str, str] = {
    "race_url": "https://apis.data.go.kr/B551015/API186_1/SeoulRace_1",
    "entry_url": "https://apis.data.go.kr/B551015/API23_1/entryRaceHorse_1",
    "horse_url": "https://apis.data.go.kr/B551015/API310/raceHorseInfo",
    "body_url": "https://apis.data.go.kr/B551015/API25_1/raceHorseBody",
    "gear_url": "https://apis.data.go.kr/B551015/API24_1/raceHorseGear",
    "rating_url": "https://apis.data.go.kr/B551015/API77/raceHorseRating",
    "odds_url": "https://apis.data.go.kr/B551015/API28_1/Dividend_rate",
    "today_odds_url": "https://apis.data.go.kr/B551015/API301/Dividend_rate_total",
    "result_detail_url": "https://apis.data.go.kr/B551015/API299_1/raceResultDetail_1",
    "race_record_url": "https://apis.data.go.kr/B551015/API214_1/raceRecord_1",
    "start_exam_url": "https://apis.data.go.kr/B551015/API76_1/startExamResult_1",
    "judge_url": "https://apis.data.go.kr/B551015/API72_1/raceJudge_1",
    "jockey_change_url": "https://apis.data.go.kr/B551015/API71_1/jockeyChange_1",
    "weather_alert_url": "https://apis.data.go.kr/1360000/WthrWrnInfoService/getPwnStatus",
    "corner_pace_url": "https://apis.data.go.kr/B551015/API303/corner_rank",
    "popularity_url": "https://apis.data.go.kr/B551015/API302/popularity",
    "first_odds_url": "https://apis.data.go.kr/B551015/API27_1/winPredictionRateInfo_1",
    "second_odds_url": "https://apis.data.go.kr/B551015/API29_1/doublePredictionRateInfo_1",
    "third_odds_url": "https://apis.data.go.kr/B551015/API30_1/triplePredictionRateInfo_1",
    # 추가 7개 API: KRA 공식 흐름 기반 사전분석/직전보정/결과검증 보강
    "race_overview_url": "https://apis.data.go.kr/B551015/API3_1/raceInfo_1",
    "race_cancel_url": "https://apis.data.go.kr/B551015/API9_1/raceHorseCancelInfo_1",
    "entry_registered_url": "https://apis.data.go.kr/B551015/API23_1/entryRaceHorse_1",
    "dividend_integrated_url": "https://apis.data.go.kr/B551015/API160_1/integratedInfo_1",
    "jockey_result_url": "https://apis.data.go.kr/B551015/API11_1/jockeyResult_1",
    "race_detail_result_url": "https://apis.data.go.kr/B551015/API214_1/RaceDetailResult_1",
    "horse_shoe_url": "https://apis.data.go.kr/B551015/API191_1/HorseShoe_1",
}


# =============================================================================
# [HOTFIX] 결과대기 API 분리
# =============================================================================
# 아래 API들은 경주 전/발매 전/결과 확정 전에는 404/500/0건이 나와도
# 앱 실패가 아니라 "결과대기"로 봅니다.
PENDING_RESULT_API_KEYS = {
    "body_url", "gear_url", "odds_url", "result_detail_url", "race_record_url",
    "start_exam_url", "judge_url", "jockey_change_url", "popularity_url",
    "first_odds_url", "second_odds_url",
}

PENDING_RESULT_API_LABEL = {
    "body_url": "계량/체중 공개 전 가능",
    "gear_url": "장구/폐출혈 공개 전 가능",
    "odds_url": "발매 전/배당 미공개 가능",
    "result_detail_url": "결과 확정 전 가능",
    "race_record_url": "기록 확정 전 가능",
    "start_exam_url": "출발심사 정보 미공개 가능",
    "judge_url": "심판정보 미공개 가능",
    "jockey_change_url": "기수변경 없으면 0건 가능",
    "popularity_url": "인기투표 집계 전 가능",
    "first_odds_url": "1착 적중승식 결과 전 가능",
    "second_odds_url": "2착 적중승식 결과 전 가능",
}

def classify_api_status(key: str, msg: str, rows: int) -> Tuple[str, str]:
    raw = str(msg or "")
    try:
        rows_int = int(rows)
    except Exception:
        rows_int = 0

    if rows_int > 0:
        return "OK", "분석사용"

    wait_like = ["HTTP 404", "HTTP 500", "0건", "ConnectionPool", "timeout", "Read timed out", "HTTPSConnectionPool"]
    if key in PENDING_RESULT_API_KEYS and any(x in raw for x in wait_like):
        return "PENDING", PENDING_RESULT_API_LABEL.get(key, "결과대기")

    if any(x in raw for x in ["HTTP 404", "HTTP 500", "ConnectionPool", "timeout", "Read timed out", "HTTPSConnectionPool"]):
        return "ERROR", "재시도필요"

    if key in PENDING_RESULT_API_KEYS:
        return "PENDING", PENDING_RESULT_API_LABEL.get(key, "결과대기")
    return "ERROR", "확인필요"

def api_status_summary_panel(status_df: pd.DataFrame) -> None:
    if status_df is None or status_df.empty or "분류" not in status_df.columns:
        return
    ok_n = int((status_df["분류"] == "OK").sum())
    pending_n = int((status_df["분류"] == "PENDING").sum())
    err_n = int((status_df["분류"] == "ERROR").sum())
    cache_n = int((status_df["분류"] == "CACHE").sum())
    blocked_n = int((status_df["분류"] == "BLOCKED").sum())
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("✅ 분석 사용 API", f"{ok_n}개")
    c2.metric("📦 캐시 사용/API OFF", f"{cache_n}개")
    c3.metric("🕒 결과대기 API", f"{pending_n}개")
    c4.metric("⚠️ 재시도 API", f"{err_n}개")
    c5.metric("🚫 비운영일 차단", f"{blocked_n}개")
    with st.expander("✅ 분석에 사용한 성공 API"):
        st.dataframe(status_df[status_df["분류"] == "OK"], width="stretch", hide_index=True)
    with st.expander("📦 성공 저장 후 자동 OFF · 캐시 사용 API"):
        st.dataframe(status_df[status_df["분류"] == "CACHE"], width="stretch", hide_index=True)
    with st.expander("🕒 아직 결과/집계 전 API"):
        st.dataframe(status_df[status_df["분류"] == "PENDING"], width="stretch", hide_index=True)
    with st.expander("🚫 금/토/일 외 API 차단"):
        st.dataframe(status_df[status_df["분류"] == "BLOCKED"], width="stretch", hide_index=True)
    with st.expander("⚠️ 진짜 재시도 필요 API"):
        st.dataframe(status_df[status_df["분류"] == "ERROR"], width="stretch", hide_index=True)


# =============================================================================
# [HOTFIX] 성공 API 저장소 / 경주시간표 20분 전 모바일 추천 / 결과대기 재분석 엔진
# =============================================================================
SUCCESS_API_CACHE_DIR = DATA_DIR / "success_api_cache"
SUCCESS_API_CACHE_DIR.mkdir(exist_ok=True)

DAILY_PLAN_FILE = DATA_DIR / "daily_mobile_plan.json"
REANALYSIS_LOG_FILE = DATA_DIR / "reanalysis_change_log.csv"
ALERT_STATE_FILE = DATA_DIR / "mobile_alert_state.json"

def _safe_file_key(*parts: Any) -> str:
    text = "_".join(str(p) for p in parts if str(p) != "")
    return re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", text)[:180]


# =============================================================================
# [HOTFIX] 성공 API 자동 OFF 정책
# =============================================================================
# 한 번 성공해서 저장하면 같은 날짜/경마장/경주에서는 다시 부를 필요가 적은 API.
# API 과호출 방지, 속도 개선, 모바일/Cloud 안정성을 위해 성공 캐시가 있으면 자동 OFF합니다.
STATIC_SUCCESS_OFF_KEYS = {
    "race_url",              # 경주정보
    "entry_url",             # 출전등록말/출전표
    "horse_url",             # 경주마정보
    "rating_url",            # 레이팅
    "race_record_url",       # 과거/기록성 자료
    "start_exam_url",        # 출발심사
    "judge_url",             # 경주심판
    "race_overview_url",     # 경주개요
    "entry_registered_url",  # 출전등록말
    "jockey_result_url",     # 기수성적
    "horse_shoe_url",        # 경주마장제
}

# 계속 변할 수 있어 자동 OFF하지 않는 API.
DYNAMIC_RETRY_KEYS = {
    "body_url", "gear_url", "odds_url", "today_odds_url", "result_detail_url",
    "jockey_change_url", "weather_alert_url", "corner_pace_url", "popularity_url",
    "first_odds_url", "second_odds_url", "third_odds_url", "race_cancel_url",
    "dividend_integrated_url", "race_detail_result_url",
}

AUTO_OFF_STATE_FILE = DATA_DIR / "api_auto_off_state.json"

def load_auto_off_state() -> Dict[str, Any]:
    return load_json_file(AUTO_OFF_STATE_FILE, {}) if "load_json_file" in globals() else {}

def save_auto_off_state(state: Dict[str, Any]) -> None:
    try:
        save_json_file(AUTO_OFF_STATE_FILE, state)
    except Exception:
        try:
            AUTO_OFF_STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

def _auto_off_id(rc_date: str, meet: str, race_no: int, key: str) -> str:
    return _safe_file_key(rc_date, meet, race_no, key)

def mark_api_auto_off_after_success(key: str, rc_date: str, meet: str, race_no: int, rows: int) -> bool:
    """정적 API가 성공 저장되면 같은 경주에서는 자동 OFF로 표시합니다."""
    if key not in STATIC_SUCCESS_OFF_KEYS:
        return False
    try:
        if int(rows) <= 0:
            return False
    except Exception:
        return False
    state = load_auto_off_state()
    api_id = _auto_off_id(rc_date, meet, race_no, key)
    state[api_id] = {
        "key": key,
        "날짜": rc_date,
        "경마장": meet,
        "경주번호": int(race_no),
        "OFF사유": "성공 저장 완료",
        "저장시각": now_str(),
        "행수": int(rows),
    }
    save_auto_off_state(state)
    return True

def is_api_auto_off_by_success(key: str, rc_date: str, meet: str, race_no: int) -> bool:
    """성공 저장된 정적 API는 다음 호출부터 건너뜁니다."""
    if key not in STATIC_SUCCESS_OFF_KEYS:
        return False
    state = load_auto_off_state()
    return _auto_off_id(rc_date, meet, race_no, key) in state

def api_auto_off_summary() -> pd.DataFrame:
    state = load_auto_off_state()
    rows = list(state.values()) if isinstance(state, dict) else []
    return pd.DataFrame(rows)

def reset_api_auto_off_state() -> None:
    save_auto_off_state({})



# =============================================================================
# [HOTFIX] 금/토/일 운영 제한 + 실패/결과대기 API 25분 전 재접속 정책
# =============================================================================
RACE_ALLOWED_WEEKDAYS = {4, 5, 6}  # 월=0, 금=4, 토=5, 일=6
PENDING_RETRY_BEFORE_MIN = 25
PENDING_RETRY_AFTER_MIN = 3
RACE_DAY_BLOCK_STATE_FILE = DATA_DIR / "race_day_block_state.json"
RACE_ONLY_ALERT_FILE = DATA_DIR / "race_only_realert.json"

def is_race_day_today(dt: Optional[datetime] = None) -> bool:
    """경마 운영일: 금/토/일만 API 접속 허용."""
    dt = dt or now_kst()
    return dt.weekday() in RACE_ALLOWED_WEEKDAYS

def race_day_name(dt: Optional[datetime] = None) -> str:
    dt = dt or now_kst()
    return ["월", "화", "수", "목", "금", "토", "일"][dt.weekday()]

def block_non_race_day_reason() -> str:
    return f"오늘은 {race_day_name()}요일입니다. 경마 운영일 금/토/일 외에는 API 접속을 차단합니다."

def should_retry_pending_for_race(race_dt: Optional[datetime], now_dt: Optional[datetime] = None) -> bool:
    """실패/결과대기 API는 경주시간 25분 전부터 출발 후 3분까지만 재접속."""
    if not race_dt:
        return False
    now_dt = now_dt or now_kst()
    remain_min = int((race_dt - now_dt).total_seconds() // 60)
    return (-PENDING_RETRY_AFTER_MIN <= remain_min <= PENDING_RETRY_BEFORE_MIN)

def get_race_datetime_from_inputs(race_time_text: Any = "") -> Optional[datetime]:
    try:
        if race_time_text:
            return _parse_hhmm_to_today(race_time_text)
    except Exception:
        pass
    try:
        if "parse_today_race_datetime" in globals():
            return parse_today_race_datetime(str(race_time_text))
    except Exception:
        pass
    return None

def pending_keys_due_for_retry(schedule_df: pd.DataFrame, meet: str, race_no: int) -> Tuple[bool, str, Optional[datetime]]:
    """현재 경주의 시간표를 보고 25분 전이면 결과대기 API 재접속 허용."""
    race_dt = None
    try:
        if schedule_df is not None and not schedule_df.empty:
            d = schedule_df.copy()
            if "경마장" in d.columns:
                d = d[d["경마장"].astype(str).apply(normalize_meet) == normalize_meet(meet)]
            if "경주번호" in d.columns:
                d = d[pd.to_numeric(d["경주번호"], errors="coerce") == int(race_no)]
            if not d.empty:
                row = d.iloc[0]
                if str(row.get("경주시각", "")).strip():
                    try:
                        race_dt = datetime.fromisoformat(str(row.get("경주시각")))
                    except Exception:
                        race_dt = None
                if race_dt is None:
                    race_dt = _parse_hhmm_to_today(row.get("경주시간", ""))
    except Exception:
        race_dt = None

    ok = should_retry_pending_for_race(race_dt)
    if not race_dt:
        return False, "경주시간표 없음 · 결과대기 API 재접속 보류", None
    remain = int((race_dt - now_kst()).total_seconds() // 60)
    if ok:
        return True, f"경주 {remain}분 전 · 결과대기 API 재접속 허용", race_dt
    return False, f"경주 {remain}분 전 · 25분 전까지 결과대기 API 재접속 보류", race_dt

def build_race_only_alert(old_row: Dict[str, Any], new_row: Dict[str, Any]) -> bool:
    """추천 변경 알림은 해당 시간 경주 1건만 재발송."""
    try:
        same_race_keys = ["날짜", "경마장", "경주번호"]
        same_race = all(str(old_row.get(k, "")) == str(new_row.get(k, "")) for k in same_race_keys if old_row.get(k, "") or new_row.get(k, ""))
        old_combo = str(old_row.get("삼쌍승18조합", ""))
        new_combo = str(new_row.get("삼쌍승18조합", ""))
        changed = bool(new_combo and old_combo and new_combo != old_combo)
        if changed and same_race:
            payload = {
                "저장시각": now_str(),
                "알림": "Y",
                "알림종류": "해당경주추천변경",
                "날짜": new_row.get("날짜", ""),
                "경마장": new_row.get("경마장", ""),
                "경주번호": new_row.get("경주번호", ""),
                "경주시간": new_row.get("경주시간", ""),
                "이전조합": old_combo,
                "신규조합": new_combo,
                "메시지": "🔔 결과대기 API 반영으로 해당 경주 추천이 변경되었습니다.",
            }
            RACE_ONLY_ALERT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
    except Exception:
        pass
    return False


def save_success_api_cache(key: str, df: pd.DataFrame, rc_date: str, meet: str, race_no: int, msg: str = "") -> bool:
    """성공 API는 한 번 받은 뒤 캐시에 저장해서 다음 접속 때 재사용합니다."""
    try:
        if df is None or df.empty:
            return False
        file_key = _safe_file_key(rc_date, meet, race_no, key)
        payload = {
            "저장시각": now_str(),
            "key": key,
            "날짜": rc_date,
            "경마장": meet,
            "경주번호": int(race_no),
            "상태": msg,
            "행수": int(len(df)),
            "rows": df.head(1000).astype(str).to_dict("records"),
        }
        (SUCCESS_API_CACHE_DIR / f"{file_key}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False

def load_success_api_cache(key: str, rc_date: str, meet: str, race_no: int) -> pd.DataFrame:
    """API가 결과대기/오류일 때 성공 캐시가 있으면 불러와 분석에 사용합니다."""
    try:
        file_key = _safe_file_key(rc_date, meet, race_no, key)
        path = SUCCESS_API_CACHE_DIR / f"{file_key}.json"
        if not path.exists():
            return pd.DataFrame()
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("rows", [])
        if rows:
            return pd.DataFrame(rows)
    except Exception:
        pass
    return pd.DataFrame()

def save_all_success_caches(data: Dict[str, pd.DataFrame], status_df: pd.DataFrame, rc_date: str, meet: str, race_no: int) -> int:
    saved = 0
    try:
        if status_df is None or status_df.empty:
            return 0
        for _, r in status_df.iterrows():
            key = str(r.get("key", ""))
            cls = str(r.get("분류", ""))
            msg = str(r.get("상태", ""))
            if cls == "OK" and key in data and data[key] is not None and not data[key].empty:
                if save_success_api_cache(key, data[key], rc_date, meet, int(race_no), msg):
                    saved += 1
                    mark_api_auto_off_after_success(key, rc_date, meet, int(race_no), len(data[key]))
    except Exception:
        pass
    return saved

def hydrate_pending_from_success_cache(data: Dict[str, pd.DataFrame], status_df: pd.DataFrame, rc_date: str, meet: str, race_no: int) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame, int]:
    """결과대기/오류 API는 기존 성공 캐시가 있으면 분석용으로 보충합니다."""
    loaded = 0
    if status_df is None or status_df.empty:
        saved_cache_count = save_all_success_caches(data, status_df, rc_date, meet, race_no)
    data, status_df, loaded_cache_count = hydrate_pending_from_success_cache(data, status_df, rc_date, meet, race_no)
    try:
        status_df["성공캐시저장수"] = saved_cache_count
        status_df["성공캐시불러오기수"] = loaded_cache_count
    except Exception:
        pass
    return data, status_df, loaded
    status_df = status_df.copy()
    for idx, r in status_df.iterrows():
        key = str(r.get("key", ""))
        cls = str(r.get("분류", ""))
        if not key:
            continue
        if cls != "OK":
            cached = load_success_api_cache(key, rc_date, meet, int(race_no))
            if not cached.empty:
                data[key] = cached
                status_df.loc[idx, "분류"] = "CACHE"
                status_df.loc[idx, "해석"] = "성공 캐시 재사용"
                if "행수" in status_df.columns:
                    status_df.loc[idx, "행수"] = len(cached)
                if "건수" in status_df.columns:
                    status_df.loc[idx, "건수"] = len(cached)
                loaded += 1
    return data, status_df, loaded

def _parse_hhmm_to_today(value: Any) -> Optional[datetime]:
    try:
        s = str(value or "").strip()
        m = re.search(r"(\d{1,2})[:시](\d{1,2})", s)
        if m:
            hh, mm = int(m.group(1)), int(m.group(2))
        else:
            nums = re.findall(r"\d+", s)
            if not nums:
                return None
            raw = nums[0].zfill(4)
            hh, mm = int(raw[:2]), int(raw[2:])
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            return now_kst().replace(hour=hh, minute=mm, second=0, microsecond=0)
    except Exception:
        return None
    return None

def extract_schedule_from_data(data: Dict[str, pd.DataFrame], rc_date: str, fallback_meet: str = "서울") -> pd.DataFrame:
    """성공 API나 저장된 race_schedule.csv에서 하루 경주시간표를 구성합니다."""
    rows = []
    candidate_dfs = []
    for k in ["race_url", "race_overview_url"]:
        if k in data and data[k] is not None and not data[k].empty:
            candidate_dfs.append(data[k])
    # 기존 CSV도 재사용
    try:
        p = DATA_DIR / "race_schedule.csv"
        if p.exists():
            candidate_dfs.append(pd.read_csv(p, encoding="utf-8-sig"))
    except Exception:
        pass

    for df in candidate_dfs:
        if df is None or df.empty:
            continue
        no_col = find_col(df, ["rcNo", "raceNo", "경주번호", "rc_no"])
        meet_col = find_col(df, ["meet", "meetCd", "경마장"])
        time_col = find_col(df, ["rcTime", "raceTime", "경주시간", "출발시간", "time"])
        date_col = find_col(df, ["rcDate", "raceDate", "날짜", "date"])
        if not no_col:
            continue
        for _, r in df.iterrows():
            try:
                race_no = int(float(str(r.get(no_col))))
            except Exception:
                continue
            meet = normalize_meet(r.get(meet_col, fallback_meet)) if meet_col else fallback_meet
            t = r.get(time_col, "") if time_col else ""
            dt = _parse_hhmm_to_today(t)
            date_v = str(r.get(date_col, rc_date)).replace("-", "")[:8] if date_col else rc_date
            if date_v and date_v != str(rc_date).replace("-", "")[:8]:
                continue
            rows.append({"날짜": rc_date, "경마장": meet, "경주번호": race_no, "경주시간": str(t), "경주시각": dt.isoformat() if dt else ""})

    if not rows:
        # 시간표 API가 비어도 하루 계획 화면이 죽지 않도록 기본 경주 간격 제공
        default_times = ["11:00", "11:25", "11:50", "12:20", "12:50", "13:20", "13:50", "14:20", "14:50", "15:20", "15:50", "16:20", "16:50", "17:20"]
        for i, t in enumerate(default_times, 1):
            dt = _parse_hhmm_to_today(t)
            rows.append({"날짜": rc_date, "경마장": fallback_meet, "경주번호": i, "경주시간": t, "경주시각": dt.isoformat() if dt else ""})

    out = pd.DataFrame(rows).drop_duplicates(subset=["날짜", "경마장", "경주번호"]).sort_values(["경마장", "경주번호"])
    try:
        out.to_csv(DATA_DIR / "race_schedule.csv", index=False, encoding="utf-8-sig")
    except Exception:
        pass
    return out


# =============================================================================
# [HOTFIX] 18마권 구매표: 안정형 6 + 고배당형 6 + 변수대응형 6
# =============================================================================
def _unique_int_list(values: List[Any], fallback_max: int = 12) -> List[int]:
    out = []
    for v in values or []:
        try:
            n = int(float(str(v).strip()))
            if n > 0 and n not in out:
                out.append(n)
        except Exception:
            continue
    n = 1
    while len(out) < 7 and n <= fallback_max:
        if n not in out:
            out.append(n)
        n += 1
    return out

def _top_nums_by_column(score_df: pd.DataFrame, score_col: str, fallback_col: str = "종합점수") -> List[int]:
    try:
        if score_df is None or score_df.empty or "마번" not in score_df.columns:
            return _unique_int_list([])
        d = score_df.copy()
        use_col = score_col if score_col in d.columns else fallback_col if fallback_col in d.columns else None
        if use_col:
            d[use_col] = pd.to_numeric(d[use_col], errors="coerce").fillna(0)
            d = d.sort_values(use_col, ascending=False)
        return _unique_int_list(d["마번"].tolist())
    except Exception:
        return _unique_int_list([])

def _six_trifecta_orders(nums3: List[int], key: str = "stable") -> List[str]:
    from itertools import permutations  # SIX_TICKET_HARD_FIX
    """3마리 기준 삼쌍승 6개 순열."""
    nums = _unique_int_list(nums3)[:3]
    if len(nums) < 3:
        nums = _unique_int_list(nums + [1,2,3])[:3]
    orders = list(itertools.permutations(nums, 3))
    # 안정형은 축마 1착을 먼저, 고배당은 구멍마 1착 가능성을 앞쪽, 변수형은 변동 후보를 앞쪽
    if key == "stable":
        orders = sorted(orders, key=lambda p: (p[0] != nums[0], p[1] != nums[1], p))
    elif key == "high":
        orders = sorted(orders, key=lambda p: (p[0] != nums[2], p[0] != nums[1], p))
    elif key == "variable":
        orders = sorted(orders, key=lambda p: (p[0] != nums[1], p[2] != nums[2], p))
    return ["-".join(map(str, p)) for p in orders[:6]]

def build_18ticket_purchase_plan(score_df: pd.DataFrame, result: Dict[str, Any] = None, total_budget: int = 18000) -> Dict[str, Any]:
    """추천 결과를 18마권 구매표로 변환합니다.
    자동구매가 아니라 더비온에 수동 입력하기 위한 복사표만 생성합니다.
    """
    result = dict(result or {})
    unit = max(100, int(total_budget / 18)) if total_budget else 1000

    stable_nums = _top_nums_by_column(score_df, "안정점수")
    high_nums = _top_nums_by_column(score_df, "고배당점수")
    variable_nums = _top_nums_by_column(score_df, "변수점수")

    # 컬럼이 부족하면 종합순위 기반으로 자연스럽게 분산
    base = _top_nums_by_column(score_df, "종합점수")
    stable3 = _unique_int_list(stable_nums[:3] or base[:3])[:3]
    high3 = _unique_int_list((high_nums[:1] + base[:2] + high_nums[1:3]) or base[:4])[:3]
    variable3 = _unique_int_list((variable_nums[:2] + base[:3]) or base[:4])[:3]

    stable6 = _six_trifecta_orders(stable3, "stable")
    high6 = _six_trifecta_orders(high3, "high")
    variable6 = _six_trifecta_orders(variable3, "variable")
    all18 = stable6 + high6 + variable6

    plan = {
        "18마권": "Y",
        "마권수": 18,
        "단위금액": unit,
        "총추천금액": unit * 18,
        "안정형6": stable6,
        "고배당형6": high6,
        "변수대응형6": variable6,
        "삼쌍승18조합": "; ".join(all18),
        "안정형대표": stable6[0] if stable6 else "",
        "고배당형대표": high6[0] if high6 else "",
        "변수대응형대표": variable6[0] if variable6 else "",
        "구매표복사": (
            "[삼쌍승 18마권 수동입력표]\\n"
            f"단위금액: {unit:,}원 / 총 {unit*18:,}원\\n\\n"
            "① 안정형 6개\\n" + "\\n".join([f"삼쌍승 {x} / {unit:,}원" for x in stable6]) + "\\n\\n"
            "② 고배당형 6개\\n" + "\\n".join([f"삼쌍승 {x} / {unit:,}원" for x in high6]) + "\\n\\n"
            "③ 변수대응형 6개\\n" + "\\n".join([f"삼쌍승 {x} / {unit:,}원" for x in variable6])
        ),
    }
    return plan

def merge_18ticket_into_row(row: Dict[str, Any], score_df: pd.DataFrame, total_budget: int = 18000) -> Dict[str, Any]:
    row = dict(row or {})
    plan = build_18ticket_purchase_plan(score_df, row, total_budget)
    row.update(plan)
    return row


# =============================================================================
# [HOTFIX] 모바일 상단 경주시간/결과상태 헤더
# =============================================================================
def _mobile_time_left_text(latest: Dict[str, Any]) -> str:
    try:
        dt = None
        if str(latest.get("경주시각", "")).strip():
            try:
                dt = datetime.fromisoformat(str(latest.get("경주시각")))
            except Exception:
                dt = None
        if dt is None:
            dt = _parse_hhmm_to_today(latest.get("경주시간", ""))
        if dt is None:
            return "출발시간 확인중"
        minutes = int((dt - now_kst()).total_seconds() // 60)
        if minutes > 0:
            return f"출발 {minutes}분 전"
        if -3 <= minutes <= 0:
            return "출발 임박"
        return f"출발 {abs(minutes)}분 경과"
    except Exception:
        return "출발시간 확인중"

def _mobile_result_status(latest: Dict[str, Any]) -> str:
    """결과상태: 결과대기 / 추천완료 / 결과확정."""
    try:
        result_no = str(latest.get("결과마번", "") or "").strip()
        hit = str(latest.get("적중여부", "") or "").strip()
        payout = str(latest.get("환급금", latest.get("총환급", "")) or "").strip()
        if result_no and result_no not in ["결과대기", "대기", "-", "None", "nan"]:
            return "결과확정"
        if hit and hit not in ["", "대기", "결과대기", "-", "None", "nan"]:
            return "결과확정"
        if payout and payout not in ["0", "0.0", "", "-", "None", "nan"]:
            return "결과확정"
        if str(latest.get("실전검증", "")).upper() == "Y" or str(latest.get("18마권", "")).upper() == "Y":
            return "추천완료"
    except Exception:
        pass
    return "결과대기"

def render_mobile_race_header(latest: Dict[str, Any]) -> None:
    """모바일 상단에는 조합수 중복표시 대신 경주시간/남은시간/갱신/상태를 표시합니다."""
    try:
        meet = latest.get("경마장", "")
        race_no = latest.get("경주번호", "")
        race_time = latest.get("경주시간", latest.get("출발시간", ""))
        time_left = _mobile_time_left_text(latest)
        updated = str(latest.get("저장시각", latest.get("추천갱신", "")) or "")
        # 2026-.. HH:MM:SS 형식이면 HH:MM만 강조
        m = re.search(r"(\d{1,2}:\d{2})", updated)
        updated_short = m.group(1) if m else updated[-5:] if len(updated) >= 5 else updated
        status = _mobile_result_status(latest)
        result_no = str(latest.get("결과마번", "결과대기") or "결과대기")
        dividend = str(latest.get("배당률", "") or "")
        profit = str(latest.get("손익", latest.get("순손익", "")) or "")

        st.markdown(
            f"""
            <div style="
                border:1px solid rgba(120,160,220,.35);
                background:linear-gradient(135deg, rgba(20,35,65,.96), rgba(12,20,38,.98));
                border-radius:24px;
                padding:18px 18px 14px 18px;
                margin:8px 0 14px 0;
                box-shadow:0 10px 28px rgba(0,0,0,.22);
            ">
              <div style="font-size:28px;font-weight:900;color:#ffffff;line-height:1.25;">
                {meet} {race_no}R · {race_time}
              </div>
              <div style="font-size:22px;font-weight:800;color:#ffd978;margin-top:6px;">
                {time_left}
              </div>
              <div style="
                    display:grid;
                    grid-template-columns:1fr;
                    gap:8px;
                    margin-top:12px;
                    font-size:16px;
              ">
                <div style="background:rgba(255,255,255,.08);border-radius:16px;padding:12px;color:#dfeaff;">
                  대표 추천<br>
                  <b style="font-size:20px;color:#ffffff;">안정형 {latest.get("안정형대표", latest.get("공격삼쌍승", "-"))}</b><br>
                  <b style="font-size:20px;color:#ffffff;">고배당 {latest.get("고배당형대표", "-")}</b><br>
                  <b style="font-size:20px;color:#ffffff;">변수형 {latest.get("변수대응형대표", "-")}</b>
                </div>
              </div>
              <div style="
                    display:grid;
                    grid-template-columns:1fr 1fr;
                    gap:8px;
                    margin-top:10px;
                    font-size:16px;
              ">
                <div style="background:rgba(255,255,255,.07);border-radius:14px;padding:10px;color:#dfeaff;">
                  추천 갱신<br><b style="font-size:20px;color:#ffffff;">{updated_short or "대기"}</b>
                </div>
                <div style="background:rgba(255,255,255,.07);border-radius:14px;padding:10px;color:#dfeaff;">
                  상태<br><b style="font-size:20px;color:#ffffff;">{status}</b>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if status == "결과확정":
            st.success(f"경주결과: {result_no} · 배당: {dividend or '확인중'} · 손익: {profit or '계산대기'}")
        else:
            st.caption("경주결과: 결과대기 · 결과 API가 들어오면 적중/배당/손익으로 자동 갱신")
    except Exception as e:
        st.caption(f"모바일 경주 헤더 표시 대기: {e}")


def render_18ticket_cards(latest: Dict[str, Any]) -> None:
    """모바일/PC 공통 18마권 표시."""
    try:
        stable6 = latest.get("안정형6", [])
        high6 = latest.get("고배당형6", [])
        variable6 = latest.get("변수대응형6", [])
        if isinstance(stable6, str):
            stable6 = [x.strip() for x in re.split(r"[;,\\n]+", stable6) if x.strip()]
        if isinstance(high6, str):
            high6 = [x.strip() for x in re.split(r"[;,\\n]+", high6) if x.strip()]
        if isinstance(variable6, str):
            variable6 = [x.strip() for x in re.split(r"[;,\\n]+", variable6) if x.strip()]
        unit = int(float(str(latest.get("단위금액", 1000)).replace(",", ""))) if str(latest.get("단위금액", "")).replace(",", "").replace(".", "").isdigit() else 1000

        st.markdown("### 🎯 삼쌍승 18마권 구매표")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### ① 안정형 6개")
            for x in stable6[:6]:
                st.code(f"삼쌍승 {x} / {unit:,}원")
        with c2:
            st.markdown("#### ② 고배당형 6개")
            for x in high6[:6]:
                st.code(f"삼쌍승 {x} / {unit:,}원")
        with c3:
            st.markdown("#### ③ 변수대응형 6개")
            for x in variable6[:6]:
                st.code(f"삼쌍승 {x} / {unit:,}원")

        copy_text = latest.get("구매표복사", "")
        if copy_text:
            st.text_area("18마권 전체 복사", value=copy_text, height=260)
    except Exception as e:
        st.caption(f"18마권 표시 대기: {e}")


def build_3group_recommendation_from_score(score_df: pd.DataFrame) -> Dict[str, Any]:
    from itertools import permutations  # THREE_GROUP_HARD_FIX
    from itertools import permutations  # HARD_FIX
    """점수표에서 3조합 삼쌍승 18장을 구성합니다."""
    if score_df is None or score_df.empty or "마번" not in score_df.columns:
        nums = [1, 2, 3, 4, 5, 6, 7]
    else:
        nums = pd.to_numeric(score_df["마번"], errors="coerce").dropna().astype(int).tolist()
    while len(nums) < 7:
        nums.append(len(nums) + 1)
    g1 = nums[:3]
    g2 = [nums[0], nums[3], nums[4]]
    g3 = nums[-3:]
    tickets = []
    for g in [g1, g2, g3]:
        tickets += ["-".join(map(str, p)) for p in itertools.permutations(g, 3)]
    return {
        "공격삼쌍승": f"{g1[0]}→{g1[1]}→{g1[2]}",
        "방어삼복승": f"{g1[0]}-{g1[1]}-{g1[2]}",
        "삼쌍승3묶음": " | ".join(["-".join(map(str, g)) for g in [g1, g2, g3]]),
        "삼쌍승18조합": "; ".join(tickets[:18]),
    }

def save_daily_mobile_plan(schedule_df: pd.DataFrame, base_result: Dict[str, Any], score_df: pd.DataFrame) -> Dict[str, Any]:
    """하루 경주시간표 기준 3조합 추천을 미리 저장합니다."""
    combo = build_3group_recommendation_from_score(score_df)
    plan = []
    for _, r in schedule_df.iterrows():
        row = dict(base_result or {})
        row.update(combo)
        row = merge_18ticket_into_row(row, score_df, int(row.get("추천금액", 18000) or 18000))
        row.update({
            "저장시각": now_str(),
            "날짜": r.get("날짜", today_kst() if "today_kst" in globals() else now_kst().strftime("%Y%m%d")),
            "경마장": r.get("경마장", row.get("경마장", "")),
            "경주번호": r.get("경주번호", row.get("경주번호", "")),
            "경주시간": r.get("경주시간", ""),
            "경주시각": r.get("경주시각", ""),
            "데이터상태": row.get("데이터상태", "실시간"),
            "실전검증": row.get("실전검증", "Y"),
            "실전표시불가": row.get("실전표시불가", "N"),
            "모바일생성": "Y",
            "계획추천": "Y",
        })
        plan.append(row)
    payload = {"저장시각": now_str(), "총경주": len(plan), "추천목록": plan}
    DAILY_PLAN_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload

def select_mobile_recommendation_by_time() -> Dict[str, Any]:
    """현재 시간 기준 다음 경주 20분 전부터 모바일 추천을 노출합니다."""
    mobile_now = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else {}
    try:
        if DAILY_PLAN_FILE.exists():
            payload = json.loads(DAILY_PLAN_FILE.read_text(encoding="utf-8"))
            plan = payload.get("추천목록", [])
            now = now_kst()
            upcoming = []
            for row in plan:
                dt = None
                try:
                    if row.get("경주시각"):
                        dt = datetime.fromisoformat(str(row.get("경주시각")))
                except Exception:
                    dt = _parse_hhmm_to_today(row.get("경주시간", ""))
                if not dt:
                    continue
                minutes = int((dt - now).total_seconds() // 60)
                if -5 <= minutes <= 20:
                    row["알림"] = "Y"
                    row["알림문구"] = f"{row.get('경마장')} {row.get('경주번호')}R 출발 {minutes}분 전 추천"
                    return row
                if minutes > 20:
                    upcoming.append((minutes, row))
            if upcoming:
                upcoming.sort(key=lambda x: x[0])
                row = upcoming[0][1]
                row["알림"] = "N"
                row["알림문구"] = f"다음 경주 {upcoming[0][0]}분 전 대기"
                return row
    except Exception:
        pass
    return mobile_now

def detect_combo_change_and_alert(old_row: Dict[str, Any], new_row: Dict[str, Any]) -> bool:
    """결과대기 API가 새로 들어와 재분석 후 3조합이 바뀌면 알림 상태를 기록합니다."""
    try:
        old_combo = str(old_row.get("삼쌍승18조합", ""))
        new_combo = str(new_row.get("삼쌍승18조합", ""))
        changed = bool(old_combo and new_combo and old_combo != new_combo)
        state = {
            "저장시각": now_str(),
            "변경감지": "Y" if changed else "N",
            "이전조합": old_combo,
            "신규조합": new_combo,
            "알림": "🔔 결과대기 API 반영으로 추천 조합이 변경되었습니다." if changed else "",
        }
        ALERT_STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        if changed:
            pd.DataFrame([state]).to_csv(REANALYSIS_LOG_FILE, mode="a", header=not REANALYSIS_LOG_FILE.exists(), index=False, encoding="utf-8-sig")
        return changed
    except Exception:
        return False

def apply_mobile_plan_update(new_result: Dict[str, Any], score_df: pd.DataFrame, schedule_df: pd.DataFrame) -> bool:
    """새 추천이 생기면 하루 계획과 현재 모바일 추천을 함께 갱신합니다."""
    old_mobile = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else {}
    payload = save_daily_mobile_plan(schedule_df, new_result, score_df)
    selected = select_mobile_recommendation_by_time()
    if selected:
        save_mobile_recommend_json(selected)
        detect_combo_change_and_alert(old_mobile, selected)
        build_race_only_alert(old_mobile, selected)
        return True
    return bool(payload)


def api_required_group_pass(status_df: pd.DataFrame, live_rows: int) -> bool:
    """필수 묶음 3개 이상 성공하면 허브 저장 가능."""
    try:
        if status_df is None or status_df.empty or "key" not in status_df.columns:
            return int(live_rows) > 0
        if "분류" in status_df.columns:
            ok_keys = set(status_df.loc[status_df["분류"].isin(["OK", "CACHE"]), "key"].astype(str).tolist())
        else:
            ok_keys = set(status_df.loc[pd.to_numeric(status_df.get("행수", 0), errors="coerce").fillna(0) > 0, "key"].astype(str).tolist())
        groups = [
            bool({"race_url", "race_overview_url"} & ok_keys),
            bool({"entry_url", "entry_registered_url"} & ok_keys),
            bool({"rating_url", "jockey_result_url", "horse_url"} & ok_keys),
            bool({"today_odds_url", "dividend_integrated_url", "third_odds_url"} & ok_keys),
        ]
        return sum(groups) >= 3 or int(live_rows) > 0
    except Exception:
        return False


API_LABELS: List[Tuple[str, str]] = [
    ("race_url", "① 경주정보"),
    ("entry_url", "② 출전등록말/출전표"),
    ("horse_url", "③ 경주마정보"),
    ("body_url", "④ 출전마 체중"),
    ("gear_url", "⑤ 장구/폐출혈"),
    ("rating_url", "⑥ 레이팅"),
    ("odds_url", "⑦ 배당/매출"),
    ("today_odds_url", "⑧ 시행당일 배당종합"),
    ("result_detail_url", "⑨ 경주결과상세"),
    ("race_record_url", "⑩ 경주기록"),
    ("start_exam_url", "⑪ 출발심사"),
    ("judge_url", "⑫ 경주심판"),
    ("jockey_change_url", "⑬ 기수변경"),
    ("weather_alert_url", "⑭ 기상특보"),
    ("corner_pace_url", "⑮ 코너/주로빠르기"),
    ("popularity_url", "⑯ 인기투표"),
    ("first_odds_url", "⑰ 1착마 적중승식"),
    ("second_odds_url", "⑱ 2착마 적중승식"),
    ("third_odds_url", "⑲ 3착마 적중승식"),
    ("race_overview_url", "⑳ 경주개요 API3_1"),
    ("race_cancel_url", "㉑ 출전취소 API9_1"),
    ("entry_registered_url", "㉒ 출전등록말 API23_1"),
    ("dividend_integrated_url", "㉓ 확정배당통합 API160_1"),
    ("jockey_result_url", "㉔ 기수성적 API11_1"),
    ("race_detail_result_url", "㉕ 경주성적상세 API214_1"),
    ("horse_shoe_url", "㉖ 경주마장제 API191_1"),
]
API_TOTAL_COUNT = len(API_LABELS)


API_URLS_LOCKED = True  # 기존 19개 + 추가 7개 = 총 26개 API URL은 프로그램 안에 자동 탑재되어 재입력하지 않습니다.
APP_VERSION = "FASTLOAD_HOTFIX_STRICT_CURRENT_RACE_26API_20260620"

CORE_DEFAULT_API_KEYS = [
    "race_url", "entry_url", "body_url", "rating_url", "today_odds_url",
    "jockey_change_url", "corner_pace_url", "popularity_url",
    "race_overview_url", "race_cancel_url", "entry_registered_url",
    "dividend_integrated_url", "jockey_result_url", "race_detail_result_url", "horse_shoe_url",
]


# =============================================================================
# [FINAL CLEAN] 모바일/PC 주소 + GitHub 허브 저장소 고정
# =============================================================================
HUB_GITHUB_REPO_URL = "https://github.com/skytins3-png/maru-kra-final-clean"
HUB_GITHUB_REPO = "skytins3-png/maru-kra-final-clean"
PC_APP_URL = "https://maru-kra-final-clean.streamlit.app"
MOBILE_APP_URL = "https://maru-kra-final-clean.streamlit.app/?mode=mobile"

def get_hub_repo_url() -> str:
    return HUB_GITHUB_REPO_URL

def get_pc_app_url() -> str:
    return PC_APP_URL

def get_mobile_app_url() -> str:
    return MOBILE_APP_URL

def try_push_hub_file_to_github(relative_path: str, content_text: str, message: str = "MARU KRA hub update") -> bool:
    """GitHub 토큰이 있는 경우에만 허브 결과를 maru-kra-final-clean 저장소에 백업합니다.
    secrets 또는 환경변수 GITHUB_TOKEN / GH_TOKEN 이 없으면 조용히 로컬 저장만 사용합니다.
    """
    try:
        token = ""
        try:
            token = st.secrets.get("GITHUB_TOKEN", "") or st.secrets.get("GH_TOKEN", "")
        except Exception:
            token = ""
        token = token or os.environ.get("GITHUB_TOKEN", "") or os.environ.get("GH_TOKEN", "")
        if not token:
            return False

        import base64
        import requests
        api = f"https://api.github.com/repos/{HUB_GITHUB_REPO}/contents/{relative_path.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        sha = None
        r0 = requests.get(api, headers=headers, timeout=8)
        if r0.status_code == 200:
            sha = r0.json().get("sha")
        payload = {
            "message": message,
            "content": base64.b64encode(content_text.encode("utf-8")).decode("ascii"),
            "branch": "main",
        }
        if sha:
            payload["sha"] = sha
        r = requests.put(api, headers=headers, json=payload, timeout=10)
        return r.status_code in (200, 201)
    except Exception:
        return False


DERBYON_BUY_URL = "https://todayrace.kra.co.kr"
CLOUD_APP_URL = "https://maru-kra-mobile-final-m52adz9wjrob3vgtxdgvu9.streamlit.app"
CLOUD_MOBILE_URL = "https://maru-kra-mobile-final-m52adz9wjrob3vgtxdgvu9.streamlit.app/?mode=mobile"
CLOUD_PC_URL = "https://maru-kra-mobile-final-m52adz9wjrob3vgtxdgvu9.streamlit.app/?mode=pc"
KRA_BUY_URLS = {
    "서울": DERBYON_BUY_URL,
    "부산경남": DERBYON_BUY_URL,
    "제주": DERBYON_BUY_URL,
}

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def now_kst() -> datetime:
    return datetime.now(KST)


def today_kst() -> str:
    return now_kst().strftime("%Y%m%d")


def now_str() -> str:
    return now_kst().strftime("%Y-%m-%d %H:%M:%S")


def load_json_file(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json_file(path: Path, payload: Any) -> bool:
    try:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def load_local_settings() -> Dict[str, Any]:
    return load_json_file(LOCAL_SETTINGS_FILE, {})


def save_local_settings(payload: Dict[str, Any]) -> bool:
    current = load_local_settings()
    current.update(payload)
    return save_json_file(LOCAL_SETTINGS_FILE, current)


def secret_get(names: List[str], default: str = "") -> str:
    try:
        if "maru" in st.secrets:
            for n in names:
                if n in st.secrets["maru"]:
                    return str(st.secrets["maru"][n])
    except Exception:
        pass
    try:
        for n in names:
            if n in st.secrets:
                return str(st.secrets[n])
    except Exception:
        pass
    for n in names:
        val = os.environ.get(n)
        if val:
            return str(val)
    return default


def get_api_key() -> str:
    if st.session_state.get("api_key_saved"):
        return str(st.session_state.get("api_key_saved", "")).strip()
    local = load_local_settings()
    if local.get("api_key"):
        return str(local.get("api_key", "")).strip()
    return secret_get(["API_KEY", "api_key", "PUBLIC_DATA_API_KEY", "SERVICE_KEY", "serviceKey"], "").strip()


def get_api_key_source() -> str:
    """모바일에서 다시 입력하지 않도록 키가 어디서 적용됐는지 표시합니다."""
    if st.session_state.get("api_key_saved"):
        return "현재 세션 저장"
    local = load_local_settings()
    if local.get("api_key"):
        return "로컬 저장파일(maru_kra_data)"
    sec = secret_get(["API_KEY", "api_key", "PUBLIC_DATA_API_KEY", "SERVICE_KEY", "serviceKey"], "")
    if sec:
        return "Streamlit Secrets 또는 환경변수"
    return "없음"


def masked_api_key() -> str:
    key = get_api_key()
    if not key:
        return ""
    if len(key) <= 12:
        return "****"
    return key[:6] + "****" + key[-4:]


def get_url(key: str) -> str:
    val = secret_get([key, key.upper()], "")
    if val:
        return val
    return FORCE_DEFAULT_URLS.get(key, "")


def kra_buy_url(meet: str = "서울") -> str:
    # 더비온/오늘의경주 공식 구매표 진입 페이지.
    # 외부 앱에서 마번/금액 자동 입력·자동구매는 하지 않고, 사용자가 직접 선택/확정합니다.
    return KRA_BUY_URLS.get(str(meet), DERBYON_BUY_URL)


def derbyon_registered_mode() -> bool:
    """사용자가 더비온 온라인 회원 등록을 마친 경우 안내/버튼 문구를 구매표 중심으로 바꿉니다."""
    return bool(st.session_state.get("derbyon_registered", True))


def derbyon_notice_html(meet: str, race_no: Any, first_combo: str) -> str:
    mode_text = "더비온 등록완료 모드" if derbyon_registered_mode() else "더비온 등록 필요"
    status_text = "더비온 로그인 후 구매표에서 직접 입력·확정" if derbyon_registered_mode() else "더비온 본인인증/대면등록 후 이용"
    return f"""
<div style="max-width:560px; margin:14px auto; background:#eef6ff; color:#10233f; border-radius:18px; padding:14px 16px; border:1px solid #bfdbfe; font-weight:900;">
  <div style="font-size:1.05rem; color:#0f3b76; font-weight:1000; margin-bottom:8px;">✅ {mode_text}</div>
  <div>경마장 <b>{meet}</b> · 경주 <b>{race_no}R</b> · 삼쌍승 <b>{first_combo}</b></div>
  <div style="margin-top:6px; color:#475569;">{status_text}</div>
  <div style="margin-top:6px; color:#dc2626;">자동구매/자동결제 없음 · 바로구매는 공식 더비온에서 본인이 직접 누름</div>
</div>
"""


def mask_key(text: str) -> str:
    s = str(text or "")
    key = get_api_key()
    if key and key in s:
        s = s.replace(key, key[:5] + "****" + key[-4:] if len(key) > 10 else "****")
    return s


def safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(float(str(x).replace(",", "")))
    except Exception:
        return default


def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(str(x).replace(",", ""))
    except Exception:
        return default

# -----------------------------------------------------------------------------
# CSS
# -----------------------------------------------------------------------------
def css() -> None:
    st.markdown(
        """
<style>
.main .block-container {padding-top: 0.7rem; max-width: 1180px;}
.hero {background:linear-gradient(135deg,#031c49,#042a67,#001738); color:#fff; border-radius:30px; padding:28px 28px; box-shadow:0 10px 30px rgba(0,0,0,.18);}
.hero h2 {font-size:3.0rem; line-height:1.05; margin:0; color:#fff; font-weight:1000; letter-spacing:-1px;}
.hero .muted {color:#d6ddf2; font-size:1.15rem; margin-top:8px; font-weight:800;}
.focus-card {background:#fff; border:5px solid #12a038; border-radius:34px; padding:28px 26px 24px 26px; box-shadow:0 8px 28px rgba(0,0,0,.08);}
.focus-badge {display:inline-block; background:#e8f7e9; color:#13792f; padding:12px 26px; border-radius:18px; font-weight:1000; font-size:1.55rem; margin-bottom:14px;}
.focus-combo {font-size:clamp(4.8rem, 15vw, 8.6rem); font-weight:1000; color:#0b9d2e; text-align:center; letter-spacing:3px; line-height:1.0; margin:6px 0 16px 0;}
.reco-meta {font-size:1.45rem; color:#1f2937; font-weight:900; text-align:center; margin:8px 0 12px 0;}
.metric-wrap {display:flex; gap:14px;}
.metric-box {flex:1; text-align:center; padding:6px 8px; border-radius:18px; background:#f8fafc; border:1px solid #e5e7eb;}
.metric-box .m-title {font-size:1.25rem; font-weight:900; color:#172554; margin-bottom:6px;}
.metric-box .m-value-green {font-size:3.0rem; font-weight:1000; color:#109b2e; line-height:1.0;}
.metric-box .m-value-orange {font-size:3.0rem; font-weight:1000; color:#f48b00; line-height:1.0;}
.metric-box .m-value-blue {font-size:2.5rem; font-weight:1000; color:#1d4ed8; line-height:1.0;}
.manual-box {background:#fff7ed;border:3px solid #fb923c;border-radius:24px;padding:18px 18px;margin:14px 0;box-shadow:0 6px 20px rgba(0,0,0,.06);}
.manual-title {font-size:1.55rem;font-weight:1000;color:#9a3412;}
.manual-note {font-size:1.05rem;font-weight:800;color:#7c2d12;margin-top:6px;}
.bigline {font-size:2.3rem; font-weight:1000; color:#111827; text-align:center; padding:14px; background:#f8fafc; border:2px dashed #94a3b8; border-radius:20px;}
.info-box-ok {background:#efffed; border:1px solid rgba(25,135,84,.25); border-radius:18px; padding:15px 16px; font-size:1.1rem; font-weight:800;}
.info-box-warn {background:#fff7e8; border:1px solid rgba(217,119,6,.28); border-radius:18px; padding:15px 16px; font-size:1.1rem; font-weight:800;}
.betting-card {background:#ffffff;border:3px solid #0ea5e9;border-radius:26px;padding:18px 18px;margin:12px 0;box-shadow:0 6px 20px rgba(0,0,0,.06);}
.betting-title {font-size:1.45rem;font-weight:1000;color:#075985;margin-bottom:8px;}
.mobile-shell {background:#050505; color:#fff; min-height:100vh; padding:8px 2px 18px 2px;}
.mobile-phone {background:linear-gradient(180deg,#0e0e0e 0%,#030303 100%); border:2px solid #d5a83c; border-radius:34px; padding:14px 12px 16px 12px; box-shadow:0 0 34px rgba(213,168,60,.28), inset 0 0 20px rgba(255,218,119,.05); color:#fff; max-width:470px; margin:0 auto;}
.mobile-topbar {display:flex; justify-content:space-between; align-items:center; color:#f6cf6b; font-weight:1000; font-size:1.05rem; padding:4px 4px 10px 4px;}
.mobile-step {text-align:center; color:#f7d77c; font-weight:1000; font-size:1.08rem; padding:5px 0 8px 0;}
.mobile-glow-title {border:1.5px solid #d5a83c; background:linear-gradient(180deg,#2b2109,#0b0b0b); border-radius:20px; padding:10px 8px; text-align:center; box-shadow:0 0 18px rgba(213,168,60,.30);}
.mobile-glow-title .small {color:#f9dc7e; font-weight:1000; font-size:.95rem;}
.mobile-glow-title .race {font-size:2.05rem; font-weight:1000; color:#fff; line-height:1.05; margin-top:7px;}
.mobile-glow-title .combo-main {font-size:2.45rem; font-weight:1000; color:#f2c451; line-height:1.0; margin:4px 0;}
.mobile-glow-title .combo-sub {font-size:1.25rem; font-weight:1000; color:#fff; margin-top:7px;}
.mobile-alert {background:linear-gradient(180deg,#ef343d,#b7121c); color:#fff; border-radius:18px; padding:14px 10px; text-align:center; font-size:1.35rem; font-weight:1000; margin:12px 0 12px 0; box-shadow:0 8px 18px rgba(185,18,28,.28);}
.mobile-main-combo {text-align:center; border:2px solid #d5a83c; border-radius:24px; padding:14px 10px; background:linear-gradient(180deg,#111,#050505); margin-bottom:12px;}
.mobile-main-combo .race {font-size:1.9rem; font-weight:1000; color:#fff; line-height:1.05;}
.mobile-purchase-block {display:flex; align-items:center; justify-content:space-between; gap:8px; border:2px solid #d5a83c; border-radius:18px; padding:14px 12px; margin:10px 0; background:linear-gradient(180deg,#151515,#070707);}
.mobile-purchase-block.secondary {border-color:#8f742b; background:linear-gradient(180deg,#111,#050505);}
.mobile-purchase-block .bettype {font-size:1.45rem; font-weight:1000; color:#f2c451; min-width:4.3rem;}
.mobile-purchase-block .numbers {font-size:clamp(2.8rem,14vw,4.5rem); font-weight:1000; color:#fff; letter-spacing:2px; line-height:1;}
.mobile-purchase-block .money {font-size:1.75rem; font-weight:1000; color:#f2c451; white-space:nowrap;}
.mobile-mini-grid {display:grid; grid-template-columns:1fr 1fr 1fr; gap:7px; margin:12px 0;}
.mobile-mini {background:#111; border:1px solid #4b4b4b; border-radius:15px; padding:9px 5px; text-align:center;}
.mobile-mini b {display:block; color:#f4d477; font-size:.78rem;}
.mobile-mini span {font-size:1.05rem; font-weight:1000; color:#fff;}
.mobile-form-preview {background:#f8fafc; color:#111; border-radius:22px; padding:13px 12px; margin:12px 0; border:2px solid #1e4fbf;}
.mobile-form-preview .title {background:#1766e8; color:#fff; border-radius:12px; display:inline-block; padding:6px 12px; font-weight:1000; margin-bottom:8px;}
.mobile-form-row {display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #e5e7eb; font-weight:900;}
.mobile-form-row span:last-child {background:#fff; border:1px solid #d1d5db; border-radius:9px; padding:6px 10px; min-width:45%; text-align:center;}
.mobile-copy-box {background:linear-gradient(180deg,#ffd96d,#d39a24); color:#111; border-radius:18px; padding:13px 12px; font-weight:1000; text-align:center; font-size:1.1rem; margin:10px 0;}
.mobile-safe-note {color:#cbd5e1; font-size:.92rem; font-weight:800; line-height:1.45; padding:9px 4px; text-align:center;}
.mobile-footer-line {display:flex; justify-content:space-around; gap:6px; color:#f8d777; font-weight:1000; font-size:.92rem; border-top:1px solid rgba(213,168,60,.45); margin-top:12px; padding-top:12px;}

.mobile-budget {background:linear-gradient(180deg,#241b08,#080808); border:2px solid #d5a83c; border-radius:22px; padding:12px; text-align:center; margin:10px 0;}
.mobile-budget .title {font-weight:1000; color:#f8d777; font-size:1.0rem;}
.mobile-budget .amount {font-weight:1000; color:#fff; font-size:2.1rem; line-height:1.0; margin-top:4px;}
.mobile-three-cards {display:grid; grid-template-columns:1fr 1fr 1fr; gap:7px; margin:12px 0;}
.mobile-reco-card {background:linear-gradient(180deg,#181818,#050505); border:2px solid #d5a83c; border-radius:18px; padding:10px 5px; text-align:center; box-shadow:0 0 15px rgba(213,168,60,.18);}
.mobile-reco-card .card-title {font-size:.82rem; font-weight:1000; color:#f8d777;}
.mobile-reco-card .card-combo {font-size:1.45rem; font-weight:1000; color:#fff; margin:5px 0; letter-spacing:1px;}
.mobile-reco-card .card-sub {font-size:.78rem; font-weight:900; color:#cbd5e1;}
.mobile-ticket-section {border:2px solid #d5a83c; border-radius:22px; padding:11px 9px; background:linear-gradient(180deg,#101010,#030303); margin:12px 0;}
.mobile-ticket-title {font-weight:1000; font-size:1.1rem; color:#f8d777; text-align:center; margin-bottom:8px;}
.mobile-ticket-grid {display:grid; grid-template-columns:1fr 1fr; gap:7px;}
.mobile-ticket {background:#f8fafc; color:#111; border-radius:13px; padding:8px 7px; font-weight:1000; display:flex; justify-content:space-between; align-items:center; border:1px solid #e5e7eb;}
.mobile-ticket .num {background:#111827; color:#fff; border-radius:50%; width:24px; height:24px; display:inline-flex; align-items:center; justify-content:center; font-size:.78rem; margin-right:4px;}
.mobile-ticket .combo {font-size:1.05rem; letter-spacing:1px;}
.mobile-ticket .won {font-size:.83rem; color:#b45309; white-space:nowrap;}
.mobile-copy-area {background:#fff7d6; color:#111; border:2px dashed #d59a22; border-radius:16px; padding:10px; font-size:.92rem; font-weight:900; line-height:1.35; white-space:pre-wrap;}
.stButton > button, .stLinkButton a {width:100%; border-radius:18px !important; min-height:58px !important; font-weight:900 !important; font-size:1.25rem !important;}
[data-testid="stMetricValue"] {font-size:2rem !important; font-weight:1000 !important;}
[data-testid="stExpander"] summary p {font-size:1.1rem !important; font-weight:900 !important;}
@media (max-width: 760px) {
  .main .block-container {padding:0.45rem 0.55rem 1.5rem 0.55rem;}
  .hero {border-radius:22px; padding:20px 18px;}
  .hero h2 {font-size:2.25rem; line-height:1.04;}
  .hero .muted {font-size:1rem;}
  .focus-card {border-radius:24px; padding:20px 12px 18px 12px; border-width:4px;}
  .focus-badge {font-size:1.1rem; padding:8px 14px; border-radius:14px;}
  .focus-combo {font-size:clamp(4.8rem, 21vw, 7.2rem); line-height:.95; margin:8px 0 12px 0;}
  .reco-meta {font-size:1.05rem; margin:4px 0 10px 0;}
  .metric-wrap {gap:4px;}
  .metric-box {padding:6px 3px;}
  .metric-box .m-title {font-size:.88rem; margin-bottom:6px;}
  .metric-box .m-value-green, .metric-box .m-value-orange {font-size:1.85rem;}
  .metric-box .m-value-blue {font-size:1.25rem; word-break:keep-all;}
  .bigline {font-size:1.45rem; padding:12px 8px;}
  .stButton > button, .stLinkButton a {min-height:64px !important; font-size:1.05rem !important;}
}
</style>
""",
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# API ON/OFF
# -----------------------------------------------------------------------------
def default_onoff_state() -> Dict[str, bool]:
    return {k: (k in CORE_DEFAULT_API_KEYS) for k, _ in API_LABELS}


def get_api_switches() -> Dict[str, bool]:
    defaults = default_onoff_state()
    return {k: bool(st.session_state.get(f"api_on_{k}", defaults.get(k, True))) for k, _ in API_LABELS}


def render_api_onoff_panel() -> None:
    with st.sidebar.expander("🔌 실시간 API ON/OFF", expanded=False):
        # Streamlit 위젯은 key 생성 뒤 같은 실행에서 값을 바꾸면 오류/경고가 납니다.
        # 그래서 기본값은 위젯 생성 전에만 넣고, 전체 ON/OFF는 플래그로 처리합니다.
        if "api_master_on" not in st.session_state:
            st.session_state["api_master_on"] = True
        defaults = default_onoff_state()
        for k, _ in API_LABELS:
            st.session_state.setdefault(f"api_on_{k}", defaults.get(k, True))
        st.session_state.setdefault("force_all_apis", False)

        st.caption("현장에서 HTTP 500 나는 항목만 OFF 해도 앱은 계속 돌아갑니다.")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("핵심 ON", width="stretch", key="api_bulk_core_on"):
                st.session_state["api_master_on"] = True
                st.session_state["force_all_apis"] = False
                for k, _ in API_LABELS:
                    st.session_state[f"api_on_{k}"] = k in CORE_DEFAULT_API_KEYS
                st.rerun()
        with c2:
            if st.button("전체 ON", width="stretch", key="api_bulk_all_on"):
                st.session_state["api_master_on"] = True
                st.session_state["force_all_apis"] = True
                for k, _ in API_LABELS:
                    st.session_state[f"api_on_{k}"] = True
                st.rerun()
        with c3:
            if st.button("전체 OFF", width="stretch", key="api_bulk_all_off"):
                st.session_state["api_master_on"] = False
                st.session_state["force_all_apis"] = False
                for k, _ in API_LABELS:
                    st.session_state[f"api_on_{k}"] = False
                st.rerun()

        st.toggle(
            "전체 실시간 API 호출",
            key="api_master_on",
            help="끄면 API를 부르지 않고 캐시/검증대기 화면만 확인합니다.",
        )
        for k, label in API_LABELS:
            st.toggle(label, key=f"api_on_{k}")
        switches = get_api_switches()
        if bool(st.session_state.get("force_all_apis", False)) and bool(st.session_state.get("api_master_on", True)):
            st.success("전체 ON 강제 적용: 이번 호출 대상은 26/26개입니다.")
        st.caption(f"현재 ON: {sum(1 for v in switches.values() if v)}/26개")

# -----------------------------------------------------------------------------
# API request/parsing
# -----------------------------------------------------------------------------
def add_or_replace_params(url: str, params: Dict[str, Any]) -> str:
    parsed = urlparse(url)
    q = dict(parse_qsl(parsed.query, keep_blank_values=True))
    for k, v in params.items():
        if v is not None and str(v) != "":
            q[k] = str(v)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(q, doseq=True), parsed.fragment))


def endpoint_with_placeholders(url: str, rc_date: str, meet: str, race_no: int) -> str:
    key = get_api_key()
    repl = {
        "{serviceKey}": key, "{SERVICE_KEY}": key, "{api_key}": key, "{API_KEY}": key,
        "{today}": rc_date, "{ymd}": rc_date, "{rcDate}": rc_date, "{raceDate}": rc_date,
        "{raceNo}": str(race_no), "{rcNo}": str(race_no), "{meet}": meet, "{track_place}": meet,
    }
    out = str(url or "")
    for a, b in repl.items():
        out = out.replace(a, b)
    return out


def request_variants(base_url: str, rc_date: str, meet: str, race_no: int) -> List[str]:
    url = endpoint_with_placeholders(base_url, rc_date, meet, race_no)
    key = get_api_key()
    base_params = {"serviceKey": key, "pageNo": 1, "numOfRows": 100}
    variants: List[str] = []
    for typ_key, typ_val in [("resultType", "json"), ("_type", "json"), ("type", "json")]:
        p = dict(base_params)
        p[typ_key] = typ_val
        variants.append(add_or_replace_params(url, p))
    for date_name in ["rcDate", "raceDate", "meetDate", "ymd"]:
        for race_name in ["rcNo", "raceNo", "raceNum"]:
            p = dict(base_params)
            p.update({date_name: rc_date, race_name: race_no, "resultType": "json"})
            variants.append(add_or_replace_params(url, p))
    meet_map = {"서울": "1", "제주": "2", "부산경남": "3", "부경": "3", "부산": "3"}
    for meet_name in ["meet", "meetCd", "rcourse", "raceTrack"]:
        p = dict(base_params)
        p.update({"rcDate": rc_date, "rcNo": race_no, meet_name: meet_map.get(meet, meet), "resultType": "json"})
        variants.append(add_or_replace_params(url, p))
    if "serviceKey=" in url:
        variants.append(url)
    seen, out = set(), []
    for v in variants:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def json_to_df(obj: Any) -> pd.DataFrame:
    if obj is None:
        return pd.DataFrame()
    candidates: Any = []
    if isinstance(obj, dict):
        paths = [
            ["response", "body", "items", "item"], ["response", "body", "item"],
            ["body", "items", "item"], ["items", "item"], ["data"], ["result"], ["list"],
        ]
        for path in paths:
            cur: Any = obj
            ok = True
            for p in path:
                if isinstance(cur, dict) and p in cur:
                    cur = cur[p]
                else:
                    ok = False
                    break
            if ok:
                candidates = cur
                break
        if candidates == []:
            def walk(x: Any):
                if isinstance(x, list) and (not x or isinstance(x[0], dict)):
                    return x
                if isinstance(x, dict):
                    for v in x.values():
                        got = walk(v)
                        if got is not None:
                            return got
                return None
            got = walk(obj)
            candidates = got if got is not None else obj
    else:
        candidates = obj
    if isinstance(candidates, dict):
        candidates = [candidates]
    if not isinstance(candidates, list):
        return pd.DataFrame()
    try:
        return pd.json_normalize(candidates)
    except Exception:
        try:
            return pd.DataFrame(candidates)
        except Exception:
            return pd.DataFrame()


def xml_to_df(txt: str) -> pd.DataFrame:
    try:
        root = ET.fromstring(txt)
        rows = []
        for item in root.findall(".//item"):
            rows.append({c.tag: c.text for c in item})
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


def save_live_cache(data: Dict[str, pd.DataFrame], status: pd.DataFrame) -> None:
    payload: Dict[str, Any] = {"saved_at": now_str(), "data": {}, "status": []}
    try:
        for k, df in data.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                payload["data"][k] = df.head(300).astype(str).to_dict("records")
        if isinstance(status, pd.DataFrame) and not status.empty:
            payload["status"] = status.astype(str).to_dict("records")
        save_json_file(LIVE_CACHE_FILE, payload)
    except Exception:
        pass


def load_live_cache() -> Dict[str, pd.DataFrame]:
    payload = load_json_file(LIVE_CACHE_FILE, {})
    out: Dict[str, pd.DataFrame] = {}
    try:
        for k, rows in payload.get("data", {}).items():
            df = pd.DataFrame(rows)
            if not df.empty:
                out[k] = df
    except Exception:
        pass
    return out



def safe_get_url(req_url: str, timeout: int = 6):
    """KRA/공공데이터 SSL 인증서 오류가 나도 앱이 멈추지 않도록 1회 자동 재시도."""
    try:
        return requests.get(req_url, timeout=timeout)
    except requests.exceptions.SSLError:
        return requests.get(req_url, timeout=timeout, verify=False)

def fetch_one_api(key: str, rc_date: str, meet: str, race_no: int) -> Tuple[pd.DataFrame, str, str]:
    url = get_url(key)
    if not url:
        return pd.DataFrame(), "URL 없음", ""
    if not get_api_key() and "serviceKey=" not in url:
        return pd.DataFrame(), "API_KEY 없음", ""
    last_msg, last_url = "", ""
    for req_url in request_variants(url, rc_date, meet, race_no):
        last_url = req_url
        try:
            r = safe_get_url(req_url, timeout=6)
            if r.status_code != 200:
                last_msg = f"HTTP {r.status_code}"
                continue
            txt = r.text.strip()
            err_words = [
                "SERVICE_KEY_IS_NOT_REGISTERED", "INVALID_REQUEST_PARAMETER", "SERVICE_ACCESS_DENIED",
                "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR", "NO_OPENAPI_SERVICE_ERROR",
            ]
            if any(w in txt for w in err_words):
                last_msg = txt[:180]
                continue
            ctype = r.headers.get("content-type", "").lower()
            if txt.startswith("{") or txt.startswith("[") or "json" in ctype:
                try:
                    df = json_to_df(r.json())
                except Exception:
                    df = pd.DataFrame()
            else:
                df = xml_to_df(txt)
            if not df.empty:
                return df, "OK", req_url
            last_msg = "응답 200 / 데이터 0건"
        except Exception as e:
            last_msg = str(e)[:180]
    return pd.DataFrame(), last_msg or "실패", last_url


def fetch_all_live(rc_date: str, meet: str, race_no: int, selected: List[str]) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    master_on = bool(st.session_state.get("api_master_on", True))
    switches = get_api_switches()
    data: Dict[str, pd.DataFrame] = {}
    status_rows: List[Dict[str, Any]] = []
    if not master_on:
        cache = load_live_cache()
        return cache, pd.DataFrame([{"API": "전체", "행수": sum(len(v) for v in cache.values()), "상태": "전체 OFF: 최근 캐시/샘플 사용", "URL": ""}])
    for key, label in API_LABELS:
        if key not in selected:
            status_rows.append({"API": label, "key": key, "행수": 0, "상태": "선택 안 함", "URL": ""})
            continue
        if not switches.get(key, True):
            status_rows.append({"API": label, "key": key, "행수": 0, "상태": "OFF: 건너뜀", "URL": ""})
            continue
        # 결과대기 API는 경주시간 25분 전부터만 재접속합니다.
        if key in PENDING_RESULT_API_KEYS:
            try:
                schedule_df_for_retry = extract_schedule_from_data(data, rc_date, meet) if "extract_schedule_from_data" in globals() else pd.DataFrame()
                allow_pending_retry, pending_note, pending_dt = pending_keys_due_for_retry(schedule_df_for_retry, meet, int(race_no))
            except Exception:
                allow_pending_retry, pending_note, pending_dt = False, "결과대기 API 재접속 보류", None
            if not allow_pending_retry:
                cached = load_success_api_cache(key, rc_date, meet, int(race_no)) if "load_success_api_cache" in globals() else pd.DataFrame()
                if cached is not None and not cached.empty:
                    data[key] = cached
                    status_rows.append({"key": key, "API": label, "행수": len(cached), "상태": "PENDING_TIME_CACHE", "분류": "CACHE", "해석": pending_note + " · 캐시사용", "URL": ""})
                else:
                    status_rows.append({"key": key, "API": label, "행수": 0, "상태": "PENDING_TIME_WAIT", "분류": "PENDING", "해석": pending_note, "URL": ""})
                continue

        df, msg, used_url = fetch_one_api(key, rc_date, meet, race_no)
        if not df.empty:
            data[key] = df
        status_rows.append({"API": label, "key": key, "행수": int(len(df)), "상태": msg, "URL": mask_key(used_url)})
        time.sleep(0.03)
    status = pd.DataFrame(status_rows)
    if data:
        save_live_cache(data, status)
    else:
        cache = load_live_cache()
        if cache:
            data = cache
            status_rows.append({"API": "캐시", "key": "cache", "행수": sum(len(v) for v in cache.values()), "상태": "실시간 0건 → 최근 캐시 사용", "URL": ""})
            status = pd.DataFrame(status_rows)
    try:
        status.to_csv(API_STATUS_FILE, index=False, encoding="utf-8-sig")
    except Exception:
        pass
    return data, status

# -----------------------------------------------------------------------------
# Data normalization / scoring
# -----------------------------------------------------------------------------
def normalize_meet(x: Any) -> str:
    s = str(x or "").strip()
    if s in ["1", "서울", "SEOUL", "Seoul", "seoul"]:
        return "서울"
    if s in ["2", "제주", "JEJU", "Jeju", "jeju"]:
        return "제주"
    if s in ["3", "부산경남", "부경", "부산", "BUSAN", "Busan", "busan"]:
        return "부산경남"
    return s


def find_col(df: pd.DataFrame, names: List[str]) -> Optional[str]:
    if df is None or df.empty:
        return None
    lower = {str(c).lower(): c for c in df.columns}
    for n in names:
        if str(n).lower() in lower:
            return lower[str(n).lower()]
    for c in df.columns:
        cl = str(c).lower()
        for n in names:
            if str(n).lower() in cl:
                return c
    return None


def horse_no_col(df: pd.DataFrame) -> Optional[str]:
    return find_col(df, ["chulNo", "출전번호", "출전마번", "마번", "horseNo", "hrNo", "no"])


def horse_name_col(df: pd.DataFrame) -> Optional[str]:
    return find_col(df, ["hrName", "horseName", "마명", "경주마명", "name"])


def current_filter(df: pd.DataFrame, rc_date: str, meet: str, race_no: int) -> pd.DataFrame:
    """날짜/경마장/경주번호가 있는 데이터는 반드시 현재 경주로 필터링합니다.
    예전 버전은 필터 결과가 비면 원본 전체를 반환해서 서울 1R 추천이 제주 6R처럼 보이는 문제가 있었습니다.
    이제는 매칭 실패 시 빈 DataFrame을 반환하여 샘플/다른 경주 추천이 실전 화면에 섞이지 않게 합니다.
    """
    if df is None or df.empty:
        return pd.DataFrame()
    d = df.copy()
    try:
        d.columns = d.columns.astype(str).str.strip()
    except Exception:
        pass
    date_col = find_col(d, ["rcDate", "raceDate", "meetDate", "날짜", "경주일자", "date"] )
    meet_col = find_col(d, ["meet", "meetCd", "rcourse", "경마장", "경마장명", "시행경마장"] )
    rc_col = find_col(d, ["rcNo", "raceNo", "경주번호", "race_no", "경주"] )
    had_filter_col = bool(date_col or meet_col or rc_col)

    try:
        if date_col:
            ds = d[date_col].astype(str).str.replace("-", "", regex=False).str.strip().str[:8]
            target_date = str(rc_date).replace("-", "")[:8]
            tmp = d[ds == target_date]
            if tmp.empty:
                return pd.DataFrame(columns=d.columns)
            d = tmp
    except Exception:
        pass
    try:
        if meet_col:
            tmp = d[d[meet_col].apply(normalize_meet) == normalize_meet(meet)]
            if tmp.empty:
                return pd.DataFrame(columns=d.columns)
            d = tmp
    except Exception:
        pass
    try:
        if rc_col:
            rs = pd.to_numeric(d[rc_col].map(_safe_race_no), errors="coerce")
            tmp = d[rs == int(race_no)]
            if tmp.empty:
                return pd.DataFrame(columns=d.columns)
            d = tmp
    except Exception:
        pass
    if had_filter_col and d.empty:
        return pd.DataFrame(columns=df.columns)
    return d


def sample_data() -> pd.DataFrame:
    df = pd.DataFrame([
        {"마번": 5, "마명": "마루스피드", "레이팅": 78, "최근순위": 2, "승률": 18, "복승률": 42, "예상배당": 9.2, "체중변화": -2, "기수점수": 75, "인기": 4},
        {"마번": 11, "마명": "그린파워", "레이팅": 75, "최근순위": 3, "승률": 15, "복승률": 38, "예상배당": 7.8, "체중변화": -1, "기수점수": 72, "인기": 5},
        {"마번": 2, "마명": "블루런", "레이팅": 72, "최근순위": 4, "승률": 12, "복승률": 35, "예상배당": 12.5, "체중변화": 0, "기수점수": 69, "인기": 7},
        {"마번": 7, "마명": "라스트킹", "레이팅": 70, "최근순위": 5, "승률": 10, "복승률": 30, "예상배당": 15.4, "체중변화": 2, "기수점수": 67, "인기": 8},
        {"마번": 3, "마명": "해피로드", "레이팅": 66, "최근순위": 6, "승률": 8, "복승률": 25, "예상배당": 22.0, "체중변화": -4, "기수점수": 65, "인기": 9},
        {"마번": 9, "마명": "스톰로드", "레이팅": 64, "최근순위": 7, "승률": 7, "복승률": 20, "예상배당": 31.0, "체중변화": 1, "기수점수": 62, "인기": 10},
    ])
    df["데이터상태"] = "샘플"
    df["실전검증"] = "N"
    return df


def build_base_horses(data: Dict[str, pd.DataFrame], rc_date: str, meet: str, race_no: int) -> pd.DataFrame:
    priority = ["entry_url", "body_url", "gear_url", "today_odds_url", "odds_url", "rating_url", "horse_url"]
    rows: Dict[int, Dict[str, Any]] = {}
    for key in priority:
        df = current_filter(data.get(key, pd.DataFrame()), rc_date, meet, race_no)
        if df is None or df.empty:
            continue
        no_col = horse_no_col(df)
        if not no_col:
            continue
        name_col = horse_name_col(df)
        for _, r in df.iterrows():
            try:
                n = int(float(r.get(no_col)))
            except Exception:
                continue
            if not 1 <= n <= 20:
                continue
            rows.setdefault(n, {"마번": n, "마명": f"{n}번", "근거API": []})
            if name_col and str(r.get(name_col, "")).strip():
                rows[n]["마명"] = str(r.get(name_col)).strip()
            rows[n]["근거API"].append(key.replace("_url", ""))
    if not rows:
        return sample_data()
    out = pd.DataFrame(list(rows.values())).sort_values("마번")
    out["데이터상태"] = "실시간"
    out["실전검증"] = "Y"
    return out


def merge_score_features(base: pd.DataFrame, data: Dict[str, pd.DataFrame], rc_date: str, meet: str, race_no: int) -> pd.DataFrame:
    h = base.copy()
    defaults = {"레이팅": 60, "최근순위": 5, "승률": 8, "복승률": 25, "예상배당": 12.0, "체중변화": 0, "기수점수": 65, "인기": 7}
    for c, v in defaults.items():
        if c not in h.columns:
            h[c] = v

    def map_by_no(key: str, target_col: str, candidate_cols: List[str]):
        df = current_filter(data.get(key, pd.DataFrame()), rc_date, meet, race_no)
        if df is None or df.empty:
            return
        no_col = horse_no_col(df)
        val_col = find_col(df, candidate_cols)
        if not no_col or not val_col:
            return
        tmp = df[[no_col, val_col]].copy()
        tmp[no_col] = pd.to_numeric(tmp[no_col], errors="coerce")
        tmp = tmp.dropna(subset=[no_col])
        mp = dict(zip(tmp[no_col].astype(int), tmp[val_col]))
        h[target_col] = h["마번"].map(mp).fillna(h[target_col])

    map_by_no("rating_url", "레이팅", ["rating", "레이팅", "rt", "ratingValue"])
    map_by_no("race_record_url", "최근순위", ["ord", "rank", "chaksun", "최근순위", "순위"])
    map_by_no("odds_url", "예상배당", ["odds", "배당", "winOdds", "dividend", "배당률"])
    map_by_no("today_odds_url", "예상배당", ["odds", "배당", "winOdds", "dividend", "배당률"])
    map_by_no("body_url", "체중변화", ["wgBudam", "weightDiff", "체중변화", "증감", "diff"])
    map_by_no("popularity_url", "인기", ["popRank", "popularity", "인기", "인기순위"])
    map_by_no("jockey_change_url", "기수점수", ["jockeyScore", "기수점수"])

    fallback = sample_data()
    for c in defaults:
        fb = float(pd.to_numeric(fallback[c], errors="coerce").median()) if c in fallback else defaults[c]
        h[c] = pd.to_numeric(h[c], errors="coerce").fillna(fb)
    return h


def fetch_weather(meet: str) -> Dict[str, Any]:
    coords = {"서울": (37.4438, 127.0165), "부산경남": (35.1545, 128.8782), "제주": (33.4097, 126.3934)}
    lat, lon = coords.get(meet, coords["서울"])
    env = {"날씨": "기본", "강수": 0.0, "바람": 2.0, "주로": "표준", "기온": 20.0}
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,wind_speed_10m&timezone=Asia%2FSeoul"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            cur = r.json().get("current", {})
            rain = float(cur.get("precipitation", 0) or 0)
            wind = float(cur.get("wind_speed_10m", 0) or 0)
            temp = float(cur.get("temperature_2m", 20) or 20)
            env.update({"강수": rain, "바람": wind, "기온": temp})
            env["날씨"] = "비" if rain > 0 else ("강풍" if wind >= 8 else "맑음/흐림")
            env["주로"] = "불량/습" if rain > 1 else ("건조" if temp >= 27 and rain == 0 else "표준")
    except Exception:
        pass
    return env


def score_and_recommend(horses: pd.DataFrame, env: Dict[str, Any], sim_count: int, risk_mode: str) -> Tuple[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]:
    """안정형/변수형/고배당형 3추천창을 동시에 만드는 핵심 분석 엔진.

    목적:
    - 평소 성적 좋은 말만 뽑지 않음
    - 기수변경, 체중변화, 거리/주로/경기장 변수, 인기 낮음+배당 높음 같은 구멍마 신호를 별도 점수화
    - 모바일에는 3추천창 × 각 6순열 = 삼쌍승 18장, 18,000원 수동구매표로 전달
    """
    df = horses.copy()
    for c in ["레이팅", "최근순위", "승률", "복승률", "예상배당", "체중변화", "기수점수", "인기"]:
        df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

    odds = df["예상배당"].replace(0, 12).clip(1, 120)
    recent_bad = df["최근순위"].clip(1, 12)
    popularity = df["인기"].replace(0, 12).clip(1, 20)
    body_abs = df["체중변화"].abs().clip(0, 18)

    # 1) 안정점수: 기본 능력, 최근 폼, 기수, 복승률 중심
    rating_score = df["레이팅"].clip(0, 120) / 120 * 25
    recent_score = (12 - recent_bad) / 11 * 20
    win_score = df["승률"].clip(0, 50) / 50 * 15
    place_score = df["복승률"].clip(0, 80) / 80 * 15
    jockey_score = df["기수점수"].clip(0, 100) / 100 * 12
    body_penalty = body_abs * 0.55
    popularity_bonus = (20 - popularity) / 19 * 5

    # 2) 변수점수: 평소 부진하지만 오늘 조건 변화로 급상승할 가능성
    # - 체중 변화는 너무 크면 위험이지만 3~8kg 구간은 컨디션 변화 신호로 가산
    body_signal = body_abs.apply(lambda x: 9 if 3 <= x <= 8 else (5 if 8 < x <= 12 else (2 if 1 <= x < 3 else 0)))
    jockey_change_signal = df["기수점수"].apply(lambda x: 8 if x >= 70 else (4 if x >= 50 else 0))
    poor_recent_rebound = recent_bad.apply(lambda x: 7 if x >= 7 else (3 if x >= 5 else 0))
    track_signal = 3 if env.get("주로") in ["불량/습", "건조"] else 1
    weather_signal = 2 if env.get("날씨") in ["비", "강풍"] else 0
    df["변수점수"] = (body_signal + jockey_change_signal + poor_recent_rebound + track_signal + weather_signal).round(2)

    # 3) 배당가치점수: 인기 낮고 배당 높으나 너무 황당하지 않은 구간을 포착
    odds_value = odds.apply(lambda x: 12 if 8 <= x <= 35 else (7 if 35 < x <= 60 else (4 if 5 <= x < 8 else 0)))
    low_pop_signal = popularity.apply(lambda x: 8 if x >= 7 else (4 if x >= 5 else 0))
    df["고배당점수"] = (odds_value + low_pop_signal + df["변수점수"] * 0.8).round(2)

    env_adj = 0
    if env.get("주로") in ["불량/습", "건조"]:
        env_adj = random.uniform(-1.0, 1.0)

    df["안정점수"] = (rating_score + recent_score + win_score + place_score + jockey_score + popularity_bonus - body_penalty + env_adj).round(2)
    df["점수"] = (df["안정점수"] * 0.62 + df["변수점수"] * 0.20 + df["고배당점수"] * 0.18).round(2)
    df["위험"] = (body_abs * 1.5 + recent_bad + popularity / 2 + (odds.clip(1, 80) / 12)).round(1)

    def role_row(r):
        if r["고배당점수"] >= max(r["안정점수"] * 0.35, 16):
            return "고배당 후보"
        if r["변수점수"] >= 14:
            return "변수마"
        if r["안정점수"] >= 45:
            return "안정마"
        return "보조마"

    df["추천역할"] = df.apply(role_row, axis=1)
    df["근거"] = df.apply(
        lambda r: f"{r['추천역할']} · 안정 {r['안정점수']:.1f} · 변수 {r['변수점수']:.1f} · 배당가치 {r['고배당점수']:.1f} · 최근 {int(r['최근순위'])}위권 · 체중 {int(r['체중변화']):+d}kg · 인기 {int(r['인기'])}",
        axis=1,
    )
    df = df.sort_values(["점수", "안정점수", "고배당점수"], ascending=[False, False, False]).reset_index(drop=True)

    # 안전 후보 / 변수 후보 / 고배당 후보를 분리해서 3추천창 구성
    all_nums = df["마번"].astype(int).tolist()
    stable_nums = df.sort_values(["안정점수", "점수"], ascending=[False, False])["마번"].astype(int).tolist()
    variable_nums = df.sort_values(["변수점수", "점수"], ascending=[False, False])["마번"].astype(int).tolist()
    value_nums = df.sort_values(["고배당점수", "예상배당", "점수"], ascending=[False, False, False])["마번"].astype(int).tolist()

    def unique_take(seq, used=None, n=3):
        used = set(used or [])
        out = []
        for x in seq + list(range(1, 21)):
            try:
                xx = int(x)
                if 1 <= xx <= 20 and xx not in out and (len(out) == 0 or xx not in used):
                    out.append(xx)
            except Exception:
                continue
            if len(out) >= n:
                break
        return out[:n]

    group1 = unique_take(stable_nums, n=3)  # 안정형: 축/상대/보조
    # 변수형: 축마 1마리를 깔고, 변수마/상대마를 섞음
    group2 = unique_take([group1[0]] + variable_nums + stable_nums, n=3)
    # 고배당형: 구멍마를 앞쪽에 두되, 축/상대도 포함
    group3 = unique_take(value_nums + group1 + variable_nums, n=3)
    triple_groups = [[str(x) for x in group1], [str(x) for x in group2], [str(x) for x in group3]]
    # 세 그룹이 너무 겹치면 기존 상위 9마리로 보정
    if len({tuple(g) for g in triple_groups}) < 3:
        triple_groups = make_triple_groups_from_nums(all_nums)
    triple_18 = expand_triple_18(triple_groups)

    axis = int(group1[0]); mate = int(group1[1]); sub = int(group1[2]); hole = int(group3[0])

    # Monte Carlo-ish combo list based on score weights.
    nums = all_nums or list(range(1, 13))
    weights = df["점수"].clip(lower=1).tolist() if not df.empty else [1] * len(nums)
    combos: List[Dict[str, Any]] = []
    rng_count = max(200, int(sim_count))
    for _ in range(rng_count):
        picked = random.choices(nums, weights=weights, k=min(3, len(nums)))
        uniq = []
        for p in picked:
            if p not in uniq:
                uniq.append(p)
        for p in nums:
            if len(uniq) >= 3:
                break
            if p not in uniq:
                uniq.append(p)
        c = uniq[:3]
        combos.append({"삼쌍승": f"{c[0]}→{c[1]}→{c[2]}", "삼복승": "-".join(map(str, sorted(c))), "축": c[0]})

    combo_df = pd.DataFrame(combos)
    top_exact = combo_df["삼쌍승"].value_counts().head(1)
    top_trio = combo_df["삼복승"].value_counts().head(1)
    exact = str(top_exact.index[0]) if not top_exact.empty else "→".join(map(str, group1))
    trio = str(top_trio.index[0]) if not top_trio.empty else "-".join(map(str, sorted(group1)))

    avg_score = float(df["점수"].head(3).mean()) if not df.empty else 0
    # 3추천창 신뢰도: 안정+변수+배당가치가 같이 높을수록 가산, 위험이 높으면 감산
    risk_penalty = float(df["위험"].head(3).mean()) if not df.empty else 20
    confidence = min(97, max(45, int(avg_score + df["변수점수"].head(3).mean() * 0.3 - risk_penalty * 0.15))) if not df.empty else 50
    est_odds = max(2.0, round(float(df["예상배당"].head(3).replace(0, 12).mean()), 1)) if not df.empty else 12.0
    risk_label = "낮음" if risk_penalty < 16 else ("중간" if risk_penalty < 28 else "높음")

    data_status = "샘플" if ("데이터상태" in df.columns and df["데이터상태"].astype(str).str.contains("샘플", na=False).any()) else "실시간"
    result = {
        "데이터상태": data_status, "실전검증": "N" if data_status == "샘플" else "Y",
        "축마": axis, "상대마": mate, "보조마": sub, "구멍마": hole,
        "공격삼쌍승": exact, "방어삼복승": trio, "추천금액": 18000,
        "삼쌍승3묶음": groups_to_text(triple_groups), "삼쌍승18조합": "; ".join(triple_18),
        "추천창1": "-".join(map(str, triple_groups[0])),
        "추천창2": "-".join(map(str, triple_groups[1])),
        "추천창3": "-".join(map(str, triple_groups[2])),
        "추천유형1": "안정형", "추천유형2": "변수형", "추천유형3": "고배당형",
        "판정": "18,000원 삼쌍승 18장 · 안정/변수/고배당 3추천창",
        "예상배당": est_odds, "신뢰도": confidence, "위험도": risk_label,
        "안정점수": round(float(df["안정점수"].head(3).mean()), 2) if not df.empty else 0,
        "변수점수": round(float(df["변수점수"].head(3).mean()), 2) if not df.empty else 0,
        "고배당점수": round(float(df["고배당점수"].head(3).mean()), 2) if not df.empty else 0,
        "근거": f"추천창1 안정형 {groups_to_text([triple_groups[0]])} / 추천창2 변수형 {groups_to_text([triple_groups[1]])} / 추천창3 고배당형 {groups_to_text([triple_groups[2]])} · 주로 {env.get('주로')} · 날씨 {env.get('날씨')} 반영",
    }
    return df, result, combos

# -----------------------------------------------------------------------------
# Hub / local save
# -----------------------------------------------------------------------------
def load_csv_safe(path: Path) -> pd.DataFrame:
    try:
        if path.exists():
            return pd.read_csv(path, encoding="utf-8-sig")
    except Exception:
        try:
            return pd.read_csv(path)
        except Exception:
            pass
    return pd.DataFrame()


def append_csv(path: Path, row: Dict[str, Any]) -> bool:
    try:
        df = pd.DataFrame([row])
        old = load_csv_safe(path)
        out = pd.concat([old, df], ignore_index=True) if not old.empty else df
        out.to_csv(path, index=False, encoding="utf-8-sig")
        return True
    except Exception:
        return False


def load_local_hub() -> pd.DataFrame:
    return load_csv_safe(LOCAL_HUB_FILE)


def load_bigdata() -> pd.DataFrame:
    return load_csv_safe(BIGDATA_FILE)


def save_hub_row(row: Dict[str, Any]) -> bool:
    ok1 = append_csv(LOCAL_HUB_FILE, row)
    ok2 = append_csv(BIGDATA_FILE, {**row, "결과상태": "대기", "성공실패": "미확인"})
    return ok1 and ok2

# -----------------------------------------------------------------------------
# Stable betting module
# -----------------------------------------------------------------------------
BET_TYPE_INFO = pd.DataFrame([
    ["단승", "1등 할 말 1마리", "필요", "이 말이 우승한다"],
    ["연승", "1~3등 안에 들 말 1마리", "상관없음", "우승까지는 몰라도 3착 안에는 온다"],
    ["복승", "1등·2등 말 2마리", "상관없음", "두 마리가 1·2등 안에 들어온다"],
    ["쌍승", "1등·2등 말 2마리", "필요", "1착과 2착 순서까지 맞힌다"],
    ["복연승", "1~3등 안에 들 말 2마리", "상관없음", "두 마리가 둘 다 3착 안에 들어온다"],
    ["삼복승", "1·2·3등 말 3마리", "상관없음", "세 마리가 모두 3착 안에 들어온다"],
    ["삼쌍승", "1·2·3등 말 3마리", "필요", "1착·2착·3착 순서까지 정확히 맞힌다"],
], columns=["승식", "맞히는 방식", "순서", "해석"])


def parse_exact_combo(exact: str, fallback: List[int]) -> List[int]:
    nums = [safe_int(x) for x in re.findall(r"\d+", str(exact or ""))]
    nums = [n for n in nums if n > 0]
    for n in fallback:
        if n not in nums:
            nums.append(n)
    return nums[:4]


def stable_plan_from_result(result: Dict[str, Any], budget: int = 18000, preset: str = "안정형") -> pd.DataFrame:
    axis = safe_int(result.get("축마", 7), 7)
    mate = safe_int(result.get("상대마", 3), 3)
    sub = safe_int(result.get("보조마", 10), 10)
    hole = safe_int(result.get("구멍마", 5), 5)
    if preset == "보수형":
        rows = [
            ["연승", f"{axis}", 15000, 1.5, "축마가 3착 안에 들어오면 방어"],
            ["복연승", f"{axis}-{mate}", 10000, 2.0, "축마+상대마가 둘 다 3착 안"],
            ["복승", f"{axis}-{mate}", 3000, 5.0, "두 마리가 1·2착이면 수익"],
            ["삼복승", f"{axis}-{mate}-{sub}", 2000, 12.0, "세 마리가 모두 3착 안"],
        ]
    elif preset == "수익형":
        rows = [
            ["연승", f"{axis}", 7000, 1.5, "기본 방어"],
            ["복연승", f"{axis}-{mate}", 6000, 2.0, "본전 방어"],
            ["복승", f"{axis}-{mate}", 7000, 5.0, "본 수익"],
            ["삼복승", f"{axis}-{mate}-{sub}", 6000, 12.0, "중배당"],
            ["쌍승", f"{axis}→{mate}", 2000, 9.0, "순서 도전"],
            ["삼쌍승", f"{axis}→{mate}→{sub}", 2000, 45.0, "고배당 도전"],
        ]
    else:
        rows = [
            ["연승", f"{axis}", 10000, 1.5, "축마가 3착 안에 들어오면 방어"],
            ["복연승", f"{axis}-{mate}", 8000, 2.0, "축마+상대마가 둘 다 3착 안"],
            ["복연승", f"{axis}-{sub}", 5000, 2.8, "상대마가 바뀌어도 방어"],
            ["복승", f"{axis}-{mate}", 4000, 5.0, "두 마리가 1·2착이면 수익"],
            ["삼복승", f"{axis}-{mate}-{sub}", 2000, 12.0, "세 마리가 모두 3착 안"],
            ["삼쌍승", f"{axis}→{mate}→{sub}", 1000, 45.0, "순서까지 맞으면 고배당"],
        ]
    df = pd.DataFrame(rows, columns=["승식", "조합", "구매금액", "예상배당", "목적"])
    base_sum = int(df["구매금액"].sum())
    if base_sum > 0 and budget != base_sum:
        ratio = budget / base_sum
        df["구매금액"] = (df["구매금액"] * ratio / 1000).round().astype(int) * 1000
        # adjust rounding drift
        diff = int(budget - df["구매금액"].sum())
        if len(df) and diff != 0:
            df.loc[0, "구매금액"] = max(1000, int(df.loc[0, "구매금액"] + diff))
    df["예상환급"] = (df["구매금액"] * df["예상배당"]).round().astype(int)
    return df


def calc_case_rows(plan: pd.DataFrame) -> pd.DataFrame:
    def total_for(types: List[str], combo_contains: Optional[str] = None) -> int:
        d = plan[plan["승식"].isin(types)].copy()
        if combo_contains:
            d = d[d["조합"].astype(str).str.contains(combo_contains, regex=False)]
        return int(d["예상환급"].sum()) if not d.empty else 0

    total_bet = int(plan["구매금액"].sum()) if not plan.empty else 0
    cases = []
    # generic cases matching default logic
    t1 = total_for(["연승"])
    cases.append(["축마만 3착 안", "연승", t1, t1 - total_bet])
    t2 = total_for(["연승", "복연승"])
    cases.append(["축마+상대/보조마 3착 안", "연승 + 복연승", t2, t2 - total_bet])
    t3 = total_for(["연승", "복연승", "복승"])
    cases.append(["축마+상대마 1·2착", "연승 + 복연승 + 복승", t3, t3 - total_bet])
    t4 = total_for(["연승", "복연승", "복승", "삼복승"])
    cases.append(["세 마리 1~3착 안", "연승 + 복연승 + 복승 + 삼복승", t4, t4 - total_bet])
    t5 = int(plan["예상환급"].sum()) if not plan.empty else 0
    cases.append(["순서까지 삼쌍 적중", "전체 대부분 적중", t5, t5 - total_bet])
    return pd.DataFrame(cases, columns=["결과 상황", "적중 승식", "환급금", "순손익"])


def render_stable_bet_module(result: Dict[str, Any], meet: str) -> None:
    st.markdown("### 💰 18,000원 삼쌍승 18장 / 예상 환급 계산")
    st.markdown(
        '<div class="betting-card"><div class="betting-title">핵심 원칙</div>'
        '한 방 몰빵보다 <b>연승·복연승으로 방어</b>하고, <b>복승·삼복승으로 수익</b>, '
        '<b>삼쌍승은 소액 도전</b>으로만 사용합니다. 수익 보장이 아니라 손실을 줄이고 오래 버티는 구조입니다.</div>',
        unsafe_allow_html=True,
    )
    with st.expander("📘 마권 승식 해석", expanded=False):
        st.dataframe(BET_TYPE_INFO, width="stretch", hide_index=True)
        st.caption("복=조합, 쌍=순서, 삼=3마리/3착까지 보는 방식으로 기억하면 쉽습니다.")

    c1, c2, c3, c4, c5 = st.columns(5)
    default_axis = safe_int(result.get("축마", 7), 7)
    default_mate = safe_int(result.get("상대마", 3), 3)
    default_sub = safe_int(result.get("보조마", 10), 10)
    default_hole = safe_int(result.get("구멍마", 5), 5)
    with c1:
        axis = st.number_input("축마", min_value=1, max_value=20, value=default_axis, step=1)
    with c2:
        mate = st.number_input("상대마", min_value=1, max_value=20, value=default_mate, step=1)
    with c3:
        sub = st.number_input("보조마", min_value=1, max_value=20, value=default_sub, step=1)
    with c4:
        hole = st.number_input("구멍마", min_value=1, max_value=20, value=default_hole, step=1)

    tmp_result = {**result, "축마": axis, "상대마": mate, "보조마": sub, "구멍마": hole}
    b1, b2 = st.columns([1, 1])
    with b1:
        budget = st.number_input("총 구매 기준", min_value=1000, max_value=100000, value=18000, step=1000)
    with b2:
        preset = st.selectbox("구매 전략", ["안정형", "보수형", "수익형"], index=0)

    plan = stable_plan_from_result(tmp_result, int(budget), preset)
    st.markdown("#### ✅ 기본 추천 조합")
    edited = st.data_editor(
        plan,
        width="stretch",
        hide_index=True,
        column_config={
            "구매금액": st.column_config.NumberColumn("구매금액", min_value=0, step=1000, format="%d원"),
            "예상배당": st.column_config.NumberColumn("예상배당", min_value=1.0, step=0.1, format="%.1f배"),
            "예상환급": st.column_config.NumberColumn("예상환급", format="%d원", disabled=True),
        },
        disabled=["승식", "조합", "목적", "예상환급"],
        key="stable_bet_editor",
    )
    edited["구매금액"] = pd.to_numeric(edited["구매금액"], errors="coerce").fillna(0).astype(int)
    edited["예상배당"] = pd.to_numeric(edited["예상배당"], errors="coerce").fillna(1.0)
    edited["예상환급"] = (edited["구매금액"] * edited["예상배당"]).round().astype(int)

    total_bet = int(edited["구매금액"].sum())
    max_return = int(edited["예상환급"].sum())
    max_profit = max_return - total_bet
    m1, m2, m3 = st.columns(3)
    m1.metric("총 구매금액", f"{total_bet:,}원")
    m2.metric("최대 예상환급", f"{max_return:,}원")
    m3.metric("최대 예상손익", f"{max_profit:,}원")

    st.markdown("#### 📊 결과별 예상")
    case_df = calc_case_rows(edited)
    st.dataframe(case_df, width="stretch", hide_index=True)

    st.markdown("#### 한눈에 보기")
    if not case_df.empty:
        p = {r["결과 상황"]: r for _, r in case_df.iterrows()}
        st.markdown(
            f"""
<div class="manual-box">
<div class="manual-title">18,000원 삼쌍승 18장 예상</div>
<div class="manual-note">최소 방어: <b>{safe_int(p.get('축마만 3착 안', {}).get('환급금', 0)):,}원</b></div>
<div class="manual-note">본전권: <b>{safe_int(p.get('축마+상대/보조마 3착 안', {}).get('환급금', 0)):,}원</b></div>
<div class="manual-note">수익권: <b>{safe_int(p.get('축마+상대마 1·2착', {}).get('환급금', 0)):,}원</b></div>
<div class="manual-note">중배당권: <b>{safe_int(p.get('세 마리 1~3착 안', {}).get('환급금', 0)):,}원</b></div>
<div class="manual-note">고배당권: <b>{safe_int(p.get('순서까지 삼쌍 적중', {}).get('환급금', 0)):,}원</b></div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.info("배당 계산 공식: 환급금 = 구매금액 × 배당률. 환급금은 원금 포함 금액으로 보고, 순손익은 환급금 - 총 구매금액입니다.")
    st.warning("실제 배당은 경주 직전까지 변동됩니다. 이 계산은 현재 배당 기준 예상치이며, 수익을 보장하지 않습니다.")
    st.link_button("↗ 더비온/KRA 공식 구매표 열기", kra_buy_url(meet), width="stretch")
    st.caption("※ 자동구매/자동결제 아님 · 공식 구매표 이동만 제공 · 사용자가 직접 입력/확정")


# -----------------------------------------------------------------------------
# Smart API collection / shared hub system
# -----------------------------------------------------------------------------
DAILY_PRELOAD_KEYS = [
    "race_url", "entry_url", "horse_url", "gear_url", "rating_url",
    "race_record_url", "start_exam_url", "judge_url",
    "race_overview_url", "entry_registered_url", "jockey_result_url", "horse_shoe_url",
]
RACE_TIME_KEYS = [
    "body_url", "jockey_change_url", "corner_pace_url", "weather_alert_url",
    "race_cancel_url",
]
LIVE_ONLY_KEYS = [
    "odds_url", "today_odds_url", "popularity_url",
    "first_odds_url", "second_odds_url", "third_odds_url",
    "dividend_integrated_url", "race_detail_result_url",
]
SMART_CORE_KEYS = list(dict.fromkeys(DAILY_PRELOAD_KEYS + RACE_TIME_KEYS + LIVE_ONLY_KEYS))

API_SMART_INTERVAL_MIN = {
    # 하루 아침에 한 번 받아도 되는 기본/과거/말 정보
    "race_url": 720,
    "entry_url": 720,
    "horse_url": 720,
    "gear_url": 720,
    "rating_url": 720,
    "race_record_url": 720,
    "start_exam_url": 720,
    "judge_url": 720,
    # 경주 전이나 변경 가능성이 있는 정보
    "body_url": 60,
    "jockey_change_url": 30,
    "corner_pace_url": 30,
    "weather_alert_url": 30,
    # 직전까지 바뀌는 실시간성 정보
    "odds_url": 5,
    "today_odds_url": 5,
    "popularity_url": 5,
    "first_odds_url": 5,
    "second_odds_url": 5,
    "third_odds_url": 5,
    "race_overview_url": 720,
    "entry_registered_url": 720,
    "jockey_result_url": 720,
    "horse_shoe_url": 720,
    "race_cancel_url": 10,
    "dividend_integrated_url": 5,
    "race_detail_result_url": 10,
}

API_SMART_GROUP = {
    **{k: "아침 1회" for k in DAILY_PRELOAD_KEYS},
    **{k: "경주 전 점검" for k in RACE_TIME_KEYS},
    **{k: "직전 실시간" for k in LIVE_ONLY_KEYS},
}


def smart_cache_path(key: str, rc_date: str, meet: str, race_no: int) -> Path:
    safe = re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", f"{rc_date}_{meet}_{race_no}_{key}")
    return SMART_API_CACHE_DIR / f"{safe}.json"


def save_smart_api_cache(key: str, rc_date: str, meet: str, race_no: int, df: pd.DataFrame, msg: str = "") -> None:
    if df is None or df.empty:
        return
    payload = {
        "saved_at": now_str(),
        "key": key,
        "rc_date": rc_date,
        "meet": meet,
        "race_no": int(race_no),
        "msg": msg,
        "rows": df.head(500).astype(str).to_dict("records"),
    }
    save_json_file(smart_cache_path(key, rc_date, meet, race_no), payload)


def load_smart_api_cache(key: str, rc_date: str, meet: str, race_no: int) -> Tuple[pd.DataFrame, Optional[datetime], str]:
    payload = load_json_file(smart_cache_path(key, rc_date, meet, race_no), {})
    if not payload or not payload.get("rows"):
        return pd.DataFrame(), None, ""
    try:
        df = pd.DataFrame(payload.get("rows", []))
        saved_at_raw = str(payload.get("saved_at", ""))
        saved_at = datetime.strptime(saved_at_raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=KST)
        return df, saved_at, str(payload.get("msg", ""))
    except Exception:
        return pd.DataFrame(), None, ""


def cache_age_min(saved_at: Optional[datetime]) -> int:
    if not saved_at:
        return 999999
    return max(0, int((now_kst() - saved_at).total_seconds() // 60))




def parse_today_race_datetime(time_text: str) -> Optional[datetime]:
    """사이드바/허브에서 받은 HH:MM 경주 예정시각을 오늘 KST datetime으로 변환합니다."""
    try:
        t = str(time_text or '').strip()
        if not t:
            return None
        m = re.search(r"(\d{1,2})[:시](\d{1,2})", t)
        if not m:
            m = re.search(r"^(\d{3,4})$", t)
            if not m:
                return None
            raw = m.group(1).zfill(4)
            hh, mm = int(raw[:2]), int(raw[2:])
        else:
            hh, mm = int(m.group(1)), int(m.group(2))
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            return None
        n = now_kst()
        return n.replace(hour=hh, minute=mm, second=0, microsecond=0)
    except Exception:
        return None


def minutes_until_race(time_text: str) -> Optional[int]:
    dt = parse_today_race_datetime(time_text)
    if not dt:
        return None
    return int((dt - now_kst()).total_seconds() // 60)


# -----------------------------------------------------------------------------
# Race-time / current-race synchronization helpers
# -----------------------------------------------------------------------------
def _clean_time_text(v: Any) -> str:
    """KRA/API 시간값을 HH:MM 형태로 정리합니다."""
    try:
        txt = str(v or "").strip()
        if not txt or txt.lower() in ["nan", "none", "-"]:
            return ""
        m = re.search(r"(\d{1,2})[:시](\d{1,2})", txt)
        if m:
            hh, mm = int(m.group(1)), int(m.group(2))
            if 0 <= hh <= 23 and 0 <= mm <= 59:
                return f"{hh:02d}:{mm:02d}"
        nums = re.findall(r"\d+", txt)
        if nums:
            raw = nums[0]
            if len(raw) in [3, 4]:
                raw = raw.zfill(4)
                hh, mm = int(raw[:2]), int(raw[2:])
                if 0 <= hh <= 23 and 0 <= mm <= 59:
                    return f"{hh:02d}:{mm:02d}"
    except Exception:
        pass
    return ""


def _norm_meet_name(v: Any) -> str:
    txt = str(v or "").strip()
    if txt in ["1", "서울", "SEOUL", "Seoul"] or "서울" in txt:
        return "서울"
    if txt in ["2", "부산", "부산경남", "부경", "BUSAN", "Busan"] or "부산" in txt or "부경" in txt:
        return "부산경남"
    if txt in ["3", "제주", "JEJU", "Jeju"] or "제주" in txt:
        return "제주"
    return txt


def _candidate_cols(cols: List[str], names: List[str]) -> List[str]:
    out: List[str] = []
    low_map = {str(c).lower().replace("_", "").replace(" ", ""): c for c in cols}
    for name in names:
        key = str(name).lower().replace("_", "").replace(" ", "")
        for lk, orig in low_map.items():
            if key == lk or key in lk or lk in key:
                if orig not in out:
                    out.append(orig)
    return out


def _load_schedule_like_frames() -> List[pd.DataFrame]:
    """허브 CSV, live cache, smart API cache에서 시간표/경주개요 형태의 프레임을 모읍니다."""
    frames: List[pd.DataFrame] = []
    for path in [DATA_DIR / "race_schedule.csv", SCHEDULE_HUB_FILE, DATA_DIR / "maru_kra_schedule_hub.csv"]:
        try:
            if path.exists():
                df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
                if not df.empty:
                    frames.append(df)
        except Exception:
            try:
                df = pd.read_csv(path, dtype=str)
                if not df.empty:
                    frames.append(df)
            except Exception:
                pass
    try:
        cache = load_live_cache()
        if isinstance(cache, dict):
            for key in ["race_overview_url", "race_url", "entry_registered_url", "entry_url"]:
                df = cache.get(key)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    frames.append(df)
    except Exception:
        pass
    try:
        live_data = st.session_state.get("live_data", {})
        if isinstance(live_data, dict):
            for key in ["race_overview_url", "race_url", "entry_registered_url", "entry_url"]:
                df = live_data.get(key)
                if isinstance(df, pd.DataFrame) and not df.empty:
                    frames.insert(0, df)
    except Exception:
        pass
    # smart api cache도 보조로 검색
    try:
        if SMART_API_CACHE_DIR.exists():
            for fp in SMART_API_CACHE_DIR.glob("*.json"):
                if not any(k in fp.name for k in ["race_overview_url", "race_url", "entry_registered_url", "entry_url"]):
                    continue
                payload = load_json_file(fp, {})
                rows = payload.get("rows", []) if isinstance(payload, dict) else []
                if rows:
                    frames.append(pd.DataFrame(rows))
    except Exception:
        pass
    return frames


def _lookup_race_time_in_df(df: pd.DataFrame, meet: Any, race_no: Any, rc_date: str = "") -> str:
    try:
        if df is None or df.empty:
            return ""
        d = df.copy()
        d.columns = d.columns.astype(str).str.strip()
        cols = list(d.columns)
        meet_cols = _candidate_cols(cols, ["경마장", "racecourse", "meet", "시행경마장", "rcCourse", "meetCd"])
        race_cols = _candidate_cols(cols, ["경주번호", "race_no", "raceno", "rcno", "경주", "race", "rcNo"])
        time_cols = _candidate_cols(cols, ["출발시간", "출발시각", "경주시간", "race_time", "start", "time", "시각", "rcTime"])
        date_cols = _candidate_cols(cols, ["날짜", "경주일자", "rc_date", "date", "일자", "rcDate"])
        if not race_cols or not time_cols:
            return ""
        target_meet = _norm_meet_name(meet)
        target_race = str(_safe_race_no(race_no))
        sub = d
        if rc_date and date_cols:
            dc = date_cols[0]
            ds = sub[dc].astype(str).str.replace("-", "", regex=False).str[:8]
            same = sub[ds == str(rc_date).replace("-", "")[:8]]
            if not same.empty:
                sub = same
        if target_meet and meet_cols:
            mc = meet_cols[0]
            same = sub[sub[mc].map(_norm_meet_name).astype(str) == target_meet]
            if not same.empty:
                sub = same
        rc = race_cols[0]
        sub = sub[sub[rc].map(_safe_race_no).astype(str) == target_race]
        if sub.empty:
            return ""
        for tc in time_cols:
            for val in sub[tc].tolist():
                t = _clean_time_text(val)
                if t:
                    return t
    except Exception:
        return ""
    return ""


def lookup_actual_race_time(meet: Any, race_no: Any, rc_date: str = "") -> str:
    rc_date = str(rc_date or today_kst()).replace("-", "")[:8]
    for df in _load_schedule_like_frames():
        t = _lookup_race_time_in_df(df, meet, race_no, rc_date)
        if t:
            return t
    return ""


def current_live_race_from_schedule(meet: Any = "서울", rc_date: str = "", window_before: int = 20, grace_after: int = 5) -> Dict[str, Any]:
    """KRA 시간표 기준 현재 구매 대상 경주를 찾습니다.
    - 출발 window_before분 전부터 출발 grace_after분 후까지 현재 경주로 간주
    - 없으면 다음 예정 경주를 반환
    """
    rc_date = str(rc_date or today_kst()).replace("-", "")[:8]
    target_meet = _norm_meet_name(meet)
    now = now_kst()
    candidates: List[Dict[str, Any]] = []
    for df in _load_schedule_like_frames():
        try:
            d = df.copy()
            d.columns = d.columns.astype(str).str.strip()
            cols = list(d.columns)
            meet_cols = _candidate_cols(cols, ["경마장", "racecourse", "meet", "시행경마장", "meetCd"])
            race_cols = _candidate_cols(cols, ["경주번호", "race_no", "raceno", "rcno", "경주", "race", "rcNo"])
            time_cols = _candidate_cols(cols, ["출발시간", "출발시각", "경주시간", "race_time", "start", "time", "시각", "rcTime"])
            date_cols = _candidate_cols(cols, ["날짜", "경주일자", "date", "일자", "rcDate"])
            if not race_cols or not time_cols:
                continue
            for _, r in d.iterrows():
                if meet_cols and target_meet:
                    if _norm_meet_name(r.get(meet_cols[0], "")) != target_meet:
                        continue
                if date_cols:
                    ds = str(r.get(date_cols[0], "")).replace("-", "")[:8]
                    if ds and ds.lower() not in ["nan", "none"] and ds != rc_date:
                        continue
                t = ""
                for tc in time_cols:
                    t = _clean_time_text(r.get(tc, ""))
                    if t:
                        break
                if not t:
                    continue
                dt = parse_today_race_datetime(t)
                if not dt:
                    continue
                diff = int((dt - now).total_seconds() // 60)
                candidates.append({
                    "경마장": target_meet or _norm_meet_name(r.get(meet_cols[0], "")) if meet_cols else str(meet),
                    "경주번호": _safe_race_no(r.get(race_cols[0], 1)),
                    "경주시간": t,
                    "분전": diff,
                    "dt": dt,
                })
        except Exception:
            continue
    if not candidates:
        return {}
    # 1순위: 구매 가능 시간대
    active = [c for c in candidates if -grace_after <= c["분전"] <= window_before]
    if active:
        active.sort(key=lambda x: abs(x["분전"]))
        out = active[0]
    else:
        future = [c for c in candidates if c["분전"] > window_before]
        if future:
            future.sort(key=lambda x: x["분전"])
            out = future[0]
        else:
            candidates.sort(key=lambda x: x["dt"], reverse=True)
            out = candidates[0]
    out = dict(out)
    out.pop("dt", None)
    return out

def current_live_race_any(rc_date: str = "", window_before: int = 20, grace_after: int = 5) -> Dict[str, Any]:
    """서울/부산경남/제주 전체에서 현재 구매 가능 또는 가장 가까운 다음 경주를 찾습니다."""
    rc_date = str(rc_date or today_kst()).replace("-", "")[:8]
    found: List[Dict[str, Any]] = []
    for m in ["서울", "부산경남", "제주"]:
        cur = current_live_race_from_schedule(m, rc_date, window_before=window_before, grace_after=grace_after)
        if cur:
            found.append(dict(cur))
    if not found:
        return {}
    active = [x for x in found if -grace_after <= int(x.get("분전", 999999)) <= window_before]
    if active:
        active.sort(key=lambda x: abs(int(x.get("분전", 999999))))
        return active[0]
    future = [x for x in found if int(x.get("분전", -999999)) > window_before]
    if future:
        future.sort(key=lambda x: int(x.get("분전", 999999)))
        return future[0]
    return {}


def sync_row_to_current_race(row: Dict[str, Any], force_if_stale: bool = True) -> Dict[str, Any]:
    """모바일/허브 추천을 실제 현재 경주와 동기화합니다.
    단, 경주가 바뀐 경우 예전 추천조합을 그대로 실전 추천으로 보여주지 않고 재분석 필요로 표시합니다.
    """
    row = dict(row or {})
    original_meet = row.get("경마장", "서울") or "서울"
    original_no = _safe_race_no(row.get("경주번호", 1))
    meet = original_meet
    rc_date = str(row.get("날짜", today_kst()) or today_kst()).replace("-", "")[:8]
    cur = current_live_race_any(rc_date) or current_live_race_from_schedule(meet, rc_date)

    rt = _race_time_text_from_row(row) if "_race_time_text_from_row" in globals() else str(row.get("경주시간", ""))
    if not rt:
        rt = lookup_actual_race_time(meet, row.get("경주번호", 1), rc_date)
        if rt:
            row["경주시간"] = rt
    if not cur:
        row.setdefault("추천검증상태", "경주시간표없음")
        row.setdefault("실전표시불가", "Y")
        return row

    cur_meet = cur.get("경마장", meet)
    cur_no = int(cur.get("경주번호", original_no))
    cur_time = cur.get("경주시간", rt)
    current_time = _clean_time_text(row.get("경주시간", ""))
    m = minutes_until_race(current_time) if current_time else None
    changed = (_norm_meet_name(original_meet) != _norm_meet_name(cur_meet)) or (original_no != cur_no)
    should_sync = False
    if force_if_stale and changed:
        if m is None or m < -5 or int(cur.get("분전", 999)) <= 20:
            should_sync = True
    if should_sync:
        row["원경마장"] = original_meet
        row["원경주번호"] = original_no
        row["경마장"] = cur_meet
        row["경주번호"] = cur_no
        row["경주시간"] = cur_time
        row["출발시간"] = cur_time
        row["시간동기화"] = "Y"
        # 경주가 달라진 예전 추천조합은 실전 구매 화면에 노출 금지
        row["추천검증상태"] = "현재경주재분석필요"
        row["실전표시불가"] = "Y"
    else:
        row.setdefault("추천검증상태", "검증완료")
        row.setdefault("실전표시불가", "N")
    return row


def live_window_state(time_text: str) -> str:
    """경주 예정시각 기준 스마트 호출 상태를 반환합니다."""
    m = minutes_until_race(time_text)
    if m is None:
        return "시간미입력"
    if 0 <= m <= 20:
        return "20분전_실시간"
    if 20 < m <= 60:
        return "60분전_점검"
    if m < 0:
        return "결과확인"
    return "대기"

def smart_selected_apis(mode: str, manual_selected: List[str]) -> List[str]:
    """26개를 매번 전부 치지 않고 상황별 필요한 API만 고릅니다.
    단, API 패널에서 '전체 ON'을 눌렀으면 스마트 자동보다 우선하여 26/26개를 호출합니다.
    """
    if bool(st.session_state.get("api_master_on", True)) and bool(st.session_state.get("force_all_apis", False)):
        return [k for k, _ in API_LABELS]
    if mode == "허브만 분석":
        return []
    if mode == "아침 사전수집":
        return DAILY_PRELOAD_KEYS + RACE_TIME_KEYS
    if mode == "경주 전 1회수집":
        return SMART_CORE_KEYS
    if mode == "실시간 집중":
        return RACE_TIME_KEYS + LIVE_ONLY_KEYS
    if mode == "전체 26개":
        return [k for k, _ in API_LABELS]
    if mode == "수동 ON/OFF":
        return manual_selected
    # 스마트 자동: 19개를 매시간 전부 호출하지 않습니다.
    # - 아침: 경주표/출전마/말정보 등 기본자료 1회 저장
    # - 경주 60~20분 전: 체중/기수변경/주로/기상 등 점검자료
    # - 경주 20분 전부터: 배당/인기/예측계열만 5분 주기로 집중 갱신
    h = now_kst().hour
    if h < 9:
        return DAILY_PRELOAD_KEYS + RACE_TIME_KEYS
    race_time_text = st.session_state.get("race_time_text", "")
    state = live_window_state(race_time_text)
    st.session_state["smart_window_state"] = state
    if state == "20분전_실시간":
        return SMART_CORE_KEYS
    if state == "60분전_점검":
        return DAILY_PRELOAD_KEYS + RACE_TIME_KEYS
    if state == "결과확인":
        return DAILY_PRELOAD_KEYS + ["result_detail_url", "today_odds_url"]
    # 경주시간을 모르면 기본/캐시 중심으로만 분석하고, 실시간 API 남발을 막습니다.
    return DAILY_PRELOAD_KEYS


def smart_default_refresh_seconds(mode: str) -> int:
    if mode in ["허브만 분석", "아침 사전수집"]:
        return 0
    if mode == "경주 전 1회수집":
        return 300
    if mode == "실시간 집중":
        return 60
    if mode == "전체 26개":
        return 300
    return 0


def fetch_all_live(rc_date: str, meet: str, race_no: int, selected: List[str]) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    """스마트 수집판: API별 캐시 주기를 적용해 매번 26개 전체 호출을 피합니다."""
    master_on = bool(st.session_state.get("api_master_on", True))
    collection_mode = st.session_state.get("collection_mode", "스마트 자동")
    switches = get_api_switches()
    data: Dict[str, pd.DataFrame] = {}
    status_rows: List[Dict[str, Any]] = []

    if not master_on or collection_mode == "허브만 분석":
        cache = load_live_cache()
        return cache, pd.DataFrame([{
            "API": "허브/캐시", "key": "hub_cache", "분류": "허브 우선",
            "행수": sum(len(v) for v in cache.values()),
            "상태": "API 호출 없이 최근 허브/캐시로 분석", "URL": ""
        }])

    selected_set = set(selected)
    for key, label in API_LABELS:
        group = API_SMART_GROUP.get(key, "기타")
        interval = int(API_SMART_INTERVAL_MIN.get(key, 60))
        if key not in selected_set:
            status_rows.append({"API": label, "key": key, "분류": group, "행수": 0, "상태": "이번 모드에서 제외", "URL": ""})
            continue
        if not switches.get(key, True) and collection_mode == "수동 ON/OFF":
            status_rows.append({"API": label, "key": key, "분류": group, "행수": 0, "상태": "OFF: 건너뜀", "URL": ""})
            continue

        cached_df, saved_at, cache_msg = load_smart_api_cache(key, rc_date, meet, int(race_no))
        age = cache_age_min(saved_at)
        # 전체 26개 모드가 아니면, 주기 안의 데이터는 재호출하지 않고 캐시 사용
        if collection_mode != "전체 26개" and not cached_df.empty and age < interval:
            data[key] = cached_df
            status_rows.append({
                "API": label, "key": key, "분류": group, "행수": int(len(cached_df)),
                "상태": f"캐시 사용: {age}분 전 저장 / 재호출 기준 {interval}분", "URL": ""
            })
            continue

        df, msg, used_url = fetch_one_api(key, rc_date, meet, int(race_no))
        if not df.empty:
            data[key] = df
            save_smart_api_cache(key, rc_date, meet, int(race_no), df, msg)
            status_rows.append({
                "API": label, "key": key, "분류": group, "행수": int(len(df)),
                "상태": f"API 호출: {msg} / 캐시 저장", "URL": mask_key(used_url)
            })
        elif not cached_df.empty:
            data[key] = cached_df
            status_rows.append({
                "API": label, "key": key, "분류": group, "행수": int(len(cached_df)),
                "상태": f"API 실패 → 기존 캐시 사용: {age}분 전 / {msg}", "URL": mask_key(used_url)
            })
        else:
            status_rows.append({
                "API": label, "key": key, "분류": group, "행수": 0,
                "상태": f"API 실패/0건: {msg}", "URL": mask_key(used_url)
            })
        time.sleep(0.03)

    status = pd.DataFrame(status_rows)
    if data:
        save_live_cache(data, status)
    else:
        cache = load_live_cache()
        if cache:
            data = cache
            status_rows.append({"API": "전체 캐시", "key": "cache", "분류": "백업", "행수": sum(len(v) for v in cache.values()), "상태": "이번 호출 0건 → 최근 전체 캐시 사용", "URL": ""})
            status = pd.DataFrame(status_rows)
    try:
        status.to_csv(API_STATUS_FILE, index=False, encoding="utf-8-sig")
    except Exception:
        pass
    return data, status


def save_mobile_recommend_json(row: Dict[str, Any]) -> bool:
    """모바일 속도 개선: 큰 CSV 대신 최근 추천 1건을 작은 JSON으로 별도 저장.
    HOTFIX: 저장 성공/실패를 bool로 반환하고, 실전검증/표시차단 필드까지 함께 저장합니다.
    """
    try:
        row = sync_row_to_current_race(dict(row or {}), force_if_stale=True)

        live_rows = 0
        try:
            live_rows = int(float(str(row.get("실시간행수", 0) or 0).replace(",", "")))
        except Exception:
            live_rows = 0

        if live_rows > 0 and str(row.get("데이터상태", "")).strip() in ["", "샘플", "대기"]:
            row["데이터상태"] = "실시간"
        if live_rows > 0 and str(row.get("실전검증", "")).strip().upper() in ["", "N", "FALSE", "0"]:
            row["실전검증"] = "Y"
        if live_rows > 0 and str(row.get("실전표시불가", "")).strip().upper() in ["", "Y", "TRUE", "1"]:
            row["실전표시불가"] = "N"

        compact_keys = [
            "저장시각", "날짜", "경마장", "경주번호", "경주시간", "출발시간", "추천금액", "신뢰도", "위험도", "예상배당",
            "축마", "상대마", "보조마", "구멍마", "공격삼쌍승", "방어삼복승", "삼쌍승3묶음", "삼쌍승18조합",
            "추천창1", "추천창2", "추천창3", "추천유형1", "추천유형2", "추천유형3",
            "18마권", "마권수", "단위금액", "총추천금액", "안정형6", "고배당형6", "변수대응형6", "안정형대표", "고배당형대표", "변수대응형대표", "구매표복사",
            "안정점수", "변수점수", "고배당점수", "결과마번", "적중여부", "배당률", "환급금", "총환급", "손익", "순손익", "근거",
            "데이터상태", "실전검증", "실전표시불가", "실시간행수", "분석모드", "모바일생성", "API호출대상", "API상태행수"
        ]
        small = {k: row.get(k, "") for k in compact_keys}
        small.setdefault("추천금액", 18000)
        small.setdefault("결과마번", "결과대기")
        small.setdefault("데이터상태", "실시간" if live_rows > 0 else "대기")
        small.setdefault("실전검증", "Y" if live_rows > 0 else "N")
        small.setdefault("실전표시불가", "N" if live_rows > 0 else "Y")
        small["저장성공"] = "Y"
        small["저장파일"] = str(MOBILE_RECOMMEND_FILE)
        mobile_text = json.dumps(small, ensure_ascii=False, indent=2)
        MOBILE_RECOMMEND_FILE.write_text(mobile_text, encoding="utf-8")
        try_push_hub_file_to_github("maru_kra_data/mobile_recommend.json", mobile_text, "Update mobile recommendation")
        return True
    except Exception as e:
        try:
            st.warning(f"mobile_recommend.json 저장 실패: {e}")
        except Exception:
            pass
        return False

def load_mobile_recommend_json() -> Dict[str, Any]:
    try:
        if MOBILE_RECOMMEND_FILE.exists():
            data = json.loads(MOBILE_RECOMMEND_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}

def save_shared_recommendation(row: Dict[str, Any]) -> bool:
    """모바일/PC가 같은 Streamlit 앱을 볼 때 같은 허브 파일에서 추천을 가져오게 저장합니다.
    HOTFIX: CSV 1개가 실패해도 mobile_recommend.json이 저장되면 성공으로 처리합니다.
    """
    row = dict(row or {})
    row.setdefault("저장시각", now_str())
    ok1 = append_csv(SHARED_RECOMMEND_FILE, row)
    ok2 = save_hub_row(row)
    ok3 = save_mobile_recommend_json(row)

    try:
        save_json_file(HUB_STATUS_FILE, {
            "저장시각": now_str(),
            "shared_csv": bool(ok1),
            "local_hub_bigdata": bool(ok2),
            "mobile_json": bool(ok3),
            "최종성공": bool(ok1 or ok2 or ok3),
            "경마장": row.get("경마장", ""),
            "경주번호": row.get("경주번호", ""),
            "실시간행수": row.get("실시간행수", 0),
        })
    except Exception:
        pass
    return bool(ok1 or ok2 or ok3)


def run_mobile_hub_analysis(meet: str, race_no: int, race_time: str = "", sim_count: int = 1200, risk_mode: str = "균형형") -> Tuple[bool, Dict[str, Any], str]:
    """PC가 꺼져 있어도 모바일에서 직접 분석→허브저장→추천 활성화를 수행합니다."""
    try:
        rc_date = today_kst()
        meet = str(meet or "서울")
        race_no = int(race_no or 1)
        # 모바일 기본값 1R에 머무르지 않게 시간표 기준 현재/다음 구매 대상 경주로 보정
        cur_race = current_live_race_any(rc_date) or current_live_race_from_schedule(meet, rc_date)
        if cur_race and (not str(race_time or "").strip() or int(race_no) == 1):
            meet = str(cur_race.get("경마장", meet))
            race_no = int(cur_race.get("경주번호", race_no))
            race_time = str(cur_race.get("경주시간", race_time))
        if race_time:
            st.session_state["race_time_text"] = str(race_time).strip()
        switches = get_api_switches()
        manual_selected = [k for k, _ in API_LABELS if switches.get(k, False)]
        selected = smart_selected_apis("스마트 자동", manual_selected)
        data, status = fetch_all_live(rc_date, meet, int(race_no), selected)
        env = fetch_weather(meet)
        base = build_base_horses(data, rc_date, meet, int(race_no))
        horses = merge_score_features(base, data, rc_date, meet, int(race_no))
        score_df, result, combos = score_and_recommend(horses, env, int(sim_count), risk_mode)
        live_rows = sum(len(v) for v in data.values()) if data else 0
        row = {
            "저장시각": now_str(), "날짜": rc_date, "경마장": meet, "경주번호": int(race_no),
            "경주시간": str(race_time or st.session_state.get("race_time_text", "")),
            "축마": result.get("축마"), "상대마": result.get("상대마"), "보조마": result.get("보조마"), "구멍마": result.get("구멍마"),
            "공격삼쌍승": result.get("공격삼쌍승"), "방어삼복승": result.get("방어삼복승"),
            "삼쌍승3묶음": result.get("삼쌍승3묶음"), "삼쌍승18조합": result.get("삼쌍승18조합"),
            "예상배당": result.get("예상배당"), "신뢰도": result.get("신뢰도"), "위험도": result.get("위험도", "중간"),
            "추천금액": result.get("추천금액", 18000), "근거": result.get("근거"), "실시간행수": live_rows,
            "모바일생성": "Y", "분석모드": "모바일 허브분석 실행",
            "API호출대상": len(selected), "API상태행수": 0 if status is None else len(status),
        }
        ok = save_shared_recommendation(row)
        return bool(ok), row, f"모바일 허브분석 저장 완료 · API/캐시 {live_rows:,}행 반영"
    except Exception as e:
        return False, {}, f"모바일 허브분석 실패: {e}"


def load_shared_recommendations(limit: int = 50) -> pd.DataFrame:
    frames = []
    for p in [SHARED_RECOMMEND_FILE, LOCAL_HUB_FILE, BIGDATA_FILE]:
        df = load_csv_safe(p)
        if not df.empty:
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    if "저장시각" in out.columns:
        out = out.drop_duplicates(subset=[c for c in ["저장시각", "날짜", "경마장", "경주번호", "공격삼쌍승"] if c in out.columns], keep="last")
        out = out.sort_values("저장시각", ascending=False)
    return out.head(limit)


# -----------------------------------------------------------------------------
# Mobile/PC separated view
# -----------------------------------------------------------------------------
MOBILE_READY_WINDOW_MIN = 20

def _query_mode() -> str:
    """URL/컨텍스트에서 모바일 모드 값을 최대한 넓게 읽습니다.
    - ?mode=mobile, ?view=mobile, ?mobile=1, ?m=1 모두 허용
    - 일부 모바일/PWA 환경에서 st.query_params가 비어 보일 때 st.context.url도 재확인
    """
    values: List[str] = []
    # 1) Streamlit 최신 query_params
    try:
        qp = st.query_params
        for k in ["mode", "view", "mobile", "m"]:
            v = qp.get(k)
            if isinstance(v, list):
                values.extend([str(x) for x in v])
            elif v is not None:
                values.append(str(v))
    except Exception:
        pass
    # 2) Streamlit 구버전 query_params
    try:
        qp = st.experimental_get_query_params()
        for k in ["mode", "view", "mobile", "m"]:
            v = qp.get(k, [])
            if isinstance(v, list):
                values.extend([str(x) for x in v])
            elif v is not None:
                values.append(str(v))
    except Exception:
        pass
    # 3) st.context.url 직접 파싱
    try:
        ctx = getattr(st, "context", None)
        url = str(getattr(ctx, "url", "") or "")
        if "?" in url:
            q = dict(parse_qsl(urlparse(url).query, keep_blank_values=True))
            for k in ["mode", "view", "mobile", "m"]:
                if k in q:
                    values.append(str(q.get(k, "")))
    except Exception:
        pass
    joined = " ".join(values).lower().strip()
    if joined in ["mobile", "m", "phone", "1", "true", "yes"]:
        return "mobile"
    if "mobile" in joined or "phone" in joined:
        return "mobile"
    return joined

def _is_mobile_device() -> bool:
    """휴대폰 접속이면 URL 파라미터가 없어도 모바일 구매 화면으로 보냅니다."""
    try:
        ctx = getattr(st, "context", None)
        headers = getattr(ctx, "headers", {}) if ctx is not None else {}
        ua = ""
        if hasattr(headers, "get"):
            ua = str(headers.get("user-agent", "") or headers.get("User-Agent", ""))
        else:
            ua = str(headers)
        ua_l = ua.lower()
        mobile_tokens = ["android", "iphone", "ipad", "ipod", "mobile", "samsungbrowser", "wv", "kakaotalk"]
        return any(tok in ua_l for tok in mobile_tokens)
    except Exception:
        return False

def _force_pc_mode() -> bool:
    """휴대폰에서 PC 화면을 보고 싶을 때 ?mode=pc 또는 ?pc=1 사용."""
    try:
        qp = st.query_params
        raw = str(qp.get("mode") or qp.get("view") or qp.get("pc") or "").lower()
        return raw in ["pc", "desktop", "1", "true"] and ("pc" in raw or str(qp.get("pc", "")).lower() in ["1", "true"])
    except Exception:
        return False

def _should_show_mobile() -> bool:
    # ?mode=pc / ?pc=1 이면 모바일 자동감지를 끄고 PC 화면을 보여줍니다.
    try:
        qp = st.query_params
        if str(qp.get("mode") or qp.get("view") or "").lower().strip() in ["pc", "desktop"]:
            return False
        if str(qp.get("pc") or "").lower().strip() in ["1", "true", "yes"]:
            return False
    except Exception:
        pass
    return _query_mode() in ["mobile", "m", "phone"] or _is_mobile_device()

def _parse_kst_time(x: Any) -> Optional[datetime]:
    try:
        if pd.isna(x):
            return None
        s = str(x).strip()
        if not s:
            return None
        dt = pd.to_datetime(s, errors="coerce")
        if pd.isna(dt):
            return None
        if getattr(dt, "tzinfo", None) is None:
            return dt.to_pydatetime().replace(tzinfo=KST)
        return dt.to_pydatetime().astimezone(KST)
    except Exception:
        return None


def _norm_race_no(v: Any) -> str:
    txt = str(v or "").strip()
    if not txt:
        return "-"
    nums = re.findall(r"\d+", txt)
    if nums:
        return str(int(nums[0]))
    return txt.replace("R", "").replace("r", "").strip() or "-"


def _safe_race_no(v: Any, default: int = 1) -> int:
    """모바일 버튼에서 경주번호가 '5R', '-', 빈값이어도 앱이 죽지 않게 정수로 보정."""
    try:
        nums = re.findall(r"\d+", str(v or ""))
        if nums:
            n = int(nums[0])
            return n if 1 <= n <= 20 else default
    except Exception:
        pass
    return default


def _race_time_text_from_row(row: Dict[str, Any]) -> str:
    for key in ["경주시간", "출발시간", "race_time_text"]:
        val = row.get(key, "")
        if str(val).strip():
            return str(val).strip()
    return ""


def _mobile_status_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    race_time_text = _race_time_text_from_row(row)
    saved_at = _parse_kst_time(row.get("저장시각", ""))
    race_dt = parse_today_race_datetime(race_time_text) if race_time_text else None
    now = now_kst()
    mins_to_race = None if race_dt is None else int((race_dt - now).total_seconds() // 60)
    result_text = str(row.get("결과마번", "") or "").strip()
    hit_text = str(row.get("적중여부", "") or "").strip()
    odds = row.get("배당률", row.get("예상배당", "-"))
    refund = row.get("환급금", row.get("총환급", 0))
    profit = row.get("손익", row.get("순손익", 0))
    if result_text and result_text not in ["결과대기", "nan", "None"]:
        status = "결과 확인"
        detail = f"실제결과 {result_text}"
    elif mins_to_race is None:
        status = "구매 가능"
        detail = "경주시간 미입력"
    elif mins_to_race > 20:
        status = "대기"
        detail = f"출발 {mins_to_race}분 전"
    elif 0 <= mins_to_race <= 20:
        status = "구매 가능"
        detail = f"출발 {mins_to_race}분 전"
    else:
        status = "결과대기"
        detail = f"출발 {-mins_to_race}분 경과"
    saved_at_txt = saved_at.strftime("%H:%M") if saved_at else "-"
    return {
        "race_time_text": race_time_text or "-",
        "saved_at_text": saved_at_txt,
        "mins_to_race": mins_to_race,
        "status": status,
        "detail": detail,
        "odds": odds,
        "refund": refund,
        "profit": profit,
        "result_text": result_text,
        "hit_text": hit_text,
    }

def mobile_ready_recommendations(limit: int = 20) -> pd.DataFrame:
    """모바일에는 실제 현재 경주와 검증된 추천만 보여줍니다.
    - mobile_recommend.json 우선
    - 저장시각/날짜/경마장/경주번호 누락 자동 보정
    - 현재 경주와 불일치한 예전 추천은 숨김 처리
    - 샘플 추천은 실전 화면에서 숨김 처리
    """
    js = load_mobile_recommend_json()
    if js:
        hub = pd.DataFrame([js])
    else:
        hub = load_shared_recommendations(300)
    if hub.empty:
        return pd.DataFrame()
    work = hub.copy()
    try:
        work = pd.DataFrame([sync_row_to_current_race(r, force_if_stale=True) for r in work.to_dict("records")])
    except Exception:
        pass
    try:
        work.columns = work.columns.astype(str).str.strip()
    except Exception:
        pass
    now = now_kst()
    if "저장시각" not in work.columns:
        for alt in ["recommended_at", "saved_at", "timestamp", "created_at", "time"]:
            if alt in work.columns:
                work["저장시각"] = work[alt]
                break
    if "저장시각" not in work.columns:
        work["저장시각"] = now_str()
    if "날짜" not in work.columns:
        for alt in ["date", "race_date", "rcDate"]:
            if alt in work.columns:
                work["날짜"] = work[alt]
                break
    if "날짜" not in work.columns:
        work["날짜"] = today_kst()
    if "경마장" not in work.columns:
        for alt in ["racecourse", "meet", "경마장명"]:
            if alt in work.columns:
                work["경마장"] = work[alt]
                break
    if "경주번호" not in work.columns:
        for alt in ["race_no", "raceNo", "경주"]:
            if alt in work.columns:
                work["경주번호"] = work[alt]
                break

    today = today_kst()
    if "날짜" in work.columns:
        today_mask = work["날짜"].astype(str).str.replace("-", "", regex=False).str[:8] == today
        blank_mask = work["날짜"].astype(str).str.strip().isin(["", "nan", "None"])
        work = work[today_mask | blank_mask].copy()
    if work.empty:
        return pd.DataFrame()

    # 현재 경주와 불일치해 재분석 필요로 표시된 row는 실전 화면에서 숨김
    if "실전표시불가" in work.columns:
        work = work[~work["실전표시불가"].astype(str).str.upper().isin(["Y", "TRUE", "1"])].copy()
    if "데이터상태" in work.columns:
        work = work[~work["데이터상태"].astype(str).str.contains("샘플", na=False)].copy()
    if "실전검증" in work.columns:
        work = work[~work["실전검증"].astype(str).str.upper().isin(["N", "FALSE", "0"])].copy()
    if work.empty:
        return pd.DataFrame()

    ages = []
    keep_rows = []
    sort_keys = []
    for _, r in work.iterrows():
        dt = _parse_kst_time(r.get("저장시각", "")) or now
        age = int((now - dt).total_seconds() // 60)
        ages.append(age)
        sort_keys.append(dt)
        race_time_text = _race_time_text_from_row(r.to_dict())
        race_dt = parse_today_race_datetime(race_time_text) if race_time_text else None
        result_text = str(r.get("결과마번", "") or "").strip()
        has_result = bool(result_text and result_text not in ["결과대기", "nan", "None"])
        if has_result:
            keep_rows.append(age <= 240)
        elif race_dt is not None and race_dt <= now:
            keep_rows.append(age <= 240)
        else:
            keep_rows.append(age <= MOBILE_READY_WINDOW_MIN)
    work["추천경과분"] = ages
    work["_정렬시각"] = sort_keys
    work["_keep"] = keep_rows
    work = work[work["_keep"]].drop(columns=["_keep"], errors="ignore")
    if work.empty:
        return pd.DataFrame()
    work = work.sort_values("_정렬시각", ascending=False).drop(columns=["_정렬시각"], errors="ignore")
    key_cols = [c for c in ["날짜", "경마장", "경주번호", "전략명"] if c in work.columns]
    if key_cols:
        work = work.drop_duplicates(subset=key_cols, keep="first")
    return work.head(limit)


def _horse_token(v: Any) -> str:
    """마번 표시용 토큰. 10번처럼 두 자리도 그대로 보존."""
    try:
        txt = str(v).replace("→", "-").replace(">", "-").strip()
        nums = re.findall(r"\d+", txt)
        if nums:
            return str(int(nums[0]))
    except Exception:
        pass
    return "-"


def _unique_horse_list(values: List[Any], max_no: int = 14) -> List[str]:
    out: List[str] = []
    for v in values:
        for n in re.findall(r"\d+", str(v).replace("→", "-").replace(">", "-")):
            try:
                nn = str(int(n))
                if 1 <= int(nn) <= 20 and nn not in out:
                    out.append(nn)
            except Exception:
                continue
    for n in range(1, max_no + 1):
        nn = str(n)
        if nn not in out:
            out.append(nn)
        if len(out) >= 9:
            break
    return out[:9]


def make_triple_groups_from_nums(nums: List[Any]) -> List[List[str]]:
    """AI 상위마를 3묶음으로 나눠 삼쌍승 후보 그룹 생성."""
    base = _unique_horse_list(nums, 14)
    return [base[0:3], base[3:6], base[6:9]]


def expand_triple_18(groups: List[List[str]]) -> List[str]:
    from itertools import permutations  # EXPAND_TRIPLE_HARD_FIX
    """3묶음 × 각 6순열 = 삼쌍승 18장."""
    import itertools
    tickets: List[str] = []
    for g in groups[:3]:
        clean = _unique_horse_list(g, 20)[:3]
        if len(clean) < 3:
            continue
        for p in itertools.permutations(clean, 3):
            tickets.append("-".join(map(str, p)))
    return tickets[:18]


def parse_groups_from_latest(latest: Dict[str, Any]) -> List[List[str]]:
    """허브 저장값에서 3묶음 복원. 없으면 축/상대/보조/구멍 기반으로 보정."""
    raw = str(latest.get("삼쌍승3묶음") or latest.get("삼쌍승추천3묶음") or latest.get("추천3묶음") or "").strip()
    groups: List[List[str]] = []
    if raw and raw.lower() not in ["nan", "none", "-"]:
        chunks = re.split(r"[|/;]+", raw)
        for ch in chunks:
            nums = re.findall(r"\d+", ch)
            if len(nums) >= 3:
                groups.append([str(int(nums[0])), str(int(nums[1])), str(int(nums[2]))])
    if len(groups) >= 3:
        return groups[:3]
    values = [
        latest.get("축마"), latest.get("상대마"), latest.get("보조마"), latest.get("구멍마"),
        latest.get("공격삼쌍승"), latest.get("방어삼복승"), latest.get("추천마권"), latest.get("추천마목록"), latest.get("상위마번")
    ]
    return make_triple_groups_from_nums(values)


def groups_to_text(groups: List[List[str]]) -> str:
    return " | ".join("-".join(g[:3]) for g in groups[:3])

def render_mobile_quick_view() -> None:
    """갤럭시 S26 Ultra 256GB 맞춤 모바일: 분석 앱 → 10초 수동구매 모드 → 공식 구매표 이동 흐름."""
    css()
    st.caption("S26 Ultra 256GB 맞춤 · 더비온 등록완료 모드 · 자동구매/자동결제 없음 · 공식 구매표에서 직접 입력·확정")

    ready = mobile_ready_recommendations(20)
    if ready.empty:
        st.markdown(
            f"""
<div class="mobile-phone" style="max-width:560px;">
  <div class="mobile-topbar"><span>☰</span><span>MARU KRA 실시간 분석</span><span>🔔</span></div>
  <div class="mobile-alert">지금 표시할 추천 없음</div>
  <div class="mobile-main-combo">
    <div class="race">구매 가능 시간대 대기 중</div>
    <div class="mobile-safe-note">아직 구매할 추천 조합이 없습니다.<br>PC/허브 분석 저장 후 모바일에 자동 표시됩니다.</div>
    <div class="mobile-safe-note">추천 저장 후 {MOBILE_READY_WINDOW_MIN}분 이내 · 결과대기 상태일 때만 표시</div>
  </div>
  <div class="mobile-copy-box">추천 확인 · 공식 구매 페이지 열기 · 새로고침</div>
  <div class="mobile-footer-line"><span>추천만 표시</span><span>18장 수동구매</span><span>직접 결제</span></div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown("### 📱 모바일에서 바로 추천 만들기")
        cur_mobile_race = current_live_race_from_schedule("서울", today_kst())
        default_no = int(cur_mobile_race.get("경주번호", 1)) if cur_mobile_race else 1
        default_time = str(cur_mobile_race.get("경주시간", st.session_state.get("race_time_text", ""))) if cur_mobile_race else st.session_state.get("race_time_text", "")
        mcol1, mcol2, mcol3 = st.columns([1.1, .8, 1])
        with mcol1:
            mobile_meet = st.selectbox("경마장", ["서울", "부산경남", "제주"], index=0, key="mobile_run_meet")
        with mcol2:
            mobile_race_no = st.number_input("경주", min_value=1, max_value=20, value=default_no, step=1, key="mobile_run_race_no")
        with mcol3:
            mobile_race_time = st.text_input("경주시간", value=default_time, placeholder="예: 14:30", key="mobile_run_race_time")
        st.caption("PC가 꺼져 있어도 Streamlit Cloud에서 API/캐시 분석 후 mobile_recommend.json을 저장합니다.")
        r0, r1 = st.columns(2)
        with r0:
            if st.button("🔥 지금 허브분석 실행", type="primary", width="stretch"):
                with st.spinner("모바일에서 허브분석 실행 중..."):
                    ok, row, msg = run_mobile_hub_analysis(mobile_meet, _safe_race_no(mobile_race_no), str(mobile_race_time))
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        with r1:
            if st.button("🔄 추천 확인", width="stretch"):
                st.rerun()
        st.link_button("↗ 더비온 공식 구매표 열기", kra_buy_url("서울"), width="stretch")
        st.stop()

    latest = sync_row_to_current_race(ready.iloc[0].to_dict(), force_if_stale=True)
    # 실제 시간표가 현재 6R인데 mobile_recommend.json이 1R로 남는 문제를 여기서 최종 차단
    meet = str(latest.get("경마장", "서울"))
    race_no = _norm_race_no(latest.get("경주번호", "-"))
    elapsed = latest.get("추천경과분", "-")
    confidence = latest.get("신뢰도", "-")
    odds = latest.get("예상배당", "-")
    risk = str(latest.get("위험도", "중간"))
    groups = parse_groups_from_latest(latest)
    tickets = expand_triple_18(groups)
    total_amount = len(tickets) * 1000
    status_info = _mobile_status_payload(latest)
    first_group = groups[0][:3] if groups else ["-", "-", "-"]
    first_combo = "-".join(first_group)
    first_tickets = expand_triple_18([first_group])[:6]
    first_text = (
        f"{meet} {race_no}R 삼쌍승 1조합 6장 / 각 1,000원 / 총 6,000원\n"
        + "\n".join([f"{i}. {c} / 1,000원" for i, c in enumerate(first_tickets, start=1)])
    )

    # 1번 화면: 분석 앱 요약 화면
    st.markdown(f"""
<div class="mobile-phone" style="max-width:560px;">
  <div class="mobile-topbar"><span>☰</span><span>MARU KRA 실시간 분석</span><span>🔔</span></div>
  <div class="mobile-glow-title">
    <div class="small">🏆 지금 놓치면 아까운 추천 · {elapsed}분 전 저장</div>
    <div class="race">{meet} {race_no}R</div>
    <div class="combo-main">삼쌍승 18장</div>
    <div class="combo-sub">3묶음 × 6순서 · 각 1,000원</div>
  </div>
</div>
""", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("예상배당", f"{odds}배")
    with m2:
        st.metric("신뢰도", f"{confidence}")
    with m3:
        st.metric("위험도", risk)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.metric("경주시간", status_info["race_time_text"])
    with s2:
        st.metric("추천저장", status_info["saved_at_text"])
    with s3:
        st.metric("상태", status_info["status"])

    st.markdown(f"""
<div class="mobile-budget" style="max-width:560px; margin-left:auto; margin-right:auto;">
  <div class="title">총 구매 기준</div>
  <div class="amount">{total_amount:,}원</div>
  <div class="mobile-safe-note">삼쌍승 {len(tickets)}장 × 1,000원 · {status_info['detail']}</div>
</div>
""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    labels = ["추천창 1 · 안정형", "추천창 2 · 변수형", "추천창 3 · 고배당형"]
    for col, label, g in zip([c1, c2, c3], labels, groups[:3]):
        with col:
            st.markdown(f"""
<div class="mobile-reco-card">
  <div class="card-title">{label}</div>
  <div class="card-combo">{'-'.join(g[:3])}</div>
  <div class="card-sub">6장 · 6,000원</div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="max-width:560px; margin:12px auto 8px auto; display:grid; gap:10px;">
  <div style="border:1.5px solid #d5a83c; border-radius:16px; padding:13px 14px; background:linear-gradient(180deg,#171717,#070707); color:#f8d777; font-weight:1000; display:flex; justify-content:space-between; align-items:center;">
    <span>🍃 허브 저장</span><span>›</span>
  </div>
  <div style="border-radius:16px; padding:15px 14px; background:linear-gradient(180deg,#ffd96d,#d39a24); color:#111; font-size:1.15rem; font-weight:1000; display:flex; justify-content:space-between; align-items:center;">
    <span>⏱ 10초 수동구매 모드</span><span>›</span>
  </div>
</div>
""", unsafe_allow_html=True)

    if status_info["result_text"] and status_info["result_text"] not in ["결과대기", "nan", "None"]:
        def _money_txt(v):
            try:
                return f"{int(float(v)):,}원"
            except Exception:
                return "-"
        st.success(f"결과 확인 · 실제결과 {status_info['result_text']} · 환급 {_money_txt(status_info['refund'])} · 손익 {_money_txt(status_info['profit'])}")
    elif status_info["status"] == "결과대기":
        st.warning("경주가 시작되었거나 종료되었습니다. 결과가 들어오면 이 자리에서 적중/실패/손익을 보여줍니다.")
    elif status_info["status"] == "구매 가능":
        st.info("지금은 구매 가능한 추천 화면입니다. 아래 10초 수동구매 모드에서 조합 복사 후 공식 구매표에서 직접 입력하세요.")
    else:
        st.info("아직 구매 대기 구간입니다. 추천은 유지되며 경주시간이 가까워지면 바로 확인하면 됩니다.")

    # 2번 화면: 10초 수동구매 모드 + 조합별 빠른 복사
    st.markdown(f"""
<div class="mobile-phone" style="max-width:560px; margin-top:18px;">
  <div class="mobile-topbar"><span>‹</span><span>10초 수동구매 모드</span><span>🔒</span></div>
  <div class="mobile-alert">🔔 지금 바로 확인</div>
  <div class="mobile-glow-title">
    <div class="race">{meet} {race_no}R</div>
    <div class="combo-main" style="font-size:3.2rem;">{first_combo}</div>
    <div class="combo-sub">1조합 6장 · 6,000원</div>
  </div>
  <div class="mobile-safe-note">추천 조합을 보고 공식 구매표에서 직접 입력</div>
</div>
""", unsafe_allow_html=True)

    group_texts: List[str] = []
    group_labels = ["1조합 6장", "2조합 6장", "3조합 6장"]
    for gi, g in enumerate(groups[:3], start=1):
        group_tickets = expand_triple_18([g])[:6]
        group_text = (
            f"{meet} {race_no}R 삼쌍승 {gi}조합 6장 / 각 1,000원 / 총 6,000원\n"
            + "\n".join([f"{i}. {c} / 1,000원" for i, c in enumerate(group_tickets, start=1)])
        )
        group_texts.append(group_text)

    st.markdown("### 🧩 조합별 빠른 복사")
    tabs = st.tabs(group_labels)
    for idx, tab in enumerate(tabs):
        with tab:
            group_text = group_texts[idx] if idx < len(group_texts) else "추천 조합 없음"
            st.caption(f"{['10초 급함','30초 가능','60초 가능'][idx]} · {group_labels[idx]}")
            st.text_area(f"{idx+1}조합 복사용", value=group_text, height=150, label_visibility="collapsed")
            st.download_button(
                f"📋 {idx+1}조합 6장 텍스트 받기",
                data=group_text.encode("utf-8"),
                file_name=f"MARU_{meet}_{race_no}R_{idx+1}조합_삼쌍승6장.txt",
                mime="text/plain",
                width="stretch",
                key=f"mobile_group_download_{idx+1}",
            )

    st.markdown(derbyon_notice_html(meet, race_no, first_combo), unsafe_allow_html=True)

    st.markdown(f"""
<div style="max-width:560px; margin:14px auto; background:#fff; color:#111; border-radius:22px; padding:18px; border:1px solid #e5e7eb;">
  <div style="font-size:1.15rem; font-weight:1000; color:#0f3b76; margin-bottom:12px;">KRA 공식 마권구매 페이지 입력 안내</div>
  <div style="display:grid; gap:9px; font-weight:900;">
    <div>경마장: <b>{meet}</b></div>
    <div>경주: <b>{race_no}R</b></div>
    <div>마권종류: <b>삼쌍승</b></div>
    <div>마번: <b>{first_combo}</b></div>
    <div>구매금액: <b>각 1,000원</b></div>
  </div>
  <div style="margin-top:12px; color:#6b7280; font-weight:800; font-size:.9rem;">결제 및 최종 확정은 공식 구매표에서 직접 진행</div>
</div>
""", unsafe_allow_html=True)

    d1, d2 = st.columns(2)
    with d1:
        if st.button("🔥 모바일 허브분석 재실행", type="primary", width="stretch"):
            with st.spinner("모바일에서 최신 추천 다시 만드는 중..."):
                ok, row, msg = run_mobile_hub_analysis(meet, _safe_race_no(race_no), status_info.get("race_time_text", ""))
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    with d2:
        if st.button("🔄 추천 확인", width="stretch"):
            st.rerun()
    st.link_button("↗ 더비온 공식 구매표 열기", kra_buy_url(meet), type="primary", width="stretch")

    st.caption("※ S26 Ultra 256GB 화면에 맞춰 분석 앱 → 10초 수동구매 모드 → 공식 구매표 이동 흐름으로 구성했습니다. 모바일에서 직접 허브분석 실행 가능, PC의 전체 분석/허브/API/빅데이터 기능은 그대로 유지됩니다.")
    st.stop()


def load_auto_analysis_log() -> pd.DataFrame:
    return load_csv_safe(AUTO_ANALYSIS_LOG_FILE)


def calc_strategy_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    """자동 허브가 저장한 결과/환급 로그로 전략별 효율을 계산합니다."""
    if df is None or df.empty:
        return pd.DataFrame()
    work = df.copy()
    for c in ["총구매", "총환급", "순손익"]:
        if c in work.columns:
            work[c] = pd.to_numeric(work[c], errors="coerce").fillna(0)
    if "전략명" not in work.columns:
        return pd.DataFrame()
    rows = []
    for name, g in work.groupby("전략명", dropna=False):
        total_bet = float(g.get("총구매", pd.Series(dtype=float)).sum())
        total_return = float(g.get("총환급", pd.Series(dtype=float)).sum())
        profit = float(g.get("순손익", pd.Series(dtype=float)).sum())
        hit_col = pd.to_numeric(g.get("적중여부", pd.Series([0]*len(g))), errors="coerce").fillna(0)
        rows.append({
            "전략명": name,
            "검증경주수": int(len(g)),
            "총구매": int(total_bet),
            "총환급": int(total_return),
            "총손익": int(profit),
            "ROI%": round((profit / total_bet * 100), 2) if total_bet else 0,
            "적중률%": round((hit_col.sum() / len(g) * 100), 2) if len(g) else 0,
            "평균손익": int(profit / len(g)) if len(g) else 0,
        })
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["ROI%", "총손익"], ascending=False)
        try:
            out.to_csv(STRATEGY_BIGDATA_FILE, index=False, encoding="utf-8-sig")
        except Exception:
            pass
    return out


def render_background_auto_hub_panel() -> None:
    st.markdown("### 🧠 접속 없어도 돌아가는 자동 허브/빅데이터 설계")
    st.info(
        "Streamlit 화면은 접속자가 있을 때 주로 실행됩니다. 그래서 '모바일/PC 접속 안 해도 매경기 자동 분석'은 "
        "동봉된 GitHub Actions 또는 서버 cron이 `auto_hub_runner.py`를 주기적으로 실행하는 구조로 처리합니다."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("아침 기본 데이터", "1회", "경주표·출전·말정보")
    c2.metric("경주 전 갱신", "30분", "체중·기수변경·주로")
    c3.metric("20분 전 실시간", "5분", "배당·인기·예측")

    st.markdown("#### 자동 실행 구조")
    st.markdown(
        """
- **API ON/OFF 유지**: 꺼둔 API는 자동 허브에서도 호출하지 않습니다.  
- **아침 1회용**: 경주표, 출전마, 말정보, 장구, 레이팅, 기록, 출발심사, 심판.  
- **30분용**: 체중, 기수변경, 코너/페이스, 기상특보.  
- **5분용**: 경주 예정시각 20분 전부터 배당, 당일배당, 인기, 단승/복승/삼복승 예측계열만 집중 갱신.  
- **허브 저장**: 경주별 추천, 추천 승식, 18,000원 삼쌍승 18장 구매안, 예상배당, 실제결과, 성공/실패, 손익을 CSV로 누적합니다.  
- **모바일/PC 확인**: 앱 접속 시 이미 쌓인 허브 추천과 전략별 수익 효율을 바로 불러옵니다.  
"""
    )

    log = load_auto_analysis_log()
    summary = calc_strategy_efficiency(log)
    st.markdown("#### 18,000원 삼쌍승 18장 전략별 빅데이터")
    if summary.empty:
        st.warning("아직 자동 검증 로그가 없습니다. GitHub Actions가 돌기 시작하면 전략별 적중률/손익/ROI가 여기에 쌓입니다.")
    else:
        show_cols = [c for c in ["전략명", "검증경주수", "적중률%", "총구매", "총환급", "총손익", "ROI%", "평균손익"] if c in summary.columns]
        st.dataframe(summary[show_cols], width="stretch", height=260)
        best = summary.iloc[0].to_dict()
        st.success(f"현재 누적 기준 효율 1위: {best.get('전략명','-')} / ROI {best.get('ROI%',0)}% / 총손익 {int(best.get('총손익',0)):,}원")

    with st.expander("최근 자동 허브 로그", expanded=False):
        if log.empty:
            st.caption("아직 로그 없음")
        else:
            cols = [c for c in ["저장시각", "날짜", "경마장", "경주번호", "전략명", "추천마권", "총구매", "총환급", "순손익", "적중여부", "결과마번"] if c in log.columns]
            st.dataframe(log[cols].tail(100) if cols else log.tail(100), width="stretch", height=360)

    with st.expander("GitHub Actions 설정 방법", expanded=False):
        st.markdown(
            """
1. 이 압축 파일을 GitHub 저장소에 올립니다.  
2. GitHub 저장소 `Settings → Secrets and variables → Actions`에서 `PUBLIC_DATA_API_KEY`를 추가합니다.  
3. `.github/workflows/maru_kra_auto_hub.yml`가 5분마다 `auto_hub_runner.py`를 실행합니다.  
4. 실행 결과는 `maru_kra_data/` CSV로 저장되고, workflow가 자동 커밋합니다.  
5. Streamlit 앱은 이 허브 CSV를 읽어서 모바일/PC에 추천과 빅데이터 결과를 보여줍니다.  

※ GitHub Actions 스케줄은 무료 환경에서 약간 지연될 수 있습니다. 더 정확한 실행은 개인 PC 작업 스케줄러, VPS, NAS cron이 더 안정적입니다.
"""
        )

def render_smart_collection_panel(rc_date: str, meet: str, race_no: int) -> None:
    st.markdown("### ⏱ 스마트 API 수집 / 허브 추천 시스템")
    st.info("결론: 26개 API를 매번 전부 호출할 필요 없습니다. 아침에는 기본 데이터를 한 번 저장하고, 경주 예정시각 20분 전부터 배당·인기·예측계열처럼 진짜 바뀌는 것만 5분마다 갱신하면 됩니다.")

    render_background_auto_hub_panel()

    mode = st.session_state.get("collection_mode", "스마트 자동")
    manual_selected = [k for k, _ in API_LABELS if get_api_switches().get(k, False)]
    selected_now = smart_selected_apis(mode, manual_selected)
    st.markdown(f"#### 현재 수집 모드: **{mode}**")
    st.caption(f"이번 모드 호출 대상: {len(selected_now)}/26개")

    plan_rows = []
    for k, label in API_LABELS:
        plan_rows.append({
            "API": label,
            "분류": API_SMART_GROUP.get(k, "기타"),
            "재호출 기준": f"{API_SMART_INTERVAL_MIN.get(k, 60)}분",
            "이번 모드": "ON" if k in selected_now else "OFF",
        })
    st.dataframe(pd.DataFrame(plan_rows), width="stretch", height=360)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🌅 오늘 아침 사전수집", width="stretch"):
            st.session_state["collection_mode"] = "아침 사전수집"
            st.rerun()
    with c2:
        if st.button("⚡ 경주 직전 실시간만", width="stretch"):
            st.session_state["collection_mode"] = "실시간 집중"
            st.rerun()
    with c3:
        if st.button("📦 허브만 불러오기", width="stretch"):
            st.session_state["collection_mode"] = "허브만 분석"
            st.rerun()

    st.markdown("#### 모바일/PC 추천 허브")
    hub = load_shared_recommendations(30)
    if hub.empty:
        st.warning("아직 저장된 추천 허브가 없습니다. 실시간 분석 탭에서 '현재 분석 허브 저장'을 누르면 모바일/PC에서 같은 추천을 확인할 수 있습니다.")
    else:
        show_cols = [c for c in ["저장시각", "날짜", "경마장", "경주번호", "축마", "상대마", "보조마", "공격삼쌍승", "방어삼복승", "예상배당", "신뢰도", "추천금액"] if c in hub.columns]
        st.dataframe(hub[show_cols] if show_cols else hub, width="stretch", height=300)
        latest = hub.iloc[0].to_dict()
        st.success(f"최근 추천: {latest.get('경마장','-')} {latest.get('경주번호','-')}R / 축 {latest.get('축마','-')} - 상대 {latest.get('상대마','-')} - 보조 {latest.get('보조마','-')} / {latest.get('공격삼쌍승','-')}")

    st.markdown("#### 권장 운영 흐름")
    st.markdown("""
1. **아침/경주 시작 전**: `아침 사전수집`으로 경주표·출전마·말정보·레이팅·기록을 한 번 저장합니다.  
2. **경주 30~60분 전**: `경주 전 1회수집`으로 체중·기수변경·주로/기상·배당 계열을 갱신합니다.  
3. **경주 직전**: `실시간 집중`으로 배당·인기·기상·변경 정보만 빠르게 갱신합니다.  
4. **현장 모바일**: API를 다시 다 치지 말고 `허브만 분석` 또는 최근 저장 추천을 불러와 확인합니다.  
""")

# -----------------------------------------------------------------------------
# UI render
# -----------------------------------------------------------------------------
def render_live_panel(rc_date: str, meet: str, race_no: int, selected: List[str], sim_count: int, risk_mode: str) -> Tuple[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]], Dict[str, pd.DataFrame], pd.DataFrame, Dict[str, Any]]:
    st.markdown("### 실시간 KRA 분석")
    if "live_data" not in st.session_state:
        st.session_state["live_data"] = {}
        st.session_state["api_status"] = pd.DataFrame()

    col_a, col_b = st.columns([1, 1])
    with col_a:
        run = st.button("실시간 데이터 새로고침", type="primary")
    with col_b:
        run_sim = st.button("불러오기 + 시뮬레이션")

    if run or run_sim:
        with st.spinner("실시간 API 수집 중... 최대 30~60초 걸릴 수 있습니다."):
            data, status = fetch_all_live(rc_date, meet, int(race_no), selected)
        st.session_state["live_data"] = data
        st.session_state["api_status"] = status
    elif not st.session_state.get("live_data"):
        # 첫 화면에서는 API를 자동 호출하지 않습니다.
        # Streamlit Cloud에서 외부 API 응답 지연이 있으면 흰 화면/스피너가 오래 지속되기 때문입니다.
        cache = load_live_cache()
        st.session_state["live_data"] = cache if cache else {}
        st.session_state["api_status"] = pd.DataFrame([{"API":"초기화","상태":"첫 화면 빠른 로딩: API 자동호출 OFF · 버튼 클릭 시 수집","행수":sum(len(v) for v in cache.values()) if cache else 0}])

    data = st.session_state.get("live_data", {})
    status = st.session_state.get("api_status", pd.DataFrame())
    env = fetch_weather(meet)
    base = build_base_horses(data, rc_date, meet, int(race_no))
    horses = merge_score_features(base, data, rc_date, meet, int(race_no))
    score_df, result, combos = score_and_recommend(horses, env, sim_count, risk_mode)

    live_rows = sum(len(v) for v in data.values()) if data else 0
    sample_mode = not api_required_group_pass(status if 'status' in locals() else locals().get('status_df', pd.DataFrame()), live_rows)
    if sample_mode:
        st.markdown('<div class="info-box-warn">⚠ 실전 검증 추천이 아닙니다. 필수 성공 API 묶음이 부족하여 검증대기 상태입니다. 결과대기 API는 실패로 보지 않습니다.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="info-box-ok">✅ 현재 경주 매칭 API 데이터 {live_rows:,}행 반영 · 실전 추천 표시 가능</div>', unsafe_allow_html=True)

    # HOTFIX: 실시간 수집 버튼 실행 후 결과가 있으면 허브/mobile_recommend.json 자동 저장
    if (run or run_sim) and (not sample_mode) and live_rows > 0:
        auto_row = {
            "저장시각": now_str(), "날짜": rc_date, "경마장": meet, "경주번호": int(race_no),
            "경주시간": st.session_state.get("race_time_text", ""),
            "축마": result.get("축마"), "상대마": result.get("상대마"), "보조마": result.get("보조마"), "구멍마": result.get("구멍마"),
            "공격삼쌍승": result.get("공격삼쌍승"), "방어삼복승": result.get("방어삼복승"),
            "삼쌍승3묶음": result.get("삼쌍승3묶음"), "삼쌍승18조합": result.get("삼쌍승18조합"),
            "예상배당": result.get("예상배당"), "신뢰도": result.get("신뢰도"), "위험도": result.get("위험도", "중간"),
            "추천금액": result.get("추천금액", 18000), "근거": result.get("근거"), "실시간행수": live_rows,
            "데이터상태": "실시간", "실전검증": "Y", "실전표시불가": "N",
            "분석모드": "PC 실시간 API 수집 자동저장", "모바일생성": "Y",
        }
        schedule_df = extract_schedule_from_data(data, rc_date, meet)
        apply_mobile_plan_update(auto_row, score_df, schedule_df)
        auto_row = merge_18ticket_into_row(auto_row, score_df, int(auto_row.get("추천금액", 18000) or 18000))
        if save_shared_recommendation(auto_row):
            st.success("허브/mobile_recommend.json 자동 저장 완료 · 하루 경주시간표 기준 20분 전 모바일 추천도 생성했습니다.")
        else:
            st.error("자동 저장 실패: 파일 권한 또는 저장소 상태를 확인하세요.")

    display_combo = "추천 대기" if sample_mode else str(result.get("공격삼쌍승", "-"))
    display_trio = "-" if sample_mode else str(result.get("방어삼복승", "-"))
    display_roles = "검증대기" if sample_mode else f"{result.get('축마')}-{result.get('상대마')}-{result.get('보조마')}-{result.get('구멍마')}"
    display_conf = 0 if sample_mode else int(result.get("신뢰도", 0))
    display_odds = "-" if sample_mode else str(result.get("예상배당", 0))
    display_amount = 0 if sample_mode else int(result.get("추천금액", 0))
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown(f"""
<div class="focus-card">
<div class="focus-badge">{('검증대기 · 추천 숨김' if sample_mode else '놓치면 아까운 조합')}</div>
<div class="focus-combo">{display_combo}</div>
<div class="reco-meta">{meet} {int(race_no)}R · {rc_date} · {env.get('날씨')}/{env.get('주로')}</div>
<div class="metric-wrap">
<div class="metric-box"><div class="m-title">신뢰도</div><div class="m-value-green">{display_conf}</div></div>
<div class="metric-box"><div class="m-title">예상배당</div><div class="m-value-orange">{display_odds}</div></div>
<div class="metric-box"><div class="m-title">추천금액</div><div class="m-value-blue">{display_amount:,}원</div></div>
</div>
<hr>
<b>방어 삼복승:</b> {display_trio}<br>
<b>축/상대/보조/구멍:</b> {display_roles}<br>
<b>근거:</b> {result.get('근거','')}
</div>
""", unsafe_allow_html=True)
        st.caption("경마 결과는 보장되지 않습니다. 실구매는 본인 판단과 책임, 소액 원칙으로만 진행하세요.")
        st.link_button("↗ 더비온/KRA 공식 구매표 열기", kra_buy_url(meet), width="stretch")
        st.caption("※ 자동구매 아님 · KRA 공식 화면으로 이동 · 로그인/구매는 본인 직접 진행")
    with right:
        st.markdown("#### 🧾 10초 수동구매 체크")
        st.markdown(f'<div class="bigline">{("실전 추천 대기" if sample_mode else "축 " + str(result.get("축마")) + " / 상대 " + str(result.get("상대마")) + " / 보조 " + str(result.get("보조마")))}</div>', unsafe_allow_html=True)
        st.markdown("- 자동구매/자동결제는 하지 않습니다.\n- 공식 화면으로 이동 후 직접 입력/확정합니다.\n- 배당은 경주 직전까지 변동됩니다.")
        if sample_mode:
            st.warning("현재 추천은 실전 검증 전이라 허브 저장을 막았습니다. 실제 현재 경주 API 데이터가 들어온 뒤 저장하세요.")
        elif st.button("현재 분석 허브 저장", type="primary"):
            row = {
                "저장시각": now_str(), "날짜": rc_date, "경마장": meet, "경주번호": int(race_no),
                "경주시간": st.session_state.get("race_time_text", ""),
                "축마": result.get("축마"), "상대마": result.get("상대마"), "보조마": result.get("보조마"), "구멍마": result.get("구멍마"),
                "공격삼쌍승": result.get("공격삼쌍승"), "방어삼복승": result.get("방어삼복승"),
                "삼쌍승3묶음": result.get("삼쌍승3묶음"), "삼쌍승18조합": result.get("삼쌍승18조합"),
                "예상배당": result.get("예상배당"), "신뢰도": result.get("신뢰도"),
                "추천금액": result.get("추천금액"), "근거": result.get("근거"), "실시간행수": live_rows,
                "데이터상태": "실시간" if live_rows > 0 else "샘플", "실전검증": "Y" if live_rows > 0 else "N",
                "실전표시불가": "N" if live_rows > 0 else "Y", "분석모드": "PC 수동 허브 저장",
            }
            ok = save_shared_recommendation(row)
            if ok:
                st.success("공유 허브/로컬 허브/빅데이터 로그 저장 완료 · 모바일/PC에서 같은 앱으로 추천 확인 가능")
            else:
                st.error("저장 실패: 폴더 권한 또는 파일 열림 상태를 확인하세요.")

    with st.expander("상세 데이터", expanded=False):
        st.markdown("#### TOP 말 점수")
        show_cols = [c for c in ["마번", "마명", "점수", "최근순위", "레이팅", "체중변화", "기수점수", "인기", "예상배당", "위험", "근거"] if c in score_df.columns]
        st.dataframe(score_df[show_cols].head(12) if show_cols else score_df.head(12), width="stretch", height=330)
        st.markdown("#### 최근 시뮬레이션 조합")
        st.dataframe(pd.DataFrame(combos).head(30), width="stretch", height=260)
    return score_df, result, combos, data, status, env


def render_api_hub_panel(status: pd.DataFrame, data: Dict[str, pd.DataFrame]) -> None:
    st.markdown("### API 상태 / 허브 저장")
    with st.expander("API 상태 요약", expanded=True):
        if isinstance(status, pd.DataFrame) and not status.empty:
            keep_cols = [c for c in ["API", "행수", "상태", "URL"] if c in status.columns]
            st.dataframe(status[keep_cols] if keep_cols else status, width="stretch", height=360)
        else:
            st.info("아직 API 호출 전입니다.")
    with st.expander("허브 저장 현황", expanded=True):
        local_hub_df = load_local_hub()
        big_df = load_bigdata()
        h1, h2, h3 = st.columns(3)
        h1.metric("허브 저장", f"{len(local_hub_df):,}건")
        h2.metric("빅데이터 로그", f"{len(big_df):,}건")
        h3.metric("현재 데이터", f"{sum(len(v) for v in data.values()) if data else 0:,}행")
        if not local_hub_df.empty:
            show_cols = [c for c in ["저장시각", "경마장", "경주번호", "공격삼쌍승", "방어삼복승", "예상배당", "신뢰도", "추천금액"] if c in local_hub_df.columns]
            st.dataframe(local_hub_df[show_cols].tail(30) if show_cols else local_hub_df.tail(30), width="stretch", height=330)
        else:
            st.info("허브 저장 데이터가 아직 없습니다.")
    with st.expander("API URL 26개 자동내장 확인용", expanded=False):
        for k, label in API_LABELS:
            st.caption(f"{label}: {get_url(k)}")



def render_triple18_dashboard_module(result: Dict[str, Any], meet: str) -> None:
    """PC/관리 화면에서도 모바일과 같은 18,000원 삼쌍승 18장 구매표를 확인합니다."""
    st.markdown("### 🎯 18,000원 기준 · 삼쌍승 18장 대시보드")
    st.info("상단 추천창 3개를 만들고, 각 추천창의 3마리 조합을 6순서로 전개합니다. 총 18장 × 1,000원 = 18,000원입니다. 자동구매/자동결제는 없고 공식 구매표에서 직접 입력·확정합니다.")

    groups = []
    raw = result.get("삼쌍승3묶음", "")
    if raw:
        for part in str(raw).split("|"):
            nums = re.findall(r"\d+", part)
            if len(nums) >= 3:
                groups.append([str(int(nums[0])), str(int(nums[1])), str(int(nums[2]))])
    if len(groups) < 3:
        values = [result.get("축마"), result.get("상대마"), result.get("보조마"), result.get("구멍마"), result.get("공격삼쌍승"), result.get("방어삼복승")]
        groups = make_triple_groups_from_nums(values)
    groups = groups[:3]
    tickets = expand_triple_18(groups)
    total_amount = len(tickets) * 1000

    c1, c2, c3 = st.columns(3)
    for i, (col, g) in enumerate(zip([c1, c2, c3], groups), start=1):
        with col:
            st.markdown(
                f"""
<div class="mobile-reco-card" style="margin-bottom:12px;">
  <div class="card-title">추천창 {i}</div>
  <div class="card-combo">{'-'.join(g[:3])}</div>
  <div class="card-sub">6장 · 6,000원</div>
</div>
""",
                unsafe_allow_html=True,
            )

    df = pd.DataFrame({
        "번호": list(range(1, len(tickets)+1)),
        "승식": ["삼쌍승"] * len(tickets),
        "추천번호": tickets,
        "구매금액": [1000] * len(tickets),
    })
    st.markdown("#### ✅ 삼쌍승 18장 구매표")
    st.dataframe(df, width="stretch", hide_index=True)
    st.metric("총 구매 기준", f"{total_amount:,}원")

    copy_text = f"{meet} 삼쌍승 18장 / 각 1,000원 / 총 {total_amount:,}원\n" + "\n".join([f"{i}. {c} / 1,000원" for i, c in enumerate(tickets, start=1)])
    st.markdown("#### 📋 복사용 추천번호")
    st.code(copy_text, language="text")
    st.download_button("추천번호 텍스트 받기", data=copy_text.encode("utf-8"), file_name="MARU_삼쌍승18장.txt", mime="text/plain", width="stretch")
    st.link_button("↗ 더비온 공식 구매표 열기", kra_buy_url(meet), type="primary", width="stretch")
    st.caption("※ 추천번호를 복사/확인한 뒤 공식 구매 페이지에서 사용자가 직접 입력·결제합니다.")


def render_help_panel() -> None:
    st.markdown("### 사용법 / 안전 안내")
    st.markdown(
        """
1. 사이드바에서 **공공데이터 API Key**를 저장합니다.  
2. 경마장, 날짜, 경주번호를 선택합니다.  
3. 현장에서 HTTP 500이 나는 API는 **API ON/OFF**에서 꺼도 앱은 계속 작동합니다.  
4. 추천 결과는 참고용입니다. 실제 구매는 공식 KRA 화면에서 직접 입력·확정합니다.  
5. **18,000원 삼쌍승 18장**은 손실을 줄이는 구조일 뿐 수익 보장이 아닙니다.

**자동구매/자동결제 기능은 없습니다.** 이 앱은 분석, 기록, 허브 저장, 공식 구매표 이동만 제공합니다.

### 스마트 수집 원칙
- 26개 API를 매번 전부 호출하지 않습니다.
- 아침에는 경주표/출전마/말정보/레이팅 같은 기본 데이터를 1회 저장합니다.
- 경주 직전에는 배당/인기/기상/체중/기수변경처럼 바뀌는 데이터만 갱신합니다.
- 모바일/PC는 같은 Streamlit 앱의 허브 저장 자료를 불러와 추천을 확인합니다.
- 접속자가 없어도 자동 분석하려면 동봉된 GitHub Actions 또는 서버 cron이 `auto_hub_runner.py`를 실행합니다.
"""
    )


def render() -> None:
    # PC 기본 화면은 기존 그대로 유지합니다.
    # 휴대폰 접속은 URL 파라미터가 없어도 자동으로 모바일 10초 구매 화면으로 분리합니다.
    # PC에서 강제로 모바일을 보려면 ?mode=mobile, 휴대폰에서 PC를 보려면 ?mode=pc 를 사용합니다.
    if _should_show_mobile():
        render_mobile_quick_view()
        return
    css()
    st.markdown(
        """
<div class="hero">
<h2>MARU KRA 실전 대시보드</h2>
<div class="muted">26개 API URL 자동내장 · 재입력 없음 · 스마트 자동수집 · API ON/OFF · 접속 없이 자동 허브 · PC 전체관리 / 모바일 10초 구매 분리</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.caption("자동구매/자동결제 없음. 공식 구매 페이지로 이동 후 사용자가 직접 입력·확정합니다.")

    with st.sidebar:
        st.title("🐎 MARU KRA")
        st.success("전체 통합본 · 기존 19개 + 추가 7개 = 26개 API URL 자동내장")
        st.caption("PC 화면은 기존 전체 대시보드 유지")
        st.success(f"외부 모바일 고정주소: {CLOUD_MOBILE_URL}")
        st.link_button("📱 모바일 10초 구매 전용 화면", CLOUD_MOBILE_URL, width="stretch")
        st.link_button("🖥 휴대폰에서 PC 관리화면 보기", CLOUD_PC_URL, width="stretch")
        st.toggle("✅ 더비온 등록완료 모드", value=st.session_state.get("derbyon_registered", True), key="derbyon_registered", help="본인인증/등록을 마친 경우 공식 구매표 이동 안내를 활성화합니다. 자동구매는 하지 않습니다.")
        st.info("API URL 26개는 프로그램 안에 고정 탑재되어 있습니다. URL은 다시 입력하지 않아도 됩니다.")
        st.info(f"현재 한국시간: {now_kst().strftime('%Y-%m-%d %H:%M:%S')} KST")
        current_key = get_api_key()
        if current_key:
            st.success("공공데이터 API Key 자동 적용됨 · 모바일 재입력 불필요")
            st.caption(f"키 출처: {get_api_key_source()} / {masked_api_key()}")
            with st.expander("API Key 변경/재저장", expanded=False):
                key_input = st.text_input("공공데이터 API Key", value=current_key, type="password", placeholder="공공데이터 일반 인증키 입력")
                if st.button("API Key 저장", width="stretch"):
                    if key_input.strip():
                        st.session_state["api_key_saved"] = key_input.strip()
                        if save_local_settings({"api_key": key_input.strip(), "saved_at_kst": now_str()}):
                            st.success("API Key 저장 완료")
                            st.rerun()
                        else:
                            st.warning("세션에는 저장됐지만 파일 저장은 실패했습니다.")
                    else:
                        st.warning("API Key를 입력해 주세요.")
        else:
            st.error("API Key 없음")
            st.info("모바일 입력이 힘들면 PC에서 Streamlit Secrets 또는 .streamlit/secrets.toml에 한 번만 저장하세요.")
            key_input = st.text_input("공공데이터 API Key", value="", type="password", placeholder="공공데이터 일반 인증키 입력")
            if st.button("API Key 저장", width="stretch"):
                if key_input.strip():
                    st.session_state["api_key_saved"] = key_input.strip()
                    if save_local_settings({"api_key": key_input.strip(), "saved_at_kst": now_str()}):
                        st.success("API Key 저장 완료")
                        st.rerun()
                    else:
                        st.warning("세션에는 저장됐지만 파일 저장은 실패했습니다.")
                else:
                    st.warning("API Key를 입력해 주세요.")

        rc_date = st.text_input("분석 날짜", value=today_kst())
        meet = st.selectbox("경마장", ["서울", "부산경남", "제주"], index=0)
        race_no = st.number_input("경주번호", min_value=1, max_value=20, value=1, step=1)
        race_time_text = st.text_input("경주 예정시각", value=st.session_state.get("race_time_text", ""), placeholder="예: 14:30")
        st.session_state["race_time_text"] = race_time_text
        sim_count = st.slider("시뮬레이션", 300, 5000, 1200, step=100)
        risk_mode = st.selectbox("전략", ["균형형", "안전형", "공격형"], index=0)
        collection_mode = st.selectbox("API 수집 모드", ["스마트 자동", "아침 사전수집", "경주 전 1회수집", "실시간 집중", "허브만 분석", "수동 ON/OFF", "전체 26개"], index=4, help="첫 화면 로딩 방지를 위해 기본값은 허브만 분석입니다. 실시간 수집은 버튼을 눌러 실행하세요.")
        st.session_state["collection_mode"] = collection_mode
        default_refresh = smart_default_refresh_seconds(collection_mode)
        refresh_options = [0, 60, 120, 300, 600, 3600]
        refresh_index = refresh_options.index(default_refresh) if default_refresh in refresh_options else 0
        auto_refresh = st.selectbox("자동 새로고침", refresh_options, index=refresh_index, format_func=lambda x: "OFF" if x == 0 else ("1시간" if x == 3600 else f"{x}초"))
        render_api_onoff_panel()
        switches = get_api_switches()
        selected = [k for k, _ in API_LABELS if switches.get(k, False)]
        selected = smart_selected_apis(collection_mode, selected)
        st.caption(f"이번 수집 대상: {len(selected)}/26개 · 모드: {collection_mode}")
        if collection_mode == "스마트 자동":
            state = st.session_state.get("smart_window_state", live_window_state(st.session_state.get("race_time_text", "")))
            if state == "20분전_실시간":
                st.success("경주 20분 전 구간: 배당·인기·예측계열을 5분 주기로 집중 갱신합니다.")
            elif state == "60분전_점검":
                st.info("경주 60~20분 전 구간: 체중·기수변경·주로·기상 중심으로 갱신합니다.")
            elif state == "시간미입력":
                st.warning("경주 예정시각을 넣으면 20분 전부터 실시간 API만 자동 갱신합니다. 미입력 시 기본자료/캐시 중심으로 분석합니다.")
            else:
                st.caption(f"스마트 상태: {state}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏇 실시간 분석", "🎯 삼쌍승18장/배당", "🔌 API/허브", "⏱ 스마트수집", "📘 도움말"])
    with tab1:
        score_df, result, combos, data, status, env = render_live_panel(rc_date, meet, int(race_no), selected, int(sim_count), risk_mode)
    with tab2:
        # Use last/live result if available; otherwise calculate sample instantly.
        if "live_data" in st.session_state:
            data2 = st.session_state.get("live_data", {})
        else:
            data2 = {}
        env2 = fetch_weather(meet)
        base2 = build_base_horses(data2, rc_date, meet, int(race_no))
        horses2 = merge_score_features(base2, data2, rc_date, meet, int(race_no))
        _, result2, _ = score_and_recommend(horses2, env2, int(sim_count), risk_mode)
        render_triple18_dashboard_module(result2, meet)
    with tab3:
        status2 = st.session_state.get("api_status", pd.DataFrame())
        data3 = st.session_state.get("live_data", {})
        st.success("✅ API URL 26개 자동 탑재 완료: 재입력 없이 호출/ON-OFF만 사용")
        render_api_hub_panel(status2, data3)
    with tab4:
        render_smart_collection_panel(rc_date, meet, int(race_no))
    with tab5:
        render_help_panel()

    if int(auto_refresh or 0) > 0:
        st.caption(f"자동 새로고침 설정: {int(auto_refresh)}초 · 현재 핫픽스에서는 자동 새로고침 대신 수동 새로고침을 권장합니다.")


if __name__ == "__main__":
    render()

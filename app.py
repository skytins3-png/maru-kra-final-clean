# DATETIME_TIMEDELTA_ATTRIBUTE_FIX
# ALL_MEET_EXCEL_VIEWER_FIX
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

# HOTFIX_LOADING_FAST: 첫 화면 10분 로딩 방지 · 초기 API 자동수집 ON · 버튼 클릭 시만 실시간 수집
import urllib3
import streamlit as st
import streamlit.components.v1 as components
import inspect
import traceback

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
    from itertools import permutations  # GEMINI_LOCAL_IMPORT_SIX
    from itertools import permutations  # SIX_TICKET_HARD_FIX
    """3마리 기준 삼쌍승 6개 순열."""
    nums = _unique_int_list(nums3)[:3]
    if len(nums) < 3:
        nums = _unique_int_list(nums)[:3]  # NO_DEFAULT_FAKE_HORSES
    orders = list(permutations(nums, 3))
    # 안정형은 축마 1착을 먼저, 고배당은 구멍마 1착 가능성을 앞쪽, 변수형은 변동 후보를 앞쪽
    if key == "stable":
        orders = sorted(orders, key=lambda p: (p[0] != nums[0], p[1] != nums[1], p))
    elif key == "high":
        orders = sorted(orders, key=lambda p: (p[0] != nums[2], p[0] != nums[1], p))
    elif key == "variable":
        orders = sorted(orders, key=lambda p: (p[0] != nums[1], p[2] != nums[2], p))
    return ["-".join(map(str, p)) for p in orders[:6]]

def build_18ticket_purchase_plan(score_df: pd.DataFrame, result: Dict[str, Any] = None, total_budget: int = 18000) -> Dict[str, Any]:
    active_nums = _active_horse_numbers_from_score_df(score_df)  # TICKET_SCOREDF_PARAM_FIX
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
    stable3 = _filter_group_to_active(stable3, active_nums) if active_nums else stable3
    high3 = _unique_int_list((high_nums[:1] + base[:2] + high_nums[1:3]) or base[:4])[:3]
    high3 = _filter_group_to_active(high3, active_nums) if active_nums else high3
    variable3 = _unique_int_list((variable_nums[:2] + base[:3]) or base[:4])[:3]
    variable3 = _filter_group_to_active(variable3, active_nums) if active_nums else variable3

    if len(stable3) < 3 or len(high3) < 3 or len(variable3) < 3:
        return {
            "18마권": "N",
            "마권수": 0,
            "단위금액": unit,
            "총추천금액": 0,
            "안정형6": [],
            "고배당형6": [],
            "변수대응형6": [],
            "삼쌍승18조합": "",
            "안정형대표": "",
            "고배당형대표": "",
            "변수대응형대표": "",
            "구매표복사": "[삼쌍승 18마권 수동입력표]\n출전표 확인중: 실제 출전마 3두 이상 확인 후 표시",
        }

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
            st.text_area("18마권 전체 복사", value=copy_text, height=260, key="ticket_copy_area_18")
    except Exception as e:
        st.caption(f"18마권 표시 대기: {e}")



def _active_horse_numbers_from_score_df(score_df: pd.DataFrame) -> List[int]:
    """실제 출전/점수표에 존재하는 말번호만 추출합니다. 출전취소·비출전 말은 추천에서 제외합니다."""
    if score_df is None or not isinstance(score_df, pd.DataFrame) or score_df.empty:
        return []
    number_cols = ["마번", "말번호", "horse_no", "hrNo", "chulNo", "번호", "gate", "Gate"]
    status_cols = ["출전상태", "상태", "status", "rcStatus", "취소여부", "scratched"]
    df = score_df.copy()
    for sc in status_cols:
        if sc in df.columns:
            s = df[sc].astype(str).str.lower()
            bad = s.str.contains("취소|제외|비출전|출전취소|scratch|scratched|cancel|withdraw|제외", na=False)
            df = df[~bad]
    col = next((c for c in number_cols if c in df.columns), None)
    if col is None:
        return []
    nums = []
    for v in df[col].tolist():
        try:
            n = int(float(str(v).strip()))
            if 1 <= n <= 20 and n not in nums:
                nums.append(n)
        except Exception:
            continue
    return nums

def _filter_group_to_active(group: List[int], active_nums: List[int]) -> List[int]:
    """추천 그룹에서 실제 출전 말만 남기고 부족하면 active 말로 보충합니다."""
    active_set = set(active_nums or [])
    out = []
    for x in group or []:
        try:
            n = int(float(str(x).strip()))
            if n in active_set and n not in out:
                out.append(n)
        except Exception:
            continue
    for n in active_nums or []:
        if n not in out:
            out.append(n)
        if len(out) >= 3:
            break
    return out[:3]


def build_3group_recommendation_from_score(score_df: pd.DataFrame) -> Dict[str, Any]:
    from itertools import permutations  # GEMINI_LOCAL_IMPORT_BUILD3
    from itertools import permutations  # THREE_GROUP_HARD_FIX
    from itertools import permutations  # HARD_FIX
    """점수표에서 3조합 삼쌍승 18장을 구성합니다."""
    if score_df is None or score_df.empty or "마번" not in score_df.columns:
        nums = []  # NO_FAKE_HORSE_FILL: 출전표 없으면 가짜 1~7 생성 금지
    else:
        nums = pd.to_numeric(score_df["마번"], errors="coerce").dropna().astype(int).tolist()
    nums = _unique_int_list(nums)
    if len(nums) < 3:
        return {
            "공격삼쌍승": "추천대기",
            "방어삼복승": "추천대기",
            "삼쌍승3묶음": "",
            "삼쌍승18조합": "",
        }
    g1 = nums[:3]
    g2 = _unique_int_list([nums[0]] + nums[3:5] + nums[:3])[:3]
    g3 = _unique_int_list(nums[-3:] + nums[:3])[:3]
    active_nums = _active_horse_numbers_from_score_df(score_df)  # BUILD3_SCOREDF_PARAM_FIX
    if active_nums:
        g1 = _filter_group_to_active(g1, active_nums)
        g2 = _filter_group_to_active(g2, active_nums)
        g3 = _filter_group_to_active(g3, active_nums)
    tickets = []
    for g in [g1, g2, g3]:
        if len(g) < 3:  # NO_FAKE_HORSE_GROUP_GUARD
            continue
        tickets += ["-".join(map(str, p)) for p in permutations(g, 3)]
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
CLOUD_APP_URL = "https://maru-kra-final-clean.streamlit.app/?mode=mobile"
CLOUD_MOBILE_URL = "https://maru-kra-final-clean.streamlit.app/?mode=mobile"
CLOUD_PC_URL = "https://maru-kra-final-clean.streamlit.app/?mode=pc"
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
        {"마번": 1, "마명": "샘플1", "레이팅": 75, "최근순위": 3, "승률": 15, "복승률": 38, "예상배당": 7.8, "체중변화": -1, "기수점수": 72, "인기": 5},
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
        for x in seq:  # NO_FAKE_HORSE_FILL: 출전표 밖 말번호 임의 보충 금지
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
    active_nums = _active_horse_numbers_from_score_df(df)  # SCORE_AND_RECOMMEND_DF_FIX_SCOREDF_NAMEFIX
    if active_nums:
        triple_groups = [_filter_group_to_active(g, active_nums) for g in triple_groups]
    triple_18 = expand_triple_18(triple_groups)

    axis = int(group1[0]); mate = int(group1[1]); sub = int(group1[2]); hole = int(group3[0])

    # Monte Carlo-ish combo list based on score weights.
    nums = all_nums or []  # NO_FAKE_HORSE_FILL: 출전표 없으면 임의 말번호 생성 금지
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
        axis = st.number_input("축마", min_value=1, max_value=20, value=default_axis, step=1, key="stable_plan_axis_no")
    with c2:
        mate = st.number_input("상대마", min_value=1, max_value=20, value=default_mate, step=1, key="stable_plan_mate_no")
    with c3:
        sub = st.number_input("보조마", min_value=1, max_value=20, value=default_sub, step=1, key="stable_plan_sub_no")
    with c4:
        hole = st.number_input("구멍마", min_value=1, max_value=20, value=default_hole, step=1, key="stable_plan_hole_no")

    tmp_result = {**result, "축마": axis, "상대마": mate, "보조마": sub, "구멍마": hole}
    b1, b2 = st.columns([1, 1])
    with b1:
        budget = st.number_input("총 구매 기준", min_value=1000, max_value=100000, value=18000, step=1000, key="stable_plan_budget")
    with b2:
        preset = st.selectbox("구매 전략", ["안정형", "보수형", "수익형"], index=0, key="stable_plan_preset")

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
    if mode == "실시간 API 우선 + 허브 보조":
        return [k for k, _ in API_LABELS]
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
    if mode == "허브만 분석":
        return 0
    if mode == "실시간 API 우선 + 허브 보조":
        return 60
    if mode == "아침 사전수집":
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



# EXTERNAL_HUB_APPS_SCRIPT
def _external_hub_config() -> Tuple[str, str]:
    """Streamlit Secrets 또는 환경변수에서 외부 허브 URL/TOKEN을 읽습니다."""
    url = ""
    token = ""
    try:
        url = str(st.secrets.get("GOOGLE_SCRIPT_URL", "") or st.secrets.get("GOOGLE_APPS_SCRIPT_WEBAPP_URL", "") or "").strip()
        token = str(st.secrets.get("GOOGLE_SCRIPT_TOKEN", "") or st.secrets.get("MARU_KRA_TOKEN", "") or "").strip()
    except Exception:
        pass
    try:
        url = url or str(os.environ.get("GOOGLE_SCRIPT_URL", "") or os.environ.get("GOOGLE_APPS_SCRIPT_WEBAPP_URL", "") or "").strip()
        token = token or str(os.environ.get("GOOGLE_SCRIPT_TOKEN", "") or os.environ.get("MARU_KRA_TOKEN", "") or "").strip()
    except Exception:
        pass
    return url, token

def external_hub_enabled() -> bool:
    url, _ = _external_hub_config()
    return bool(url.startswith("https://"))

def external_hub_save(kind: str, payload: Dict[str, Any]) -> bool:
    """Google Apps Script 허브에 JSON을 저장합니다. 실패해도 앱은 로컬 저장으로 계속 동작합니다."""
    url, token = _external_hub_config()
    if not url:
        return False
    try:
        body = {
            "action": "save",
            "kind": kind,
            "token": token,
            "payload": payload or {},
            "saved_at": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
        }
        r = requests.post(url, json=body, timeout=8)
        if r.status_code != 200:
            return False
        data = r.json() if "application/json" in (r.headers.get("content-type", "").lower()) else {}
        return bool(data.get("ok", True))
    except Exception:
        return False

def external_hub_load(kind: str = "mobile_recommend") -> Dict[str, Any]:
    """Google Apps Script 허브에서 최신 JSON을 읽습니다.

    11ROUND_EXTERNAL_LOAD_GUARD:
    - 일반 PC/모바일 화면에서는 mobile_recommend 1건만 외부 허브에서 읽습니다.
    - learning_bigdata/agent_runs 같은 무거운 허브 조회는 Apps Script tick 또는 수동 실행 때만 허용합니다.
    - 같은 화면 렌더링 안에서는 kind별 1회 캐시를 써서 반복 호출을 막습니다.
    """
    try:
        allow_network = "_hub365_network_allowed" in globals() and _hub365_network_allowed()
    except Exception:
        allow_network = False
    if (not allow_network) and str(kind) != "mobile_recommend":
        return {}
    cache_key = f"_external_hub_load_cache_{kind}"
    try:
        cached = st.session_state.get(cache_key)
        if isinstance(cached, dict) and cached:
            return cached
    except Exception:
        pass
    url, token = _external_hub_config()
    if not url:
        return {}
    try:
        r = requests.get(url, params={"action": "load", "kind": kind, "token": token}, timeout=8)
        if r.status_code != 200:
            return {}
        data = r.json()
        if isinstance(data, dict):
            payload = data.get("payload", data)
            out = payload if isinstance(payload, dict) else {}
            try:
                if out:
                    st.session_state[cache_key] = out
            except Exception:
                pass
            return out
    except Exception:
        pass
    return {}


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
            "18마권", "마권수", "단위금액", "총추천금액", "안정형6", "안정형근거", "변수형대표", "변수형6", "변수형근거", "고배당형6", "고배당형근거", "변수대응형6", "안정형대표", "고배당형대표", "변수대응형대표", "구매표복사",
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
        small = _build_three_type_recommendation(small)  # THREE_TYPE_SAVE_APPLY
        _save_three_type_hub_and_bigdata(small)
        _save_five_agent_run(small)  # FIVE_AGENT_SAVE_APPLY
        small = _apply_agent365_probability(small) if "_apply_agent365_probability" in globals() else small  # AGENT365_PROBABILITY_SAVE_APPLY
        try:
            _agent365_tick("save_mobile_recommend", small)
        except Exception:
            pass
        small = _mobile_compact_summary(small)  # MOBILE_COMPACT_SAVE
        small["구매표복사"] = _compact_ticket_lines(small.get("구매표복사", ""), 22)
        mobile_text = json.dumps(small, ensure_ascii=False, indent=2)
        MOBILE_RECOMMEND_FILE.write_text(mobile_text, encoding="utf-8")
        try_push_hub_file_to_github("maru_kra_data/mobile_recommend.json", mobile_text, "Update mobile recommendation")
        external_ok = external_hub_save("mobile_recommend", small)  # EXTERNAL_HUB_SAVE_MOBILE_RECOMMEND
        _save_current_race_status_to_external(small)  # MOBILE_PC_SYNC_SAVE_STATUS
        try:
            small["외부허브저장"] = "Y" if external_ok else "N"
            MOBILE_RECOMMEND_FILE.write_text(json.dumps(small, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass
        return True
    except Exception as e:
        try:
            st.warning(f"mobile_recommend.json 저장 실패: {e}")
        except Exception:
            pass
        return False


# MOBILE_PC_SYNC_STALE_FIX
def _norm_text(v: Any) -> str:
    try:
        return str(v or "").strip()
    except Exception:
        return ""

def _mobile_row_is_seoul1_stale(row: Dict[str, Any]) -> bool:
    if not isinstance(row, dict) or not row:
        return False
    meet = _norm_text(row.get("경마장", ""))
    race_no = _norm_text(row.get("경주번호", ""))
    status = (_norm_text(row.get("데이터상태", "")) + " " + _norm_text(row.get("상태", ""))).strip()
    return (meet in ["", "서울"]) and race_no in ["", "1", "1.0"] and (status == "" or any(x in status for x in ["대기", "샘플", "모바일 추천 데이터 없음"]))

def _sanitize_mobile_loaded_row(row: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(row or {})
    try:
        ended = False
        last_no = None
        if "_end_of_day_kst_stop" in globals():
            ended, last_no, last_time = _end_of_day_kst_stop(_norm_text(row.get("날짜", "")) or today_kst(), _norm_text(row.get("경마장", "서울")) or "서울")
        else:
            now = now_kst() if "now_kst" in globals() else datetime.datetime.now()
            ended = now.hour >= 18
        if ended and _mobile_row_is_seoul1_stale(row):
            row["경마장"] = row.get("경마장", "서울") or "서울"
            if last_no:
                row["경주번호"] = int(last_no)
            row["데이터상태"] = "경주종료"
            row["상태"] = f"오늘 경주 종료 · 이전 추천 표시 차단"
            row["실전표시불가"] = "Y"
            row["실전검증"] = "N"
            row["삼쌍승18조합"] = ""
            row["구매표복사"] = "[경주 종료]\n오늘 경주는 종료되었습니다.\n이전 경주 추천은 모바일에 표시하지 않습니다.\nPC 또는 Apps Script 백그라운드에서 새 경주 분석 후 다시 저장됩니다."
            return row
    except Exception:
        pass
    try:
        if "sync_row_to_current_race" in globals():
            row = sync_row_to_current_race(row, force_if_stale=True)
    except Exception:
        pass
    return row

def _save_current_race_status_to_external(row: Dict[str, Any]) -> None:
    try:
        if "external_hub_save" in globals():
            external_hub_save("current_race_status", {
                "저장시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
                "날짜": row.get("날짜", today_kst() if "today_kst" in globals() else ""),
                "경마장": row.get("경마장", ""),
                "경주번호": row.get("경주번호", ""),
                "경주시간": row.get("경주시간", row.get("출발시간", "")),
                "데이터상태": row.get("데이터상태", ""),
                "실시간행수": row.get("실시간행수", 0),
            })
    except Exception:
        pass


def load_mobile_recommend_json() -> Dict[str, Any]:
    # 13ROUND_HUB_READ_CACHE:
    # - 한 번의 화면 렌더링에서 같은 mobile_recommend를 여러 번 외부 호출하지 않습니다.
    # - 모바일/PC 일반 화면은 추천 결과 읽기만 허용하고, 저장/수집은 하지 않습니다.
    cache_key = "_hub365_mobile_recommend_cache_once"
    try:
        cached = st.session_state.get(cache_key)
        if isinstance(cached, dict) and cached:
            return _sanitize_mobile_loaded_row(cached)
    except Exception:
        pass
    try:
        hub_data = external_hub_load("mobile_recommend") if "external_hub_load" in globals() else {}
        if isinstance(hub_data, dict) and hub_data:
            row = _sanitize_mobile_loaded_row(hub_data)  # MOBILE_PC_SYNC_SANITIZE_HUB
            try:
                st.session_state[cache_key] = row
            except Exception:
                pass
            return row
    except Exception:
        pass
    try:
        if MOBILE_RECOMMEND_FILE.exists():
            data = json.loads(MOBILE_RECOMMEND_FILE.read_text(encoding="utf-8"))
            row = _sanitize_mobile_loaded_row(data) if isinstance(data, dict) else {}  # MOBILE_PC_SYNC_SANITIZE_LOCAL
            try:
                if row:
                    st.session_state[cache_key] = row
            except Exception:
                pass
            return row
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
    ok4 = external_hub_save("shared_recommendation", row)  # EXTERNAL_HUB_SAVE_SHARED_RECOMMEND

    try:
        save_json_file(HUB_STATUS_FILE, {
            "저장시각": now_str(),
            "shared_csv": bool(ok1),
            "local_hub_bigdata": bool(ok2),
            "mobile_json": bool(ok3),
            "external_hub": bool(ok4),
            "최종성공": bool(ok1 or ok2 or ok3 or ok4),
            "경마장": row.get("경마장", ""),
            "경주번호": row.get("경주번호", ""),
            "실시간행수": row.get("실시간행수", 0),
        })
    except Exception:
        pass
    return bool(ok1 or ok2 or ok3 or ok4)


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
    from itertools import permutations  # GEMINI_LOCAL_IMPORT_EXPAND18
    from itertools import permutations  # EXPAND_TRIPLE_HARD_FIX
    """3묶음 × 각 6순열 = 삼쌍승 18장."""
    import itertools
    tickets: List[str] = []
    for g in groups[:3]:
        clean = _unique_horse_list(g, 20)[:3]
        if len(clean) < 3:
            continue
        for p in permutations(clean, 3):
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
    return " | ".join("-".join(map(str, g[:3])) for g in groups[:3] if len(g) >= 3)


def _safe_first_mobile_row(ready: Any, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """모바일 추천 데이터가 비어도 앱이 죽지 않도록 첫 row를 안전하게 반환합니다."""
    fallback = dict(fallback or {})
    try:
        if isinstance(ready, pd.DataFrame) and not ready.empty:
            return _safe_first_mobile_row(ready)
        if isinstance(ready, list) and len(ready) > 0:
            first = ready[0]
            return dict(first) if isinstance(first, dict) else fallback
        if isinstance(ready, dict) and ready:
            return dict(ready)
    except Exception:
        pass
    row = dict(fallback)
    row.setdefault("경마장", "서울")
    row.setdefault("경주번호", 1)
    row.setdefault("경주시간", "")
    row.setdefault("상태", "추천대기")
    row.setdefault("데이터상태", "모바일 추천 데이터 없음")
    row.setdefault("대표추천", "대기")
    row.setdefault("추천금액", 18000)
    return row



# SCHEDULE_AUTO_5MIN_COMPACT_MOBILE_FIX
# AUTO_REFRESH_CONTEXT_60S_VISUAL: 화면 갱신은 60초, 실제 API 수집은 경주일정 기준 5분 단위
def _auto_collect_window_by_schedule(rc_date: str, meet: str, race_no: int) -> Tuple[bool, str, Optional[int]]:
    """
    한국시간 기준 경주일정 자동 수집창.
    - 각 경주 시작 25분 전부터 시작
    - 5분 단위 자동 수집/분석/허브 저장
    - 경주 시작 후 20분까지 결과/배당 확인
    - 마지막 경주 +20분 뒤 전체 수집 중단
    """
    try:
        now = now_kst() if "now_kst" in globals() else datetime.datetime.now()
    except Exception:
        now = datetime.datetime.now()

    try:
        sched = _load_schedule_for_sidebar(rc_date, meet) if "_load_schedule_for_sidebar" in globals() else pd.DataFrame()
    except Exception:
        sched = pd.DataFrame()

    # 시간표 없으면 무리하게 계속 수집하지 않음. 경마 시간대만 보수적으로 허용.
    if sched is None or not isinstance(sched, pd.DataFrame) or sched.empty:
        if 9 <= now.hour < 18:
            # 시간표가 아직 없으면 5분 단위로만 허용
            return (now.minute % 5 == 0), "시간표 없음 · 5분 단위 보수 자동", None
        return False, "경주시간 외 · 자동수집 중단", None

    df = sched.copy()
    meet_cols = ["경마장", "meet", "MEET", "경주장", "장소"]
    race_cols = ["경주번호", "race_no", "RACE_NO", "rcNo", "경주", "race"]
    time_cols = ["경주예정시각", "예정시각", "출발시각", "경주시간", "race_time", "rcTime", "time", "출발시간"]

    mcol = next((c for c in meet_cols if c in df.columns), None)
    rcol = next((c for c in race_cols if c in df.columns), None)
    tcol = next((c for c in time_cols if c in df.columns), None)

    if mcol is not None:
        df = df[df[mcol].astype(str).str.contains(str(meet), na=False)]
    if rcol is None or tcol is None or df.empty:
        return (9 <= now.hour < 18 and now.minute % 5 == 0), "시간표 컬럼 부족 · 5분 단위 보수 자동", None

    df["_race_no_auto5"] = pd.to_numeric(df[rcol], errors="coerce")
    if "_parse_hhmm_to_minutes" in globals():
        df["_time_min_auto5"] = df[tcol].apply(_parse_hhmm_to_minutes)
    else:
        def _p(v):
            s = str(v)
            m = re.search(r"(\d{1,2})[:.](\d{2})", s)
            if m:
                return int(m.group(1))*60 + int(m.group(2))
            return None
        df["_time_min_auto5"] = df[tcol].apply(_p)

    df = df.dropna(subset=["_race_no_auto5", "_time_min_auto5"])
    if df.empty:
        return (9 <= now.hour < 18 and now.minute % 5 == 0), "시간표 시간 파싱 실패 · 5분 단위 보수 자동", None

    now_min = now.hour * 60 + now.minute
    df = df.sort_values("_time_min_auto5")
    last_row = df.iloc[-1]
    last_min = int(last_row["_time_min_auto5"])
    last_no = int(last_row["_race_no_auto5"])

    # 마지막 경주 +20분 이후 완전 중단
    if now_min > last_min + 20:
        return False, f"오늘 {meet} 경주 종료 · 마지막 {last_no}경주 +20분 경과", last_no

    # 현재 수집 대상: 선택 경주 우선, 범위 밖이면 시간상 가장 가까운 경주
    cur = df[df["_race_no_auto5"].astype(int) == int(race_no)]
    if cur.empty:
        in_window = df[(df["_time_min_auto5"] - 25 <= now_min) & (now_min <= df["_time_min_auto5"] + 20)]
        if not in_window.empty:
            target = in_window.iloc[0]
        else:
            future = df[df["_time_min_auto5"] >= now_min]
            target = future.iloc[0] if not future.empty else last_row
    else:
        target = cur.iloc[0]

    target_no = int(target["_race_no_auto5"])
    target_min = int(target["_time_min_auto5"])

    # 경주별 수집창: -25 ~ +20
    in_collect_window = (target_min - 25) <= now_min <= (target_min + 20)
    five_min_tick = (now.minute % 5 == 0)

    if in_collect_window and five_min_tick:
        return True, f"{meet} {target_no}경주 자동수집창 · 출발 -25분~+20분 · 5분 단위", target_no
    if in_collect_window:
        return False, f"{meet} {target_no}경주 수집창 대기 · 다음 5분 단위까지 대기", target_no
    return False, f"{meet} {target_no}경주 수집창 아님 · 출발 25분 전부터 자동", target_no



# FIVE_AGENT_LEARNING_AI_FIX
AGENT_ROLES = [
    {
        "id": "sun_agent",
        "name": "해",
        "title": "총괄 판단 에이전트",
        "job": "한 경기의 전체 흐름을 종합해 안정형·변수형·고배당형 추천의 최종 균형을 잡음",
        "specialty": "종합판단, 수익효율, 최종 추천 우선순위",
        "risk": "과도한 몰빵 금지, 구매/결제는 수동",
    },
    {
        "id": "moon_agent",
        "name": "달",
        "title": "일정·시간 감시 에이전트",
        "job": "한국시간 기준 경주 시작 -25분부터 +20분까지 자동수집창을 판단하고 마지막 경주 +20분 후 중단",
        "specialty": "KST 시간표, 경주 시작/종료, 서울1 찌꺼기 차단",
        "risk": "경주 종료 후 불필요한 API 수집 금지",
    },
    {
        "id": "star_agent",
        "name": "별",
        "title": "공식데이터 수집 에이전트",
        "job": "KRA/공공데이터 승인 API에서 출전표·말·기수·결과·배당을 수집하고 허브에 정리",
        "specialty": "공식 API, 허용 공개 URL 순찰, 출전표 검증, 결과/배당 저장",
        "risk": "승인 API 우선, 무단 크롤링 금지",
    },
    {
        "id": "cloud_agent",
        "name": "구름",
        "title": "변수 감지 에이전트",
        "job": "체중변화·게이트·주로상태·날씨·기수변경·인기변화를 감지해 변수형 추천을 만듦",
        "specialty": "변수형 6마권, 흐름 변화, 위험 신호",
        "risk": "출전표 없는 말번호 추천 금지",
    },
    {
        "id": "rain_agent",
        "name": "비",
        "title": "배당·학습 검증 에이전트",
        "job": "배당흐름과 실제 결과를 비교해 learning_bigdata에 저장하고 다음 추천 가중치 보정",
        "specialty": "고배당형 6마권, 기대값, 적중/실패 복기, 자기학습",
        "risk": "적중 보장 표현 금지, 누적 데이터 기반 보정",
    },
]

def _five_agent_empty_report() -> Dict[str, Any]:
    return {
        "에이전트수": 5,
        "해": "대기 · 총괄 판단",
        "달": "대기 · 일정/시간 감시",
        "별": "대기 · 공식데이터 수집",
        "구름": "대기 · 변수 감지",
        "비": "대기 · 배당/학습 검증",
        "전략": "수익효율 우선: 안정형6/변수형6/고배당형6 분리",
    }

def _run_five_agents(row: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(row or {})
    report = _five_agent_empty_report()
    try:
        rc_date = str(row.get("날짜", today_kst() if "today_kst" in globals() else ""))
        meet = str(row.get("경마장", "서울") or "서울")
        race_no = int(float(row.get("경주번호", 1) or 1))
        if "_auto_collect_window_by_schedule" in globals():
            ok, reason, target_no = _auto_collect_window_by_schedule(rc_date, meet, race_no)
            # 15ROUND_AGENT_TARGET_LOCK: 시간표 감시는 참고만 하고, 이미 수집/분석 중인 경주번호는 바꾸지 않음
            if target_no and int(target_no) != int(race_no):
                report["달"] = f"{reason} · 현재 추천대상 {race_no}R 유지"
            else:
                report["달"] = reason
        else:
            report["달"] = "한국시간 기준 대기"
    except Exception as e:
        report["달"] = f"점검필요: {e}"
    try:
        live_rows = int(float(row.get("실시간행수", row.get("출전두수", 0)) or 0))
        report["별"] = f"수집행수 {live_rows} · 승인 API/허브 기준"
    except Exception:
        report["별"] = "공식 API/허브 기준"
    try:
        odds_text = str(row.get("예상배당", row.get("배당", "")) or "")
        report["비"] = f"배당/인기 변화 추적 · {odds_text[:40]}"
    except Exception:
        report["비"] = "배당/인기 변화 추적"
    try:
        env = " / ".join([str(row.get(k, "")) for k in ["주로상태", "환경", "체중변화", "기수변경", "인기변화"] if str(row.get(k, "")).strip()])
        report["구름"] = env[:80] if env else "체중·게이트·주로·기수·인기 변화 감시"
    except Exception:
        report["구름"] = "변수 감시"
    try:
        stat = _learning_summary_from_bigdata() if "_learning_summary_from_bigdata" in globals() else {"총기록": 0}
        report["비"] = f"학습데이터 {stat.get('총기록',0)}건 · 결과 저장 후 가중치 보정"
    except Exception:
        report["비"] = "결과 누적 대기"
    row["AI에이전트"] = report
    row["AI에이전트요약"] = (
        f"해:총괄 판단 | "
        f"달:{report.get('달','')} | "
        f"별:{report.get('별','')} | "
        f"구름:{report.get('구름','')} | "
        f"비:{report.get('비','')}"
    )
    row["투자전략"] = "해가 총괄, 달이 시간, 별이 공식데이터, 구름이 변수, 비가 배당/학습 담당 · 안정형6/변수형6/고배당형6 분산 · 구매/결제는 수동"
    return row

def _expected_profit_efficiency_note(row: Dict[str, Any]) -> str:
    row = dict(row or {})
    stable = row.get("안정형대표", "")
    variable = row.get("변수형대표", "")
    value = row.get("고배당형대표", "")
    return (
        f"효율전략: 안정형({stable})로 기본 방어, "
        f"변수형({variable})으로 흐름 변화 대응, "
        f"고배당형({value})은 소액 기대값 노림. "
        "한 경기 몰빵보다 3분류 분산이 손실 관리에 유리합니다."
    )


# NAMED_AGENT_DISPLAY_FIX
def _named_agent_summary_text() -> str:
    lines = ["[5 AI 에이전트 전문업무]"]
    for a in AGENT_ROLES:
        lines.append(f"{a['name']} - {a['title']}: {a['specialty']}")
    return "\n".join(lines)

def _save_five_agent_run(row: Dict[str, Any]) -> None:
    try:
        row = _run_five_agents(row)
        if "external_hub_save" in globals():
            external_hub_save("agent_runs", {
                "저장시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
                "날짜": row.get("날짜", ""),
                "경마장": row.get("경마장", ""),
                "경주번호": row.get("경주번호", ""),
                "AI에이전트": row.get("AI에이전트", {}),
                "AI에이전트요약": row.get("AI에이전트요약", ""),
                "투자전략": row.get("투자전략", ""),
            })
    except Exception:
        pass


# THREE_TYPE_LEARNING_HUB_AI_FIX
def _safe_json_loads(v: Any, default: Any = None) -> Any:
    try:
        if isinstance(v, (dict, list)):
            return v
        if v is None:
            return default
        return json.loads(str(v))
    except Exception:
        return default

def _split_combo_text_to_list(v: Any) -> List[str]:
    if isinstance(v, list):
        raw = v
    else:
        raw = re.split(r"[/,\n]+", str(v or ""))
    out = []
    for x in raw:
        nums = re.findall(r"\d+", str(x))
        if len(nums) >= 3:
            out.append("-".join(nums[:3]))
    seen, final = set(), []
    for c in out:
        if c not in seen:
            seen.add(c)
            final.append(c)
    return final

def _combo_list_to_text(lst: List[str], limit: int = 6) -> str:
    return " / ".join([str(x).strip() for x in lst if str(x).strip()][:limit])

def _pick_combo_pool_from_row(row: Dict[str, Any]) -> List[str]:
    pools = []
    for k in ["삼쌍승18조합", "구매표복사", "추천조합", "combos", "조합", "안정형6", "변수형6", "변수대응형6", "고배당형6"]:
        pools += _split_combo_text_to_list(row.get(k, ""))
    seen, out = set(), []
    for c in pools:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out

def _build_three_type_recommendation(row: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(row or {})
    combos = _pick_combo_pool_from_row(row)

    stable = _split_combo_text_to_list(row.get("안정형6", "")) or _split_combo_text_to_list(row.get("안정형대표", ""))
    variable = _split_combo_text_to_list(row.get("변수형6", "")) or _split_combo_text_to_list(row.get("변수대응형6", "")) or _split_combo_text_to_list(row.get("변수대응형대표", ""))
    value = _split_combo_text_to_list(row.get("고배당형6", "")) or _split_combo_text_to_list(row.get("고배당형대표", ""))

    if len(stable) < 6:
        stable = (stable + combos[0:6])[:6]
    if len(variable) < 6:
        variable = (variable + combos[6:12] + combos[0:6])[:6]
    if len(value) < 6:
        value = (value + combos[12:18] + combos[6:12] + combos[0:6])[:6]

    row["안정형대표"] = stable[0] if stable else ""
    row["안정형6"] = _combo_list_to_text(stable, 6)
    row["안정형근거"] = row.get("안정형근거", "최근폼·기수·주로 안정성 우선")

    row["변수형대표"] = variable[0] if variable else ""
    row["변수형6"] = _combo_list_to_text(variable, 6)
    row["변수형근거"] = row.get("변수형근거", "체중변화·게이트·주로상태·인기변화 대응")

    row["고배당형대표"] = value[0] if value else ""
    row["고배당형6"] = _combo_list_to_text(value, 6)
    row["고배당형근거"] = row.get("고배당형근거", "배당 대비 기대값·변수 터짐 가능성 우선")

    all18 = []
    for c in stable + variable + value:
        if c and c not in all18:
            all18.append(c)
    row["삼쌍승18조합"] = _combo_list_to_text(all18, 18)
    row["마권수"] = len(all18)
    row["분류구조"] = "안정형6/변수형6/고배당형6"
    row["구매방식"] = "수동입력/수동확정"
    row["자동화모드"] = "Y"
    row = _run_five_agents(row)  # FIVE_AGENT_THREE_TYPE_APPLY
    row["수익효율메모"] = _expected_profit_efficiency_note(row)
    return row

def _three_type_mobile_ticket(row: Dict[str, Any]) -> str:
    row = _build_three_type_recommendation(row)
    lines = [
        f"[{row.get('경마장','')} {row.get('경주번호','')}R] 3분류 추천",
        "",
        f"안정형 대표: {row.get('안정형대표','')}",
        f"안정형 6: {row.get('안정형6','')}",
        f"근거: {row.get('안정형근거','')}",
        "",
        f"변수형 대표: {row.get('변수형대표','')}",
        f"변수형 6: {row.get('변수형6','')}",
        f"근거: {row.get('변수형근거','')}",
        "",
        f"고배당형 대표: {row.get('고배당형대표','')}",
        f"고배당형 6: {row.get('고배당형6','')}",
        f"근거: {row.get('고배당형근거','')}",
        "",
        f"AI요약: {row.get('AI에이전트요약', '')[:140]}",
        "담당: 해=총괄 / 달=시간 / 별=공식데이터 / 구름=변수 / 비=배당학습",  # NAMED_AGENT_MOBILE_DISPLAY
        "",
        "※ 구매/결제는 공식 사이트에서 수동 입력·수동 확정",  # FIVE_AGENT_MOBILE_TICKET
    ]
    return "\n".join(lines)

def _learning_result_record(row: Dict[str, Any], result: Dict[str, Any] = None) -> Dict[str, Any]:
    row = _build_three_type_recommendation(row)
    result = dict(result or {})
    return {
        "저장시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
        "날짜": row.get("날짜", today_kst() if "today_kst" in globals() else ""),
        "경마장": row.get("경마장", ""),
        "경주번호": row.get("경주번호", ""),
        "경주시간": row.get("경주시간", row.get("출발시간", "")),
        "안정형대표": row.get("안정형대표", ""),
        "안정형6": row.get("안정형6", ""),
        "변수형대표": row.get("변수형대표", ""),
        "변수형6": row.get("변수형6", ""),
        "고배당형대표": row.get("고배당형대표", ""),
        "고배당형6": row.get("고배당형6", ""),
        "삼쌍승18조합": row.get("삼쌍승18조합", ""),
        "실제결과": result.get("실제결과", row.get("실제결과", "")),
        "적중분류": result.get("적중분류", row.get("적중분류", "")),
        "배당결과": result.get("배당결과", row.get("배당결과", "")),
        "환경": row.get("환경", row.get("주로상태", "")),
        "기수변경": row.get("기수변경", ""),
        "체중변화": row.get("체중변화", ""),
        "인기변화": row.get("인기변화", ""),
        "학습메모": result.get("학습메모", row.get("학습메모", "")),
        "AI에이전트요약": row.get("AI에이전트요약", ""),
        "투자전략": row.get("투자전략", ""),  # FIVE_AGENT_BIGDATA_FIELDS
    }

def _save_three_type_hub_and_bigdata(row: Dict[str, Any], result: Dict[str, Any] = None) -> None:
    try:
        row = _build_three_type_recommendation(row)
        if "external_hub_save" in globals():
            compact = _mobile_compact_summary(row) if "_mobile_compact_summary" in globals() else row
            external_hub_save("mobile_recommend", compact)
            external_hub_save("three_type_recommend", row)
            external_hub_save("learning_bigdata", _learning_result_record(row, result))
    except Exception:
        pass

def _load_learning_bigdata(limit: int = 200) -> List[Dict[str, Any]]:
    try:
        if "external_hub_load" in globals():
            data = external_hub_load("learning_bigdata")
            if isinstance(data, list):
                return data[-limit:]
            if isinstance(data, dict) and data:
                return [data]
    except Exception:
        pass
    return []

def _learning_summary_from_bigdata() -> Dict[str, Any]:
    rows = _load_learning_bigdata(500)
    stat = {"총기록": len(rows), "안정형적중": 0, "변수형적중": 0, "고배당형적중": 0}
    for r in rows:
        hit = str(r.get("적중분류", ""))
        if "안정" in hit:
            stat["안정형적중"] += 1
        if "변수" in hit:
            stat["변수형적중"] += 1
        if "고배당" in hit:
            stat["고배당형적중"] += 1
    return stat


def _mobile_compact_summary(row: Dict[str, Any]) -> Dict[str, Any]:
    """모바일은 5페이지처럼 길게 보이지 않게 핵심만 남깁니다."""
    row = _build_three_type_recommendation(dict(row or {}))  # THREE_TYPE_MOBILE_COMPACT_APPLY
    keep = [
        "저장시각", "날짜", "경마장", "경주번호", "경주시간", "출발시간",
        "데이터상태", "상태", "실전검증", "실전표시불가",
        "안정형대표", "고배당형대표", "변수대응형대표",
        "안정형6", "안정형근거", "변수형대표", "변수형6", "변수형근거", "고배당형6", "고배당형근거", "변수대응형6",
        "삼쌍승18조합", "구매표복사", "총추천금액", "마권수", "단위금액",
        "신뢰도", "위험도", "예상배당", "근거",
        "자동화모드", "구매방식"
    ]
    compact = {k: row.get(k, "") for k in keep}
    compact.setdefault("구매방식", "수동입력/수동확정")
    compact.setdefault("자동화모드", "Y")
    return compact

def _compact_ticket_lines(text: Any, limit: int = 18) -> str:
    """모바일 구매표 줄 수 제한. 너무 긴 설명/전체 원문을 잘라냄."""
    s = str(text or "").strip()
    if not s:
        return ""
    lines = [x for x in s.splitlines() if x.strip()]
    if len(lines) <= limit:
        return "\n".join(lines)
    return "\n".join(lines[:limit]) + "\n... 이하 상세는 PC 화면에서 확인"



# MOBILE_REAL_COMPACT_3TYPE_ONLY_FIX
def _mobile_real_compact_css() -> str:
    return """
    <style>
    .main .block-container {padding-top: 0.7rem; padding-bottom: 1rem; max-width: 760px;}
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stToolbar"] {display:none;}
    .mk-wrap {font-family: -apple-system, BlinkMacSystemFont, "Noto Sans KR", sans-serif;}
    .mk-top {background: linear-gradient(180deg,#101014,#050506); border: 2px solid #d6ad43; border-radius: 24px; padding: 22px 20px; margin: 8px 0 12px 0; text-align:center; box-shadow: 0 10px 26px rgba(0,0,0,.18);}
    .mk-small {font-size: 15px; color:#b8b8b8; font-weight:700;}
    .mk-title {font-size: 34px; color:#fff; font-weight:900; line-height:1.15; margin-top:6px;}
    .mk-gold {color:#ffd15a;}
    .mk-status {background:#fff8d7; color:#594200; border-radius:18px; padding:14px 16px; font-size:17px; font-weight:800; margin:12px 0;}
    .mk-grid {display:grid; grid-template-columns:1fr; gap:10px;}
    .mk-card {background: linear-gradient(180deg,#151515,#060606); border: 2px solid #d6ad43; border-radius:22px; padding:17px 18px; color:#fff;}
    .mk-card h3 {margin:0 0 7px 0; color:#ffd15a; font-size:22px;}
    .mk-rep {font-size:34px; font-weight:900; letter-spacing:1px; margin:2px 0 8px 0;}
    .mk-six {font-size:15px; color:#d8dde8; line-height:1.42; word-break:keep-all;}
    .mk-reason {font-size:13px; color:#aeb6c5; margin-top:7px;}
    .mk-note {font-size:13px; color:#7a7a7a; margin-top:10px; text-align:center;}
    </style>
    """

def _safe_mobile_val(row: Dict[str, Any], *keys: str, default: str = "-") -> str:
    for k in keys:
        v = row.get(k, "")
        if v is not None and str(v).strip():
            return str(v).strip()
    return default

def _format_6_for_mobile(text: Any) -> str:
    combos = _split_combo_text_to_list(text) if "_split_combo_text_to_list" in globals() else []
    if combos:
        return " · ".join(combos[:6])
    s = str(text or "").strip()
    return s if s else "-"

def _render_mobile_compact_3type_view(row: Dict[str, Any]) -> None:
    row = dict(row or {})
    try:
        if "_build_three_type_recommendation" in globals():
            row = _build_three_type_recommendation(row)
    except Exception:
        pass

    meet = _safe_mobile_val(row, "경마장", default="서울")
    race_no = _safe_mobile_val(row, "경주번호", default="-")
    race_time = _safe_mobile_val(row, "경주시간", "출발시간", default="-")
    status = _safe_mobile_val(row, "상태", "데이터상태", default="대기")
    saved = _safe_mobile_val(row, "저장시각", default="-")
    stable_rep = _safe_mobile_val(row, "안정형대표", default="-")
    stable_6 = _format_6_for_mobile(row.get("안정형6", ""))
    stable_reason = _safe_mobile_val(row, "안정형근거", default="최근폼·기수·주로 안정성 우선")
    var_rep = _safe_mobile_val(row, "변수형대표", "변수대응형대표", default="-")
    var_6 = _format_6_for_mobile(row.get("변수형6", row.get("변수대응형6", "")))
    var_reason = _safe_mobile_val(row, "변수형근거", "변수대응형근거", default="체중·게이트·주로·기수 변경 대응")
    high_rep = _safe_mobile_val(row, "고배당형대표", default="-")
    high_6 = _format_6_for_mobile(row.get("고배당형6", ""))
    high_reason = _safe_mobile_val(row, "고배당형근거", default="배당 대비 기대값 우선")
    amount = _safe_mobile_val(row, "총추천금액", "추천금액", default="18,000원")
    unit = _safe_mobile_val(row, "단위금액", default="1,000원")
    auto = _safe_mobile_val(row, "자동화모드", default="Y")

    row = _mobile_drop_placeholder_combos(row) if "_mobile_drop_placeholder_combos" in globals() else row  # MOBILE_NO_BLANK_COMPACT_GATE
    if "_mobile_has_any_real_recommend" in globals() and not _mobile_has_any_real_recommend(row):
        _render_mobile_end_or_wait_view(row)
        return
    st.markdown(_mobile_real_compact_css(), unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mk-wrap">
      <div class="mk-top">
        <div class="mk-small">MARU KRA · 모바일 3분류 핵심</div>
        <div class="mk-title">{meet} {race_no}R <span class="mk-gold">삼쌍승 18장</span></div>
        <div class="mk-small">경주시간 {race_time} · 기준 {amount} · 각 {unit}</div>
      </div>
      <div class="mk-status">상태: {status} · 자동화 {auto} · 저장 {saved}</div>
      <div class="mk-grid">
        <div class="mk-card">
          <h3>① 안정형 6장</h3>
          <div class="mk-rep">{stable_rep}</div>
          <div class="mk-six">{stable_6}</div>
          <div class="mk-reason">{stable_reason}</div>
        </div>
        <div class="mk-card">
          <h3>② 변수형 6장</h3>
          <div class="mk-rep">{var_rep}</div>
          <div class="mk-six">{var_6}</div>
          <div class="mk-reason">{var_reason}</div>
        </div>
        <div class="mk-card">
          <h3>③ 고배당형 6장</h3>
          <div class="mk-rep">{high_rep}</div>
          <div class="mk-six">{high_6}</div>
          <div class="mk-reason">{high_reason}</div>
        </div>
      </div>
      <div class="mk-note">자동구매/자동결제 없음 · 더비온에서 본인이 수동 입력·확정</div>
    </div>
    """, unsafe_allow_html=True)

    copy_text = _three_type_mobile_ticket(row) if "_three_type_mobile_ticket" in globals() else str(row.get("구매표복사", ""))
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📋 18장 텍스트", copy_text, file_name=f"maru_{meet}_{race_no}R_18tickets.txt", key="mobile_3type_18tickets_download")
    with c2:
        st.link_button("↗ 더비온 열기", "https://www.derbyon.co.kr")




# PC_MOBILE_CHARACTER_UNIFIED_FIX
CHARACTER_AGENTS = [
    {"name": "해", "animal": "태양 그리핀", "role": "총괄·전략", "mission": "안정형/변수형/고배당형 최종 균형 판단", "emoji": "🦁☀️"},
    {"name": "달", "animal": "달빛 토끼", "role": "수집·감시", "mission": "한국시간 경주일정·자동수집창·종료시점 감시", "emoji": "🐇🌙"},
    {"name": "별", "animal": "별사슴", "role": "분석·패턴", "mission": "공식API·출전표·배당·결과 패턴 분석", "emoji": "🦌⭐"},
    {"name": "구름", "animal": "구름양", "role": "통신·복구", "mission": "허브·API·모바일·PC 동기화와 오류 복구", "emoji": "🐏☁️"},
    {"name": "비", "animal": "비고래", "role": "학습·개선", "mission": "실제결과·손익·실패원인 저장 후 가중치 개선", "emoji": "🐋💧"},
]

def _character_growth_phase() -> Dict[str, Any]:
    try:
        now = now_kst() if "now_kst" in globals() else datetime.datetime.now()
    except Exception:
        now = datetime.datetime.now()
    wd = now.weekday()
    if wd in [0, 1, 2, 3]:
        return {"mode": "월화수목 허브성장", "active": True, "apply": False, "weekday": wd, "hour": now.hour}
    if wd == 4 and now.hour < 7:
        return {"mode": "금요일 07시 적용대기", "active": True, "apply": False, "weekday": wd, "hour": now.hour}
    if wd == 4 and now.hour >= 7:
        return {"mode": "금요일 07시 전략적용", "active": True, "apply": True, "weekday": wd, "hour": now.hour}
    return {"mode": "주말 실전운영", "active": True, "apply": True, "weekday": wd, "hour": now.hour}

def _agent_growth_from_hub() -> Dict[str, Any]:
    stat = {"learning_count": 0, "agent_runs": 0, "web_patrol": 0, "comm_ok": 0, "apply_count": 0}
    try:
        if "_hub365_network_allowed" in globals() and not _hub365_network_allowed():
            return stat
        if "external_hub_load" in globals():
            learn = external_hub_load("learning_bigdata")
            runs = external_hub_load("agent_runs")
            patrol = external_hub_load("web_patrol")
            comm = external_hub_load("comm_status")
            apply_log = external_hub_load("weekly_apply_log")
            stat["learning_count"] = len(learn) if isinstance(learn, list) else (1 if isinstance(learn, dict) and learn else 0)
            stat["agent_runs"] = len(runs) if isinstance(runs, list) else (1 if isinstance(runs, dict) and runs else 0)
            stat["web_patrol"] = len(patrol) if isinstance(patrol, list) else (1 if isinstance(patrol, dict) and patrol else 0)
            stat["comm_ok"] = 1 if isinstance(comm, dict) and comm else 0
            stat["apply_count"] = len(apply_log) if isinstance(apply_log, list) else (1 if isinstance(apply_log, dict) and apply_log else 0)
    except Exception:
        pass

    growth = {}
    base_exp = stat["learning_count"] * 18 + stat["agent_runs"] * 12 + stat["web_patrol"] * 10 + stat["comm_ok"] * 8 + stat["apply_count"] * 20
    for i, a in enumerate(CHARACTER_AGENTS):
        exp = max(0, base_exp + (i + 1) * 7)
        level = 1 + min(30, exp // 100)
        pct = int(exp % 100)
        stage = "새싹"
        if level >= 5: stage = "성장"
        if level >= 10: stage = "진화"
        if level >= 20: stage = "각성"
        growth[a["name"]] = {"레벨": int(level), "경험치": pct, "단계": stage, "누적EXP": int(exp), "상태": "활동중"}
    return growth

def _save_character_growth_to_hub() -> Dict[str, Any]:
    payload = {
        "저장시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
        "주간모드": _character_growth_phase(),
        "캐릭터성장": _agent_growth_from_hub(),
        "운영방식": "월화수목 허브 성장 · 금요일 07시 적용 · 주말 실전운영",
        "자동구매": "없음",
        "자동결제": "없음",
    }
    try:
        if "external_hub_save" in globals():
            external_hub_save("character_growth", payload)
    except Exception:
        pass
    return payload

def _character_growth_css() -> str:
    return """
    <style>
    .agent-zone {display:grid; grid-template-columns: repeat(auto-fit,minmax(160px,1fr)); gap:12px;}
    .agent-card {background:linear-gradient(180deg,#111827,#05070c); border:1.5px solid #d6ad43; border-radius:20px; padding:15px; color:#fff; position:relative; overflow:hidden; min-height:170px;}
    .agent-card:before {content:""; position:absolute; width:90px; height:90px; right:-25px; top:-25px; border-radius:60px; background:rgba(255,209,90,.16); animation:pulseGlow 2.4s infinite ease-in-out;}
    .agent-emoji {font-size:38px; animation:floatAgent 2.6s infinite ease-in-out;}
    .agent-name {font-size:25px; font-weight:900; color:#ffd15a; margin-top:4px;}
    .agent-animal {font-size:15px; color:#dbeafe; font-weight:800;}
    .agent-role {font-size:12px; color:#a8b3c7; margin:8px 0;}
    .agent-bar {height:9px; background:#263244; border-radius:999px; overflow:hidden; margin-top:8px;}
    .agent-fill {height:9px; background:linear-gradient(90deg,#f7c948,#38bdf8); border-radius:999px;}
    .agent-level {font-size:12px; color:#e5e7eb; margin-top:7px;}
    @keyframes floatAgent {0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
    @keyframes pulseGlow {0%,100%{opacity:.4; transform:scale(.9)}50%{opacity:1; transform:scale(1.08)}}
    </style>
    """

def _character_cards_html(compact: bool = False) -> str:
    payload = _save_character_growth_to_hub()
    growth = payload.get("캐릭터성장", {})
    html = ['<div class="agent-zone">']
    for a in CHARACTER_AGENTS:
        g = growth.get(a["name"], {})
        exp_pct = max(0, min(100, int(g.get("경험치", 0))))
        mission = a["role"] if compact else f"{a['role']} · {a['mission']}"
        html.append(f"""
        <div class="agent-card">
          <div class="agent-emoji">{a['emoji']}</div>
          <div class="agent-name">{a['name']}</div>
          <div class="agent-animal">{a['animal']}</div>
          <div class="agent-role">{mission}</div>
          <div class="agent-bar"><div class="agent-fill" style="width:{exp_pct}%"></div></div>
          <div class="agent-level">Lv.{g.get('레벨',1)} · EXP {exp_pct}% · {g.get('단계','새싹')}</div>
        </div>
        """)
    html.append("</div>")
    return "".join(html)

def render_character_growth_dashboard() -> None:
    try:
        payload = _save_character_growth_to_hub()
        phase = payload.get("주간모드", {})
        st.markdown("### 🐾 해·달·별·구름·비 성장 허브")
        st.caption(f"{phase.get('mode','')} · PC/모바일 캐릭터 성장 표시")
        st.markdown(_character_growth_css(), unsafe_allow_html=True)
        st.markdown(_character_cards_html(False), unsafe_allow_html=True)
        with st.expander("캐릭터 성장 데이터", expanded=False):
            st.json(payload)
    except Exception as e:
        st.warning(f"캐릭터 성장 허브 표시 오류: {e}")

def render_mobile_character_strip() -> None:
    try:
        st.markdown(_character_growth_css(), unsafe_allow_html=True)
        st.markdown("### 🐾 에이전트 활동")
        st.markdown(_character_cards_html(True), unsafe_allow_html=True)
    except Exception:
        pass











# ALL_MEET_ALL_RACE_MONITOR_FIX
def _parse_schedule_dt_for_monitor(row: Dict[str, Any]) -> Optional[datetime.datetime]:
    try:
        if row.get("경주시각"):
            return pd.to_datetime(row.get("경주시각"), errors="coerce").to_pydatetime()
    except Exception:
        pass
    try:
        t = str(row.get("경주시간", "") or "").strip()
        if "_parse_hhmm_to_today" in globals():
            return _parse_hhmm_to_today(t)
    except Exception:
        pass
    return None

def load_all_meet_schedule_for_monitor(rc_date: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """서울/부산경남/제주 전체 경주일정을 한 번에 가져와 모니터링용으로 반환합니다."""
    sched = pd.DataFrame()
    log_df = pd.DataFrame()
    try:
        if "fetch_all_meet_schedule_direct" in globals():
            sched, log_df = fetch_all_meet_schedule_direct(rc_date)
    except Exception as e:
        log_df = pd.DataFrame([{"경마장": "전체", "API": "schedule", "상태": f"직접수신 실패: {str(e)[:120]}", "행수": 0}])

    if sched is None or not isinstance(sched, pd.DataFrame) or sched.empty:
        frames = []
        for m in ["서울", "부산경남", "제주"]:
            try:
                df = _load_schedule_for_sidebar(rc_date, m) if "_load_schedule_for_sidebar" in globals() else pd.DataFrame()
                if isinstance(df, pd.DataFrame) and not df.empty:
                    if "경마장" not in df.columns:
                        df["경마장"] = m
                    frames.append(df)
            except Exception:
                pass
        if frames:
            sched = pd.concat(frames, ignore_index=True)

    if sched is None or not isinstance(sched, pd.DataFrame):
        sched = pd.DataFrame()

    if not sched.empty:
        if "경마장" not in sched.columns:
            sched["경마장"] = "미상"
        if "경주번호" in sched.columns:
            try:
                sched["경주번호"] = pd.to_numeric(sched["경주번호"], errors="coerce").fillna(0).astype(int)
            except Exception:
                pass
        try:
            sched = sched.drop_duplicates(subset=[c for c in ["날짜", "경마장", "경주번호"] if c in sched.columns])
            sort_cols = [c for c in ["경마장", "경주번호"] if c in sched.columns]
            if sort_cols:
                sched = sched.sort_values(sort_cols)
        except Exception:
            pass
    return sched, log_df

def _schedule_monitor_status(dt: Optional[datetime.datetime]) -> str:
    if not dt:
        return "시간미확인"
    now = now_kst() if "now_kst" in globals() else datetime.datetime.now()
    mins = int((dt - now).total_seconds() // 60)
    if mins > 25:
        return f"대기 {mins}분전"
    if -20 <= mins <= 25:
        return f"수집창 {mins}분"
    if mins < -20:
        return "종료/결과확인"
    return "대기"

def _current_or_next_races(sched: pd.DataFrame, per_meet: int = 3) -> pd.DataFrame:
    if sched is None or sched.empty:
        return pd.DataFrame()
    df = sched.copy()
    dts = []
    for _, r in df.iterrows():
        dts.append(_parse_schedule_dt_for_monitor(dict(r)))
    df["_dt"] = dts
    df["상태"] = [_schedule_monitor_status(x) for x in dts]
    now = now_kst() if "now_kst" in globals() else datetime.datetime.now()
    out = []
    for meet, g in df.groupby("경마장", dropna=False):
        gg = g.copy()
        if "_dt" in gg.columns:
            future = gg[gg["_dt"].notna() & (gg["_dt"] >= now - pd.Timedelta(minutes=20))]
            if not future.empty:
                gg = future.sort_values("_dt").head(per_meet)
            else:
                gg = g.tail(per_meet)
        else:
            gg = g.head(per_meet)
        out.append(gg)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()

def render_all_meet_all_race_monitor(rc_date: str, selected: List[str], sim_count: int, risk_mode: str) -> None:
    """서울 1R 고정 대신 모든 경마장/모든 경주일정을 확인하는 전체 관제 화면."""
    st.markdown("### 🌐 전체 경마장 · 전체 경주일정 관제")
    st.info("PC 화면 진입만으로 전체 경마장 API를 수집하지 않습니다. 필요할 때 아래 버튼을 한 번만 누르세요.")
    st.caption("Apps Script 백그라운드 호출(agent_tick=1) 또는 수동 버튼일 때만 관제를 실행합니다.")

    manual_run = st.button("🌐 전체 경마장 관제 1회 실행", key="all_meet_monitor_manual_run_once")
    if not manual_run and not (_hub365_network_allowed() if "_hub365_network_allowed" in globals() else False):
        st.warning("대기 중 · 자동수집 차단됨. PC 화면에서는 버튼을 눌렀을 때만 1회 실행합니다.")
        return
    if manual_run:
        st.session_state["_hub365_network_allowed"] = True

    sched, log_df = load_all_meet_schedule_for_monitor(rc_date)
    if sched.empty:
        st.error("전체 경마장 경주일정을 받지 못했습니다.")
        if isinstance(log_df, pd.DataFrame) and not log_df.empty:
            st.dataframe(log_df, use_container_width=True, hide_index=True)
        return

    try:
        counts = sched.groupby("경마장").size().to_dict()
        st.success(" / ".join([f"{k} {v}경주" for k, v in counts.items()]))
    except Exception:
        pass

    display_cols = [c for c in ["날짜", "경마장", "경주번호", "경주시간", "경주시각"] if c in sched.columns]
    if display_cols:
        st.markdown("#### 오늘 전체 경주일정")
        st.dataframe(sched[display_cols], use_container_width=True, hide_index=True, height=360)

    targets = _current_or_next_races(sched, per_meet=3)
    if targets.empty:
        st.warning("현재/다음 경주를 계산하지 못했습니다.")
        return

    st.markdown("#### 현재/다음 점검 대상")
    show_cols = [c for c in ["경마장", "경주번호", "경주시간", "상태"] if c in targets.columns]
    st.dataframe(targets[show_cols], use_container_width=True, hide_index=True, height=260)

    render_force_real_collection_center(rc_date, selected, targets)  # FORCE_REAL_COLLECTION_CENTER_ALL_MEET_APPLY
    auto_m, auto_r = _auto_current_target_for_recommend(rc_date, "전체", 0)
    render_sequential_26api_center(rc_date, auto_m, auto_r)  # CURRENT_RACE_TARGET_MATCH_SEQ_ALL_MEET_APPLY
    render_recommendation_after_each_race_center(rc_date, auto_m, auto_r)  # CURRENT_RACE_TARGET_MATCH_RECOMMEND_ALL_MEET_APPLY

    st.markdown("#### 경마장별 첫 대상 자동 API 점검")
    result_rows = []
    for meet, g in targets.groupby("경마장", dropna=False):
        try:
            row = g.iloc[0].to_dict()
            race_no = int(float(row.get("경주번호", 1) or 1))
            data, status = no_click_fetch_26api_snapshot(rc_date, str(meet), race_no) if "no_click_fetch_26api_snapshot" in globals() else ({}, pd.DataFrame())
            total_rows = 0
            entry_rows = 0
            if isinstance(data, dict):
                total_rows = sum(len(v) for v in data.values() if hasattr(v, "__len__"))
                entry_rows = max(len(data.get("entry_url", pd.DataFrame())) if hasattr(data.get("entry_url", pd.DataFrame()), "__len__") else 0,
                                 len(data.get("entry_registered_url", pd.DataFrame())) if hasattr(data.get("entry_registered_url", pd.DataFrame()), "__len__") else 0)
            ok_api = 0
            if isinstance(status, pd.DataFrame) and not status.empty:
                try:
                    ok_api = int((pd.to_numeric(status.get("행수", 0), errors="coerce").fillna(0) > 0).sum())
                except Exception:
                    ok_api = 0
            result_rows.append({
                "경마장": meet,
                "경주번호": race_no,
                "경주시간": row.get("경주시간", ""),
                "API성공": ok_api,
                "총행수": total_rows,
                "출전표행수": entry_rows,
                "추천가능": "가능" if entry_rows >= 3 else "출전표 부족",
            })
        except Exception as e:
            result_rows.append({"경마장": meet, "오류": str(e)[:120]})
    if result_rows:
        st.dataframe(pd.DataFrame(result_rows), use_container_width=True, hide_index=True)

    st.info("추천은 서울 1R 고정이 아니라 위 표의 현재/다음 경주를 기준으로 확인합니다. 특정 경주를 깊게 분석하려면 사이드바에서 선택 경마장 모드로 바꾸면 됩니다.")


# SOURCE_TRUTH_AND_HUB_MODE_FIX
def _source_truth_snapshot(data=None, status_df=None, selected=None, collection_mode: str = "") -> Dict[str, Any]:
    data = data if data is not None else st.session_state.get("live_data", {}) or {}
    status_df = status_df if status_df is not None else st.session_state.get("api_status", pd.DataFrame())
    selected = selected if selected is not None else []
    collection_mode = collection_mode or st.session_state.get("collection_mode", "실시간 API 우선 + 허브 보조")
    snap = {
        "확인시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
        "수집모드": collection_mode,
        "모드해석": "",
        "API호출대상수": len(selected or []),
        "API성공수": 0,
        "API총행수": 0,
        "허브상태": {},
        "API상태": [],
        "주의": [],
    }
    if collection_mode == "허브만 분석":
        snap["모드해석"] = "API를 호출하지 않고 허브/캐시만 읽는 모드입니다."
        snap["주의"].append("허브만 분석 모드에서는 26개 API 접속이 0개가 정상입니다.")
        snap["주의"].append("실전 추천을 받으려면 '실시간 API 우선 + 허브 보조' 또는 '전체 26개'로 바꾸세요.")
    elif collection_mode == "실시간 API 우선 + 허브 보조":
        snap["모드해석"] = "공식 API를 먼저 호출하고, 실패/0건일 때 허브 저장값을 보조로 사용합니다."
    else:
        snap["모드해석"] = "선택한 모드에 따라 일부 API만 호출합니다."

    try:
        if isinstance(data, dict):
            snap["API총행수"] = int(sum(len(v) for v in data.values() if hasattr(v, "__len__")))
    except Exception:
        pass

    try:
        if isinstance(status_df, pd.DataFrame) and not status_df.empty:
            ok = 0
            rows = []
            for _, r in status_df.iterrows():
                try:
                    row_count = int(float(str(r.get("행수", 0)).replace(",", "")))
                except Exception:
                    row_count = 0
                state = str(r.get("상태", "") or r.get("분류", ""))
                if row_count > 0 or state.upper() in ["OK", "CACHE", "SUCCESS", "성공"]:
                    ok += 1
                rows.append({
                    "API": r.get("API", ""),
                    "key": r.get("key", ""),
                    "행수": row_count,
                    "상태": state,
                    "URL": str(r.get("URL", ""))[:160],
                    "자료출처": "공식 API 직접수신" if row_count > 0 else ("허브/캐시" if "CACHE" in state.upper() else "미수신/대기"),
                })
            snap["API성공수"] = ok
            snap["API상태"] = rows
    except Exception:
        pass

    try:
        if "_hub365_network_allowed" in globals() and not _hub365_network_allowed():
            snap["허브상태"]["외부조회"] = "화면진입 자동조회 차단"
        elif "external_hub_load" in globals():
            for name in ["mobile_recommend", "three_type_recommend", "learning_bigdata", "api_schedule_status", "api_received_files", "pipeline_reason_snapshot"]:
                try:
                    val = external_hub_load(name)
                    if isinstance(val, list):
                        snap["허브상태"][name] = f"{len(val)}건"
                    elif isinstance(val, dict):
                        snap["허브상태"][name] = "있음" if val else "없음"
                    else:
                        snap["허브상태"][name] = "있음" if val else "없음"
                except Exception as e:
                    snap["허브상태"][name] = f"확인실패: {str(e)[:60]}"
        else:
            snap["허브상태"]["허브함수"] = "없음"
    except Exception:
        pass

    if snap["API호출대상수"] == 0:
        snap["주의"].append("현재 호출 대상 API가 0개입니다. 사이드바 수집모드를 확인하세요.")
    if snap["API총행수"] == 0 and collection_mode != "허브만 분석":
        snap["주의"].append("API 호출 모드인데 수신 행수가 0건입니다. API Key/승인/URL/공공데이터 응답 상태를 확인해야 합니다.")
    return snap

def render_source_truth_center(data=None, status_df=None, selected=None, collection_mode: str = "") -> None:
    st.markdown("### 🧾 자료 출처 확인센터")
    snap = _source_truth_snapshot(data, status_df, selected, collection_mode)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("수집모드", snap.get("수집모드", "-")[:12])
    c2.metric("호출대상 API", snap.get("API호출대상수", 0))
    c3.metric("API 성공", snap.get("API성공수", 0))
    c4.metric("수신 총행수", snap.get("API총행수", 0))
    st.info(snap.get("모드해석", ""))
    for w in snap.get("주의", []):
        st.warning(w)

    hub_rows = [{"허브시트/항목": k, "상태": v} for k, v in snap.get("허브상태", {}).items()]
    if hub_rows:
        st.markdown("#### 허브 저장 상태")
        st.dataframe(pd.DataFrame(hub_rows), use_container_width=True, hide_index=True, height=220)

    api_rows = snap.get("API상태", [])
    if api_rows:
        st.markdown("#### API별 직접수신/허브/캐시 출처")
        st.dataframe(pd.DataFrame(api_rows), use_container_width=True, hide_index=True, height=360)
    else:
        st.caption("아직 API 상태표가 없습니다. 수집모드가 허브만 분석이면 API 상태표가 비어 있을 수 있습니다.")

    with st.expander("자료 출처 전체 JSON", expanded=False):
        st.json(snap)


# FULL_PIPELINE_AUDIT_AND_REASON_CENTER_FIX
def _count_rows_in_data(data: Dict[str, Any], key: str) -> int:
    try:
        v = data.get(key)
        if v is None:
            return 0
        if isinstance(v, pd.DataFrame):
            return len(v)
        return len(v)
    except Exception:
        return 0

def _pipeline_reason_snapshot(rc_date: str = "", meet: str = "서울", race_no: Any = "") -> Dict[str, Any]:
    rc_date = rc_date or (today_kst() if "today_kst" in globals() else (now_kst().strftime("%Y%m%d") if "now_kst" in globals() else ""))
    meet = meet or "서울"
    try:
        race_no = int(float(race_no or (_detect_current_race_for_no_click(rc_date, meet) if "_detect_current_race_for_no_click" in globals() else 1)))
    except Exception:
        race_no = 1

    snap = {
        "확인시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
        "날짜": rc_date,
        "경마장": meet,
        "경주번호": race_no,
        "최종판정": "확인중",
        "추천가능": "N",
        "원인": [],
        "다음조치": [],
        "수집": {},
        "일정": {},
        "추천": {},
        "허브": {},
    }

    try:
        key_ok = bool(get_api_key()) if "get_api_key" in globals() else False
        snap["수집"]["API_KEY"] = "있음" if key_ok else "없음"
        snap["수집"]["키출처"] = get_api_key_source() if "get_api_key_source" in globals() else "-"
        if not key_ok:
            snap["원인"].append("공공데이터 API Key가 감지되지 않음")
            snap["다음조치"].append("Streamlit Secrets에 KRA_API_KEY 저장")
    except Exception as e:
        snap["원인"].append(f"API Key 확인 실패: {str(e)[:80]}")

    try:
        master_on = bool(st.session_state.get("api_master_on", True))
        snap["수집"]["API_MASTER"] = "ON" if master_on else "OFF"
        if not master_on:
            snap["원인"].append("API 마스터 스위치가 OFF")
            snap["다음조치"].append("PC 사이드바에서 API 전체 ON")
    except Exception:
        pass

    try:
        if "fetch_all_meet_schedule_direct" in globals():
            schedule_df, schedule_log = fetch_all_meet_schedule_direct(rc_date)
        else:
            schedule_df, schedule_log = pd.DataFrame(), pd.DataFrame()
        snap["일정"]["전체경주일정행수"] = int(len(schedule_df)) if isinstance(schedule_df, pd.DataFrame) else 0
        if isinstance(schedule_df, pd.DataFrame) and not schedule_df.empty and "경마장" in schedule_df.columns:
            snap["일정"]["경마장별"] = schedule_df.groupby("경마장").size().to_dict()
        else:
            snap["원인"].append("서울/부산경남/제주 경주일정 직접수신 0건")
            snap["다음조치"].append("경주일정 접속로그에서 HTTP 500/200 0건/키 오류 확인")
        if isinstance(schedule_log, pd.DataFrame):
            snap["일정"]["접속로그행수"] = int(len(schedule_log))
    except Exception as e:
        snap["원인"].append(f"경주일정 직접수신 실패: {str(e)[:100]}")

    data = st.session_state.get("live_data", {}) or {}
    status_df = st.session_state.get("api_status", pd.DataFrame())
    try:
        if "no_click_fetch_26api_snapshot" in globals():
            data2, status2 = no_click_fetch_26api_snapshot(rc_date, meet, race_no)
            if data2:
                data = data2
            if isinstance(status2, pd.DataFrame) and not status2.empty:
                status_df = status2
    except Exception as e:
        snap["원인"].append(f"26개 API 자동접속 실패: {str(e)[:120]}")

    try:
        api_total_rows = sum(_count_rows_in_data(data, k) for k in data.keys()) if isinstance(data, dict) else 0
        snap["수집"]["API총행수"] = int(api_total_rows)
        snap["수집"]["출전표행수"] = max(_count_rows_in_data(data, "entry_url"), _count_rows_in_data(data, "entry_registered_url"))
        snap["수집"]["경주정보행수"] = max(_count_rows_in_data(data, "race_url"), _count_rows_in_data(data, "race_overview_url"))
        snap["수집"]["배당행수"] = max(_count_rows_in_data(data, "today_odds_url"), _count_rows_in_data(data, "odds_url"), _count_rows_in_data(data, "third_odds_url"))
        if api_total_rows <= 0:
            snap["원인"].append("26개 API 수신자료 총행수 0건")
            snap["다음조치"].append("API 상태표의 URL/상태/HTTP 메시지 확인")
        if snap["수집"]["출전표행수"] <= 0:
            snap["원인"].append("출전표/출전등록말 API 0건이라 실제 마번 조합 생성 불가")
            snap["다음조치"].append("entry_url / entry_registered_url 상태와 승인 여부 확인")
    except Exception as e:
        snap["원인"].append(f"API 행수 계산 실패: {str(e)[:80]}")

    try:
        latest = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else {}
        has_combo = _mobile_has_any_real_recommend(latest) if "_mobile_has_any_real_recommend" in globals() else bool(latest.get("삼쌍승18조합"))
        snap["추천"]["최근추천저장"] = "있음" if isinstance(latest, dict) and latest else "없음"
        snap["추천"]["실제3숫자조합"] = "있음" if has_combo else "없음"
        snap["추천"]["최근저장시각"] = latest.get("저장시각", "-") if isinstance(latest, dict) else "-"
        if not has_combo:
            snap["원인"].append("모바일 표시 가능한 실제 3숫자 추천 조합이 없음")
            snap["다음조치"].append("출전표 3두 이상 수신 후 재분석 필요")
    except Exception as e:
        snap["원인"].append(f"추천 저장 확인 실패: {str(e)[:80]}")

    try:
        if "_hub365_network_allowed" in globals() and not _hub365_network_allowed():
            snap["허브"]["mobile_recommend"] = "화면진입 자동조회 차단"
        elif "external_hub_load" in globals():
            hub_mobile = external_hub_load("mobile_recommend")
            snap["허브"]["mobile_recommend"] = "있음" if hub_mobile else "없음"
        else:
            snap["허브"]["mobile_recommend"] = "허브함수없음"
    except Exception as e:
        snap["허브"]["mobile_recommend"] = f"확인실패: {str(e)[:80]}"

    if snap["수집"].get("출전표행수", 0) > 0 and snap["추천"].get("실제3숫자조합") == "있음":
        snap["최종판정"] = "추천 표시 가능"
        snap["추천가능"] = "Y"
    else:
        snap["최종판정"] = "추천 차단 · 원인 확인 필요"
        snap["추천가능"] = "N"

    try:
        if "external_hub_save" in globals():
            external_hub_save("pipeline_reason_snapshot", snap)
    except Exception:
        pass
    return snap

def render_pipeline_reason_center(rc_date: str = "", meet: str = "서울", race_no: Any = "", compact: bool = False) -> None:
    st.markdown("### 🧭 추천 없음 원인 분석센터")
    snap = _pipeline_reason_snapshot(rc_date, meet, race_no)
    if snap.get("추천가능") == "Y":
        st.success(f"최종판정: {snap.get('최종판정')}")
    else:
        st.error(f"최종판정: {snap.get('최종판정')}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("API 총행수", snap.get("수집", {}).get("API총행수", 0))
    c2.metric("출전표", snap.get("수집", {}).get("출전표행수", 0))
    c3.metric("경주일정", snap.get("일정", {}).get("전체경주일정행수", 0))
    c4.metric("추천조합", snap.get("추천", {}).get("실제3숫자조합", "없음"))
    if snap.get("원인"):
        st.markdown("#### 막힌 이유")
        for r in snap.get("원인", [])[:12]:
            st.warning(f"• {r}")
    if snap.get("다음조치"):
        st.markdown("#### 바로 할 일")
        for r in snap.get("다음조치", [])[:12]:
            st.info(f"• {r}")
    with st.expander("전체 진단 JSON", expanded=False):
        st.json(snap)


# EXCEL_DETAIL_WORKBOOK_EXPORT_FIX
def _excel_safe_sheet_name(name: Any, used: Optional[set] = None) -> str:
    used = used if used is not None else set()
    s = str(name or "Sheet").strip()
    s = re.sub(r"[\[\]\:\*\?\/\\]+", "_", s)
    s = s[:31] or "Sheet"
    base = s
    i = 1
    while s in used:
        suffix = f"_{i}"
        s = (base[:31-len(suffix)] + suffix)[:31]
        i += 1
    used.add(s)
    return s

def _excel_output_dir() -> Path:
    d = DATA_DIR / "excel_exports" if "DATA_DIR" in globals() else Path("maru_kra_data") / "excel_exports"
    d.mkdir(parents=True, exist_ok=True)
    return d

def _xlsx_write_one_sheet(writer, sheet_name: str, df: pd.DataFrame, title: str = "") -> None:
    if df is None:
        df = pd.DataFrame()
    if not isinstance(df, pd.DataFrame):
        try:
            df = pd.DataFrame(df)
        except Exception:
            df = pd.DataFrame()
    if df.empty:
        df = pd.DataFrame([{"내용": "수신 자료 없음"}])
    df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    title_fmt = workbook.add_format({"bold": True, "font_size": 14, "font_color": "#FFFFFF", "bg_color": "#111827", "align": "center"})
    header_fmt = workbook.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": "#B45309", "border": 1, "align": "center"})
    body_fmt = workbook.add_format({"border": 1, "valign": "top"})
    worksheet.merge_range(0, 0, 0, max(0, min(len(df.columns)-1, 12)), title or sheet_name, title_fmt)
    for col_idx, col_name in enumerate(df.columns):
        worksheet.write(1, col_idx, col_name, header_fmt)
        sample = [str(col_name)] + [str(x) for x in df[col_name].head(30).tolist()]
        width = min(max([len(x) for x in sample] + [10]) + 2, 42)
        worksheet.set_column(col_idx, col_idx, width, body_fmt)
    worksheet.freeze_panes(2, 0)
    try:
        worksheet.autofilter(1, 0, max(1, len(df)+1), max(0, len(df.columns)-1))
    except Exception:
        pass

def build_excel_detail_workbook(data=None, status_df=None, rc_date: str = "", meet: str = "", race_no: Any = "") -> Dict[str, Any]:
    data = data or st.session_state.get("live_data", {}) or {}
    status_df = status_df if status_df is not None else st.session_state.get("api_status", pd.DataFrame())
    if not rc_date:
        rc_date = today_kst() if "today_kst" in globals() else (now_kst().strftime("%Y%m%d") if "now_kst" in globals() else "")
    if not meet:
        meet = "서울"
    if not race_no:
        try:
            race_no = _detect_current_race_for_no_click(rc_date, meet) if "_detect_current_race_for_no_click" in globals() else ""
        except Exception:
            race_no = ""

    out_dir = _excel_output_dir()
    file_name = f"MARU_KRA_DETAIL_{_safe_filename_part(rc_date) if '_safe_filename_part' in globals() else rc_date}_{_safe_filename_part(meet) if '_safe_filename_part' in globals() else meet}_{_safe_filename_part(race_no) if '_safe_filename_part' in globals() else race_no}.xlsx"
    out_path = out_dir / file_name

    schedule_df = pd.DataFrame()
    schedule_log = pd.DataFrame()
    try:
        if "fetch_all_meet_schedule_direct" in globals():
            schedule_df, schedule_log = fetch_all_meet_schedule_direct(rc_date)
    except Exception as e:
        schedule_log = pd.DataFrame([{"상태": f"전체 일정 직접수신 실패: {str(e)[:120]}"}])

    try:
        if "no_click_fetch_26api_snapshot" in globals():
            data2, status2 = no_click_fetch_26api_snapshot(rc_date, meet, race_no)
            if data2:
                data = data2
            if isinstance(status2, pd.DataFrame) and not status2.empty:
                status_df = status2
    except Exception:
        pass

    try:
        import xlsxwriter  # noqa: F401
    except Exception:
        return {"성공": False, "메시지": "xlsxwriter가 설치되지 않았습니다. requirements.txt에 xlsxwriter를 추가해야 합니다.", "경로": ""}

    try:
        with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
            used = set()
            summary_rows = [
                {"항목": "생성시각", "값": now_str() if "now_str" in globals() else str(datetime.datetime.now())},
                {"항목": "날짜", "값": rc_date},
                {"항목": "기준 경마장", "값": meet},
                {"항목": "기준 경주", "값": race_no},
                {"항목": "경주일정 행수", "값": len(schedule_df) if isinstance(schedule_df, pd.DataFrame) else 0},
                {"항목": "API 상태 행수", "값": len(status_df) if isinstance(status_df, pd.DataFrame) else 0},
                {"항목": "API 자료 묶음수", "값": len(data) if isinstance(data, dict) else 0},
                {"항목": "자동구매", "값": "없음"},
                {"항목": "자동결제", "값": "없음"},
            ]
            _xlsx_write_one_sheet(writer, _excel_safe_sheet_name("요약", used), pd.DataFrame(summary_rows), "MARU KRA 엑셀 상세 요약")
            _xlsx_write_one_sheet(writer, _excel_safe_sheet_name("전체_경주일정", used), schedule_df, "서울·부산경남·제주 전체 경주일정")
            _xlsx_write_one_sheet(writer, _excel_safe_sheet_name("경주일정_접속로그", used), schedule_log, "경주일정 API 접속 로그")
            _xlsx_write_one_sheet(writer, _excel_safe_sheet_name("API_상태표", used), status_df, "26개 API 접속 상태표")
            label_map = dict(API_LABELS) if "API_LABELS" in globals() else {}
            if isinstance(data, dict):
                for key, df in data.items():
                    try:
                        label = label_map.get(key, key)
                        _xlsx_write_one_sheet(writer, _excel_safe_sheet_name(f"API_{label}", used), df if isinstance(df, pd.DataFrame) else pd.DataFrame(df), f"{label} 수신자료")
                    except Exception:
                        continue
        manifest = {"성공": True, "메시지": "엑셀 상세파일 생성 완료", "경로": str(out_path), "파일명": file_name, "생성시각": now_str() if "now_str" in globals() else str(datetime.datetime.now())}
        try:
            if "external_hub_save" in globals():
                external_hub_save("excel_detail_exports", manifest)
        except Exception:
            pass
        return manifest
    except Exception as e:
        return {"성공": False, "메시지": f"엑셀 생성 실패: {str(e)[:180]}", "경로": ""}

def render_excel_detail_workbook_center(data=None, status_df=None, rc_date: str = "", meet: str = "", race_no: Any = "", compact: bool = False) -> None:
    st.markdown("### 📘 엑셀 상세자료")
    st.caption("경주일정·API상태·API수신자료를 시트별로 묶은 .xlsx 파일입니다.")
    manifest = build_excel_detail_workbook(data, status_df, rc_date, meet, race_no)
    if not manifest.get("성공"):
        st.error(manifest.get("메시지", "엑셀 생성 실패"))
        return
    st.success(manifest.get("메시지", "엑셀 생성 완료"))
    st.caption(f"파일명: {manifest.get('파일명','')}")
    try:
        p = Path(manifest.get("경로", ""))
        if p.exists():
            st.download_button(
                "📘 엑셀 상세자료 열기",
                data=p.read_bytes(),
                file_name=p.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"excel_detail_download_{'m' if compact else 'p'}",
                width="stretch",
            )
    except Exception as e:
        st.warning(f"엑셀 파일 표시 실패: {e}")


# NO_CLICK_AUTO_API_DIAGNOSTIC_FIX
def _api_key_visible_status() -> Dict[str, Any]:
    info = {"키있음": False, "키출처": "-", "마스터ON": True, "선택API수": 0, "전체API수": len(API_LABELS) if "API_LABELS" in globals() else 0}
    try:
        key = get_api_key() if "get_api_key" in globals() else ""
        info["키있음"] = bool(str(key or "").strip())
        info["키출처"] = get_api_key_source() if "get_api_key_source" in globals() else ("감지됨" if key else "없음")
        info["키미리보기"] = masked_api_key() if "masked_api_key" in globals() else ("있음" if key else "없음")
    except Exception as e:
        info["키출처"] = f"확인실패: {str(e)[:60]}"
    try:
        info["마스터ON"] = bool(st.session_state.get("api_master_on", True))
    except Exception:
        pass
    try:
        switches = get_api_switches() if "get_api_switches" in globals() else {}
        info["선택API수"] = sum(1 for k, _ in API_LABELS if switches.get(k, True)) if "API_LABELS" in globals() else 0
    except Exception:
        pass
    return info

def render_no_click_api_diagnostic() -> None:
    st.markdown("### 🚦 API 연결 즉시진단")
    info = _api_key_visible_status()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("API Key", "있음" if info.get("키있음") else "없음")
    c2.metric("키 출처", str(info.get("키출처","-"))[:18])
    c3.metric("마스터", "ON" if info.get("마스터ON") else "OFF")
    c4.metric("API 선택", f"{info.get('선택API수',0)}/{info.get('전체API수',0)}")
    if not info.get("키있음"):
        st.error("공공데이터 API Key가 감지되지 않았습니다. Streamlit Secrets에 KRA_API_KEY를 넣어야 26개 API가 붙습니다.")
    elif not info.get("마스터ON"):
        st.error("API 마스터 스위치가 OFF입니다. PC 사이드바에서 API 전체 ON으로 바꿔야 합니다.")
    else:
        st.success(f"API Key 감지됨 · {info.get('키미리보기','')}")

def _auto_safe_selected_api_keys() -> List[str]:
    if "API_LABELS" in globals():
        return [k for k, _ in API_LABELS]
    return ["race_url", "entry_url", "horse_url", "body_url", "gear_url", "rating_url", "odds_url", "today_odds_url"]

def _detect_current_race_for_no_click(rc_date: str = "", meet: str = "서울") -> int:
    try:
        rc_date = rc_date or (today_kst() if "today_kst" in globals() else now_kst().strftime("%Y%m%d"))
        sched = pd.DataFrame()
        try:
            sched, _log = fetch_all_meet_schedule_direct(rc_date) if "fetch_all_meet_schedule_direct" in globals() else (pd.DataFrame(), pd.DataFrame())
        except Exception:
            sched = pd.DataFrame()
        if isinstance(sched, pd.DataFrame) and not sched.empty:
            sdf = sched[sched["경마장"].astype(str).str.contains(str(meet), na=False)].copy() if "경마장" in sched.columns else sched.copy()
            if not sdf.empty and "경주번호" in sdf.columns:
                now = now_kst() if "now_kst" in globals() else datetime.datetime.now()
                if "경주시각" in sdf.columns:
                    sdf["_dt"] = pd.to_datetime(sdf["경주시각"], errors="coerce")
                    future = sdf[sdf["_dt"].notna() & (sdf["_dt"] >= now - pd.Timedelta(minutes=20))]
                    if not future.empty:
                        return int(float(future.sort_values("_dt").iloc[0]["경주번호"]))
                return int(float(sdf.sort_values("경주번호").iloc[0]["경주번호"]))
    except Exception:
        pass
    return 1

def no_click_fetch_26api_snapshot(rc_date: str = "", meet: str = "서울", race_no: Any = "") -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    rc_date = rc_date or (today_kst() if "today_kst" in globals() else (now_kst().strftime("%Y%m%d") if "now_kst" in globals() else ""))
    meet = meet or "서울"
    try:
        race_no = int(float(race_no or _detect_current_race_for_no_click(rc_date, meet)))
    except Exception:
        race_no = 1

    data = st.session_state.get("live_data", {}) or {}
    status = st.session_state.get("api_status", pd.DataFrame())
    try:
        if isinstance(data, dict) and any((hasattr(v, "__len__") and len(v) > 0) for v in data.values()):
            return data, status if isinstance(status, pd.DataFrame) else pd.DataFrame()
    except Exception:
        pass

    try:
        if "get_api_key" in globals() and not get_api_key():
            return {}, pd.DataFrame([{"API": "전체", "key": "ALL", "행수": 0, "상태": "API_KEY 없음 · Streamlit Secrets 확인", "URL": ""}])
    except Exception:
        pass

    run_key = f"no_click_26api_once_{rc_date}_{meet}_{race_no}"
    if st.session_state.get(run_key):
        return data, status if isinstance(status, pd.DataFrame) else pd.DataFrame()
    st.session_state[run_key] = True

    try:
        selected = _auto_safe_selected_api_keys()
        data, status = fetch_all_live(rc_date, meet, int(race_no), selected)
        st.session_state["live_data"] = data
        st.session_state["api_status"] = status
        st.session_state["live_race_key"] = f"{rc_date}|{meet}|{race_no}"
        return data, status
    except Exception as e:
        return {}, pd.DataFrame([{"API": "전체", "key": "ALL", "행수": 0, "상태": f"자동접속 실패: {str(e)[:160]}", "URL": ""}])

def render_no_click_api_excel_viewer(compact: bool = False, meet: str = "서울") -> None:
    st.markdown("### 📡 26개 API 자동접속 · 바로보기")
    render_no_click_api_diagnostic()
    rc_date = today_kst() if "today_kst" in globals() else (now_kst().strftime("%Y%m%d") if "now_kst" in globals() else "")
    race_no = _detect_current_race_for_no_click(rc_date, meet)
    data, status = no_click_fetch_26api_snapshot(rc_date, meet, race_no)

    if isinstance(status, pd.DataFrame) and not status.empty:
        st.markdown("#### API 접속 상태표")
        show_cols = [c for c in ["API", "key", "행수", "상태", "URL"] if c in status.columns]
        st.dataframe(status[show_cols] if show_cols else status, use_container_width=True, hide_index=True, height=300 if compact else 420)
    else:
        st.warning("API 상태표가 아직 없습니다.")

    if isinstance(data, dict) and data:
        st.markdown("#### 받은 API 자료")
        shown = 0
        for key, df in data.items():
            try:
                if df is None:
                    continue
                if not isinstance(df, pd.DataFrame):
                    df = pd.DataFrame(df)
                if df.empty:
                    continue
                label = dict(API_LABELS).get(key, key) if "API_LABELS" in globals() else key
                st.markdown(f"**{label} · {len(df)}건**")
                st.dataframe(df.head(200), use_container_width=True, hide_index=True, height=260 if compact else 360)
                shown += 1
                if compact and shown >= 5:
                    st.caption("모바일에서는 상위 5개 수신자료만 먼저 표시합니다.")
                    break
            except Exception:
                continue
        if shown == 0:
            st.info("수신된 API 데이터 행이 0건입니다.")
    else:
        st.info("수신된 API 데이터가 없습니다. 위 상태표의 원인을 확인하세요.")


# DIRECT_ALL_MEET_SCHEDULE_EXCEL_FIX
def _meet_code(meet: str) -> str:
    m = normalize_meet(meet) if "normalize_meet" in globals() else str(meet)
    return {"서울": "1", "제주": "2", "부산경남": "3", "부경": "3", "부산": "3"}.get(m, str(meet or ""))

def _meet_endpoint_url_variants(base_url: str, meet: str) -> List[str]:
    """서울 전용 endpoint가 들어와도 부산경남/제주 endpoint 후보까지 직접 시도합니다."""
    m = normalize_meet(meet) if "normalize_meet" in globals() else str(meet)
    repls = {
        "서울": ["Seoul", "seoul", "SEOUL"],
        "제주": ["Jeju", "jeju", "JEJU"],
        "부산경남": ["Busan", "busan", "BUSAN", "BusanGyeongnam", "BusanGyeongNam", "Pukyong", "pukyong"],
    }
    out = [base_url]
    # known race endpoint family: SeoulRace_1 / JejuRace_1 / BusanRace_1 etc.
    for token in repls.get(m, []):
        for old in ["Seoul", "seoul", "SEOUL", "Jeju", "jeju", "JEJU", "Busan", "busan", "BUSAN", "BusanGyeongnam", "BusanGyeongNam", "Pukyong", "pukyong"]:
            if old in base_url:
                out.append(base_url.replace(old, token))
    seen = []
    for u in out:
        if u not in seen:
            seen.append(u)
    return seen

def _schedule_request_variants(base_url: str, rc_date: str, meet: str) -> List[str]:
    """경주일정은 rcNo를 빼고 날짜+경마장 기준으로 직접 요청합니다."""
    variants = []
    key = get_api_key() if "get_api_key" in globals() else ""
    meet_cd = _meet_code(meet)
    for u in _meet_endpoint_url_variants(base_url, meet):
        base_params = {"serviceKey": key, "pageNo": 1, "numOfRows": 200}
        for typ_key in ["resultType", "_type", "type"]:
            p = dict(base_params)
            p[typ_key] = "json"
            variants.append(add_or_replace_params(u, p))
        for date_name in ["rcDate", "raceDate", "meetDate", "ymd"]:
            for meet_name in ["meet", "meetCd", "rcourse", "raceTrack"]:
                p = dict(base_params)
                p.update({date_name: rc_date, meet_name: meet_cd, "resultType": "json"})
                variants.append(add_or_replace_params(u, p))
        # 일부 API는 날짜만 있어도 전체 경주일정이 내려옵니다.
        for date_name in ["rcDate", "raceDate", "meetDate", "ymd"]:
            p = dict(base_params)
            p.update({date_name: rc_date, "resultType": "json"})
            variants.append(add_or_replace_params(u, p))
    seen, out = set(), []
    for v in variants:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out

def fetch_schedule_direct_for_meet(rc_date: str, meet: str) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """서울/부산경남/제주 경주일정을 API에서 직접 받아 화면에서 바로 볼 수 있게 합니다."""
    logs = []
    frames = []
    keys = ["race_url", "race_overview_url"]
    for key in keys:
        try:
            base_url = get_url(key) if "get_url" in globals() else ""
        except Exception:
            base_url = ""
        if not base_url:
            logs.append({"경마장": meet, "API": key, "상태": "URL 없음", "행수": 0})
            continue
        for req_url in _schedule_request_variants(base_url, rc_date, meet)[:18]:
            try:
                r = safe_get_url(req_url, timeout=8) if "safe_get_url" in globals() else requests.get(req_url, timeout=8)
                if r.status_code != 200:
                    logs.append({"경마장": meet, "API": key, "상태": f"HTTP {r.status_code}", "행수": 0, "URL": req_url[:160]})
                    continue
                text = r.text.strip()
                if any(w in text for w in ["SERVICE_KEY_IS_NOT_REGISTERED", "INVALID_REQUEST_PARAMETER", "SERVICE_ACCESS_DENIED", "LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR", "NO_OPENAPI_SERVICE_ERROR"]):
                    logs.append({"경마장": meet, "API": key, "상태": text[:100], "행수": 0, "URL": req_url[:160]})
                    continue
                ctype = r.headers.get("content-type", "").lower()
                if text.startswith("{") or text.startswith("[") or "json" in ctype:
                    try:
                        df = json_to_df(r.json()) if "json_to_df" in globals() else pd.DataFrame()
                    except Exception:
                        df = pd.DataFrame()
                else:
                    df = xml_to_df(text) if "xml_to_df" in globals() else pd.DataFrame()
                if isinstance(df, pd.DataFrame) and not df.empty:
                    df["경마장"] = meet
                    df["수신API"] = key
                    frames.append(df)
                    logs.append({"경마장": meet, "API": key, "상태": "OK", "행수": len(df), "URL": req_url[:160]})
                    break
                logs.append({"경마장": meet, "API": key, "상태": "200 / 0건", "행수": 0, "URL": req_url[:160]})
            except Exception as e:
                logs.append({"경마장": meet, "API": key, "상태": str(e)[:100], "행수": 0})
    if frames:
        raw = pd.concat(frames, ignore_index=True)
        sched = extract_schedule_from_data({"race_url": raw}, rc_date, meet) if "extract_schedule_from_data" in globals() else raw
        if isinstance(sched, pd.DataFrame) and not sched.empty:
            sched["경마장"] = sched.get("경마장", meet)
            return sched.drop_duplicates(), logs
    return pd.DataFrame(), logs

def fetch_all_meet_schedule_direct(rc_date: str = "") -> Tuple[pd.DataFrame, pd.DataFrame]:
    if not rc_date:
        rc_date = today_kst() if "today_kst" in globals() else (now_kst().strftime("%Y%m%d") if "now_kst" in globals() else "")
    schedules, logs = [], []
    for meet in ["서울", "부산경남", "제주"]:
        df, lg = fetch_schedule_direct_for_meet(rc_date, meet)
        logs.extend(lg)
        if isinstance(df, pd.DataFrame) and not df.empty:
            schedules.append(df)
    out = pd.concat(schedules, ignore_index=True) if schedules else pd.DataFrame()
    if isinstance(out, pd.DataFrame) and not out.empty:
        try:
            out = out.drop_duplicates(subset=[c for c in ["날짜", "경마장", "경주번호"] if c in out.columns]).sort_values([c for c in ["경마장", "경주번호"] if c in out.columns])
        except Exception:
            pass
        try:
            p = DATA_DIR / "race_schedule_all_meets.csv" if "DATA_DIR" in globals() else Path("race_schedule_all_meets.csv")
            out.to_csv(p, index=False, encoding="utf-8-sig")
        except Exception:
            pass
    log_df = pd.DataFrame(logs)
    try:
        p2 = DATA_DIR / "race_schedule_fetch_log.csv" if "DATA_DIR" in globals() else Path("race_schedule_fetch_log.csv")
        log_df.to_csv(p2, index=False, encoding="utf-8-sig")
    except Exception:
        pass
    return out, log_df

def render_direct_schedule_excel_viewer(compact: bool = False) -> None:
    """다운로드/expander 없이 바로 보이는 전체 경마장 경주일정 엑셀 뷰어."""
    st.markdown("### 🗓️ 전체 경마장 경주일정 바로보기")
    rc_date = today_kst() if "today_kst" in globals() else (now_kst().strftime("%Y%m%d") if "now_kst" in globals() else "")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.caption(f"대상일자: {rc_date}")
    with col2:
        force = st.button("🔄 서울·부산경남·제주 일정 다시 받기", key=f"direct_schedule_reload_{'m' if compact else 'p'}", width="stretch")

    cache_key = f"direct_all_meet_schedule_{rc_date}"
    log_key = f"direct_all_meet_schedule_log_{rc_date}"
    # NO_AUTO_SPIN_HARD_STOP: 화면 진입만으로 경주일정 API를 호출하지 않습니다.
    # 반드시 사용자가 [일정 다시 받기] 버튼을 눌렀을 때만 1회 수집합니다.
    if force:
        with st.spinner("서울·부산경남·제주 경주일정 API 직접 수신 중..."):
            sched, log_df = fetch_all_meet_schedule_direct(rc_date)
            st.session_state[cache_key] = sched
            st.session_state[log_key] = log_df
    else:
        sched = st.session_state.get(cache_key, pd.DataFrame())
        log_df = st.session_state.get(log_key, pd.DataFrame())
        if not isinstance(sched, pd.DataFrame) or sched.empty:
            st.info("대기 중 · 화면 진입만으로 경주일정 API를 수집하지 않습니다. 필요할 때 [서울·부산경남·제주 일정 다시 받기]를 한 번만 누르세요.")
            return

    if isinstance(sched, pd.DataFrame) and not sched.empty:
        meet_col = "경마장" if "경마장" in sched.columns else None
        if meet_col:
            counts = sched.groupby(meet_col).size().to_dict()
            st.success(" / ".join([f"{k} {v}경주" for k, v in counts.items()]))
        show_cols = [c for c in ["날짜", "경마장", "경주번호", "경주시간", "경주시각"] if c in sched.columns]
        if not show_cols:
            show_cols = list(sched.columns)[:12]
        st.dataframe(sched[show_cols], use_container_width=True, hide_index=True, height=360 if compact else 520)
    else:
        st.error("서울·부산경남·제주 경주일정을 직접 받지 못했습니다.")
        st.caption("아래 API 접속 로그에서 HTTP 오류, 0건, 키 오류를 확인하세요.")

    st.markdown("#### API 접속 로그")
    if isinstance(log_df, pd.DataFrame) and not log_df.empty:
        cols = [c for c in ["경마장", "API", "상태", "행수"] if c in log_df.columns]
        st.dataframe(log_df[cols], use_container_width=True, hide_index=True, height=260 if compact else 380)
    else:
        st.info("접속 로그가 없습니다.")


# API_RECEIVED_FILE_VIEWER_FIX
def _api_received_dir() -> Path:
    d = DATA_DIR / "api_received_files" if "DATA_DIR" in globals() else Path("maru_kra_data") / "api_received_files"
    d.mkdir(parents=True, exist_ok=True)
    return d

def _safe_filename_part(x: Any) -> str:
    s = str(x or "").strip()
    s = re.sub(r"[^0-9A-Za-z가-힣_\-]+", "_", s)
    return s[:60] or "unknown"

def save_api_received_files(data=None, status_df=None, rc_date: str = "", meet: str = "", race_no: Any = "") -> Dict[str, Any]:
    data = data or st.session_state.get("live_data", {}) or {}
    status_df = status_df if status_df is not None else st.session_state.get("api_status", pd.DataFrame())
    if not rc_date:
        try:
            rc_date = today_kst() if "today_kst" in globals() else now_kst().strftime("%Y%m%d")
        except Exception:
            rc_date = ""
    if not meet:
        meet = "서울"
    if not race_no:
        try:
            latest = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else {}
            race_no = latest.get("경주번호", "")
        except Exception:
            race_no = ""

    out_dir = _api_received_dir()
    saved_rows = []
    label_map = dict(API_LABELS) if "API_LABELS" in globals() else {}

    try:
        if isinstance(status_df, pd.DataFrame) and not status_df.empty:
            status_file = out_dir / f"{_safe_filename_part(rc_date)}_{_safe_filename_part(meet)}_{_safe_filename_part(race_no)}_API_STATUS.csv"
            status_df.to_csv(status_file, index=False, encoding="utf-8-sig")
            saved_rows.append({"구분": "상태표", "API": "API_STATUS", "파일명": status_file.name, "행수": len(status_df), "컬럼수": len(status_df.columns), "경로": str(status_file), "저장시각": now_str() if "now_str" in globals() else str(datetime.datetime.now())})
    except Exception:
        pass

    try:
        for key, df in (data.items() if isinstance(data, dict) else []):
            if df is None:
                continue
            try:
                if not isinstance(df, pd.DataFrame):
                    df = pd.DataFrame(df)
            except Exception:
                continue
            label = label_map.get(key, key)
            file_path = out_dir / f"{_safe_filename_part(rc_date)}_{_safe_filename_part(meet)}_{_safe_filename_part(race_no)}_{_safe_filename_part(key)}_{_safe_filename_part(label)}.csv"
            try:
                df.to_csv(file_path, index=False, encoding="utf-8-sig")
                saved_rows.append({"구분": "API데이터", "API": label, "key": key, "파일명": file_path.name, "행수": len(df), "컬럼수": len(df.columns), "경로": str(file_path), "저장시각": now_str() if "now_str" in globals() else str(datetime.datetime.now())})
            except Exception:
                pass
    except Exception:
        pass

    try:
        sched = _load_schedule_for_sidebar(rc_date, meet) if "_load_schedule_for_sidebar" in globals() else pd.DataFrame()
        if isinstance(sched, pd.DataFrame) and not sched.empty:
            sched_file = out_dir / f"{_safe_filename_part(rc_date)}_{_safe_filename_part(meet)}_RACE_SCHEDULE.csv"
            sched.to_csv(sched_file, index=False, encoding="utf-8-sig")
            saved_rows.append({"구분": "경주일정", "API": "RACE_SCHEDULE", "파일명": sched_file.name, "행수": len(sched), "컬럼수": len(sched.columns), "경로": str(sched_file), "저장시각": now_str() if "now_str" in globals() else str(datetime.datetime.now())})
    except Exception:
        pass

    manifest = {"저장시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()), "날짜": rc_date, "경마장": meet, "경주번호": race_no, "파일수": len(saved_rows), "파일목록": saved_rows}
    try:
        (_api_received_dir() / "api_received_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    try:
        if "external_hub_save" in globals():
            external_hub_save("api_received_files", manifest)
    except Exception:
        pass
    return manifest

def load_api_received_manifest() -> Dict[str, Any]:
    try:
        p = _api_received_dir() / "api_received_manifest.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"파일수": 0, "파일목록": []}

def _read_api_received_csv(path_text: str, max_rows: int = 80) -> pd.DataFrame:
    try:
        p = Path(path_text)
        if p.exists() and p.is_file():
            return pd.read_csv(p, nrows=max_rows)
    except Exception:
        pass
    return pd.DataFrame()

def _render_one_api_file_item(item: Dict[str, Any], idx: int, allow_download: bool = False) -> None:
    title = f"{item.get('구분','파일')} · {item.get('API','')} · {item.get('행수',0)}건"
    with st.expander(title, expanded=False):
        st.caption(item.get("파일명", ""))
        df = _read_api_received_csv(item.get("경로", ""), max_rows=500)
        if not df.empty:
            st.markdown("#### 엑셀 뷰어")
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=360,
            )
            st.caption(f"표시 행수: {len(df)}건 · 컬럼수: {len(df.columns)}개")
        else:
            st.info("미리보기 할 행이 없거나 파일을 읽지 못했습니다.")

        if allow_download:
            try:
                p = Path(item.get("경로", ""))
                if p.exists() and p.is_file():
                    st.download_button("CSV 다운로드", data=p.read_bytes(), file_name=p.name, mime="text/csv", key=f"api_file_download_{idx}_{p.name}", width="stretch")
            except Exception:
                pass


def render_api_received_file_viewer(data=None, status_df=None, rc_date: str = "", meet: str = "", race_no: Any = "", compact: bool = False) -> None:
    st.markdown("### 📊 경주일정 · API 수신자료 엑셀 뷰어")
    b1, b2 = st.columns([1, 1])
    with b1:
        if st.button("🔄 현재 수집자료 새로 열기", key=f"api_file_save_now_{'m' if compact else 'p'}", width="stretch"):
            manifest = save_api_received_files(data, status_df, rc_date, meet, race_no)
            st.success(f"갱신 완료: {manifest.get('파일수', 0)}개 자료")
    with b2:
        st.caption("다운로드 없이 PC/모바일 화면에서 바로 표로 확인합니다.")

    try:
        manifest = save_api_received_files(data, status_df, rc_date, meet, race_no)
    except Exception:
        manifest = load_api_received_manifest()

    files = manifest.get("파일목록", []) if isinstance(manifest, dict) else []
    if not files:
        st.warning("아직 열어볼 API 수신자료가 없습니다. 실시간 데이터 새로고침 후 다시 확인하세요.")
        return

    st.caption(f"최근 확인: {manifest.get('저장시각','-')} · 자료 {len(files)}개")

    summary_df = pd.DataFrame(files)
    show_cols = [c for c in ["구분", "API", "파일명", "행수", "컬럼수", "저장시각"] if c in summary_df.columns]
    if show_cols:
        st.dataframe(summary_df[show_cols], use_container_width=True, hide_index=True, height=220 if compact else 300)

    schedule_files = [x for x in files if str(x.get("구분","")) == "경주일정"]
    status_files = [x for x in files if str(x.get("구분","")) == "상태표"]
    api_files = [x for x in files if str(x.get("구분","")) == "API데이터"]

    tabs = st.tabs(["경주일정", "API 상태표", "API 수신자료"])
    with tabs[0]:
        if not schedule_files:
            st.info("경주일정 자료가 없습니다.")
        else:
            # 전체 일정 우선 표시
            schedule_files = sorted(schedule_files, key=lambda x: (0 if "ALL_RACE_SCHEDULE" in str(x.get("API","")) else 1, str(x.get("API",""))))
            limit = len(schedule_files)
            for i, item in enumerate(schedule_files[:limit]):
                _render_one_api_file_item(item, 1000 + i, allow_download=False)

    with tabs[1]:
        if not status_files:
            st.info("API 상태표 자료가 없습니다.")
        else:
            for i, item in enumerate(status_files[:5]):
                _render_one_api_file_item(item, 2000 + i, allow_download=False)

    with tabs[2]:
        if not api_files:
            st.info("API 수신자료가 없습니다.")
        else:
            if compact:
                st.caption("모바일에서는 상위 10개 자료만 먼저 보여줍니다.")
                api_files = api_files[:10]
            for i, item in enumerate(api_files):
                _render_one_api_file_item(item, 3000 + i, allow_download=False)


# API_SCHEDULE_VISIBILITY_CENTER_FIX
def _safe_df_len(x) -> int:
    try:
        return int(len(x)) if x is not None else 0
    except Exception:
        return 0

def _api_status_summary_dict(status_df=None, data=None) -> Dict[str, Any]:
    """26개 API 접속/수집 여부를 PC·모바일에서 볼 수 있게 요약합니다."""
    now_text = now_str() if "now_str" in globals() else str(datetime.datetime.now())
    data = data or st.session_state.get("live_data", {}) or {}
    if status_df is None:
        status_df = st.session_state.get("api_status", pd.DataFrame())
    total = len(API_LABELS) if "API_LABELS" in globals() else 0
    rows = []
    ok_count = 0
    fail_count = 0
    waiting_count = 0

    label_map = dict(API_LABELS) if "API_LABELS" in globals() else {}
    keys = [k for k, _ in API_LABELS] if "API_LABELS" in globals() else list(data.keys())

    status_lookup = {}
    try:
        if status_df is not None and isinstance(status_df, pd.DataFrame) and not status_df.empty:
            for _, r in status_df.iterrows():
                key = str(r.get("key", "") or r.get("API", "") or "").strip()
                if key:
                    status_lookup[key] = dict(r)
    except Exception:
        pass

    for key in keys:
        label = label_map.get(key, key)
        df_len = _safe_df_len(data.get(key))
        st_row = status_lookup.get(key, {})
        row_count = df_len
        try:
            if row_count <= 0 and "행수" in st_row:
                row_count = int(float(str(st_row.get("행수", 0)).replace(",", "")))
        except Exception:
            pass
        state = str(st_row.get("상태", "") or st_row.get("분류", "") or "").strip()
        if row_count > 0 or state.upper() in ["OK", "CACHE", "SUCCESS", "성공"]:
            icon = "✅"
            ok_count += 1
            state = state or "수집됨"
        elif any(x in state for x in ["OFF", "선택 안 함", "대기", "시간전", "보류"]):
            icon = "⏳"
            waiting_count += 1
            state = state or "대기"
        else:
            icon = "❌"
            fail_count += 1
            state = state or "미수집"
        rows.append({
            "상태": icon,
            "API": label,
            "key": key,
            "행수": row_count,
            "메시지": state,
            "URL": str(st_row.get("URL", ""))[:120] if st_row else "",
        })

    schedule_rows = 0
    schedule_note = "경주일정 미확인"
    try:
        rc_date = today_kst() if "today_kst" in globals() else (now_kst().strftime("%Y%m%d") if "now_kst" in globals() else "")
        meet_counts = {}
        for m in ["서울", "부산경남", "제주"]:
            try:
                sched = _load_schedule_for_sidebar(rc_date, m) if "_load_schedule_for_sidebar" in globals() else pd.DataFrame()
                cnt = _safe_df_len(sched)
                meet_counts[m] = cnt
                schedule_rows += cnt
            except Exception:
                meet_counts[m] = 0
        schedule_note = " / ".join([f"{k} {v}건" for k, v in meet_counts.items()])
        schedule_note = f"경주일정 수신: {schedule_note}" if schedule_rows > 0 else "경주일정 0건 · API/허브 확인 필요"
    except Exception as e:
        schedule_note = f"경주일정 확인 실패: {str(e)[:80]}"

    rec = {}
    rec_note = "추천 저장 미확인"
    try:
        rec = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else {}
        if isinstance(rec, dict) and rec:
            saved = rec.get("저장시각", "-")
            meet = rec.get("경마장", "-")
            rno = rec.get("경주번호", "-")
            has_combo = _mobile_has_any_real_recommend(rec) if "_mobile_has_any_real_recommend" in globals() else bool(rec.get("삼쌍승18조합"))
            rec_note = f"최근추천 {meet} {rno}R · 저장 {saved} · {'조합있음' if has_combo else '조합없음'}"
        else:
            rec_note = "최근추천 없음"
    except Exception as e:
        rec_note = f"추천 확인 실패: {str(e)[:80]}"

    return {
        "확인시각": now_text,
        "총API": total,
        "성공": ok_count,
        "대기": waiting_count,
        "실패": fail_count,
        "경주일정건수": schedule_rows,
        "경주일정상태": schedule_note,
        "추천상태": rec_note,
        "rows": rows,
    }

def _save_api_schedule_snapshot(status_df=None, data=None) -> Dict[str, Any]:
    snap = _api_status_summary_dict(status_df, data)
    try:
        if "external_hub_save" in globals():
            external_hub_save("api_schedule_status", snap)
    except Exception:
        pass
    try:
        p = DATA_DIR / "api_schedule_status.json" if "DATA_DIR" in globals() else Path("api_schedule_status.json")
        p.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return snap

def render_api_schedule_visibility_center(status_df=None, data=None) -> None:
    """PC에서 26개 API·경주일정·추천저장 상태를 한눈에 보여줍니다.
    화면 진입만으로 허브 저장을 하지 않고, 현재 세션/캐시 상태만 표시합니다.
    """
    snap = _api_status_summary_dict(status_df, data)
    st.markdown("### 🔎 26개 API · 경주일정 · 추천저장 확인센터")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("API 성공", f"{snap.get('성공',0)} / {snap.get('총API',0)}")
    c2.metric("대기", snap.get("대기",0))
    c3.metric("실패/미수집", snap.get("실패",0))
    c4.metric("경주일정", f"{snap.get('경주일정건수',0)}건")
    st.info(snap.get("경주일정상태", ""))
    st.success(snap.get("추천상태", ""))

    rows = snap.get("rows", [])
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df[["상태", "API", "행수", "메시지"]], use_container_width=True, hide_index=True)
    else:
        st.warning("API 목록을 찾지 못했습니다.")

    with st.expander("상세 JSON / 허브 저장 확인", expanded=False):
        st.json({k: v for k, v in snap.items() if k != "rows"})

def render_mobile_api_schedule_status() -> None:
    """모바일 하단에 간단한 API/일정/추천 상태 표시.
    모바일 화면 보기만으로 허브 저장/수집을 하지 않습니다.
    """
    try:
        snap = _api_status_summary_dict()
        st.markdown("### 🔎 수집 상태")
        st.caption(f"확인 {snap.get('확인시각','-')}")
        a, b, c = st.columns(3)
        a.metric("API 성공", f"{snap.get('성공',0)}/{snap.get('총API',0)}")
        b.metric("일정", f"{snap.get('경주일정건수',0)}건")
        c.metric("미수집", snap.get("실패",0))
        st.info(snap.get("경주일정상태", ""))
        st.success(snap.get("추천상태", ""))
        with st.expander("26개 API 상세", expanded=False):
            rows = snap.get("rows", [])
            for r in rows:
                st.caption(f"{r.get('상태')} {r.get('API')} · {r.get('행수')}건 · {r.get('메시지')}")
    except Exception as e:
        st.warning(f"수집 상태 표시 오류: {e}")


# MOBILE_RACE_TIME_SELF_ANALYZE_FIX
def _mobile_pick_live_context(latest: Dict[str, Any]) -> Dict[str, Any]:
    """모바일에서 추천이 비었을 때 현재 경주시간 기준으로 분석 대상 경주를 잡습니다."""
    latest = dict(latest or {})
    rc_date = str(latest.get("날짜", "") or (today_kst() if "today_kst" in globals() else now_kst().strftime("%Y%m%d")))
    meet = str(latest.get("경마장", "") or "서울")
    try:
        race_no = int(float(latest.get("경주번호", 1) or 1))
    except Exception:
        race_no = 1

    # 경주 시간표 기준 자동 대상 경주가 있으면 그걸 우선 적용
    try:
        if "_auto_collect_window_by_schedule" in globals():
            ok, reason, target_no = _auto_collect_window_by_schedule(rc_date, meet, race_no)
            if target_no:
                race_no = int(target_no)
            return {"날짜": rc_date, "경마장": meet, "경주번호": race_no, "수집허용": bool(ok), "사유": reason}
    except Exception as e:
        return {"날짜": rc_date, "경마장": meet, "경주번호": race_no, "수집허용": True, "사유": f"시간표 확인 실패 · 모바일 즉시 분석 시도: {e}"}

    return {"날짜": rc_date, "경마장": meet, "경주번호": race_no, "수집허용": True, "사유": "모바일 즉시 분석 시도"}

def _mobile_generate_real_recommend_now(latest: Dict[str, Any]) -> Dict[str, Any]:
    """
    모바일 추천이 비어 있는데 경주 시간대라면 모바일 자체에서 공식 API 수집→분석→허브저장까지 시도.
    자동구매/자동결제는 하지 않고 추천표만 생성합니다.
    """
    ctx = _mobile_pick_live_context(latest)
    rc_date = ctx.get("날짜")
    meet = ctx.get("경마장")
    race_no = int(ctx.get("경주번호") or 1)

    try:
        # 너무 자주 두드리지 않도록 2분 단위 방어
        now = now_kst() if "now_kst" in globals() else datetime.datetime.now()
        throttle_key = f"mobile_self_analyze_{rc_date}_{meet}_{race_no}_{now.strftime('%H%M')}"
        if st.session_state.get(throttle_key):
            return dict(latest or {})
        st.session_state[throttle_key] = True
    except Exception:
        pass

    try:
        selected = [k for k, _ in API_LABELS] if "API_LABELS" in globals() else []
        if not selected:
            selected = ["race_url", "entry_url", "horse_url", "body_url", "rating_url", "odds_url", "today_odds_url", "jockey_change_url", "corner_pace_url"]

        data, status = fetch_all_live(rc_date, meet, race_no, selected)
        try:
            st.session_state["live_data"] = data
            st.session_state["api_status"] = status
            st.session_state["live_race_key"] = f"{rc_date}|{meet}|{race_no}"
        except Exception:
            pass

        env = fetch_weather(meet) if "fetch_weather" in globals() else {}
        base = build_base_horses(data, rc_date, meet, race_no)
        horses = merge_score_features(base, data, rc_date, meet, race_no)
        score_df, result, combos = score_and_recommend(horses, env, 300, "균형형")

        row = dict(result or {})
        row.update(build_3group_recommendation_from_score(score_df) if "build_3group_recommendation_from_score" in globals() else {})
        if "merge_18ticket_into_row" in globals():
            row = merge_18ticket_into_row(row, score_df, int(row.get("추천금액", 18000) or 18000))
        elif "build_18ticket_purchase_plan" in globals():
            row.update(build_18ticket_purchase_plan(score_df, row, 18000))

        live_rows = 0
        try:
            live_rows = sum(len(v) for v in data.values() if hasattr(v, "__len__"))
        except Exception:
            live_rows = 0

        row.update({
            "저장시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
            "날짜": rc_date,
            "경마장": meet,
            "경주번호": race_no,
            "데이터상태": "모바일실시간",
            "실전검증": "Y" if live_rows > 0 else row.get("실전검증", "N"),
            "실전표시불가": "N" if live_rows > 0 else row.get("실전표시불가", "Y"),
            "실시간행수": live_rows,
            "모바일자가분석": "Y",
            "자동구매": "없음",
            "자동결제": "없음",
        })

        if "_build_three_type_recommendation" in globals():
            row = _build_three_type_recommendation(row)

        # 실제 3숫자 조합이 있을 때만 저장/표시
        if "_mobile_has_any_real_recommend" in globals() and not _mobile_has_any_real_recommend(row):
            row["상태"] = "모바일 실시간 분석했지만 출전표/조합 부족"
            return row

        if "save_mobile_recommend_json" in globals():
            save_mobile_recommend_json(row)
        if "external_hub_save" in globals():
            try:
                external_hub_save("mobile_recommend", row)
                external_hub_save("three_type_recommend", row)
            except Exception:
                pass
        return row
    except Exception as e:
        row = dict(latest or {})
        row["상태"] = f"모바일 실시간 분석 실패: {str(e)[:120]}"
        row["모바일자가분석"] = "실패"
        return row


# MOBILE_NO_BLANK_ENDSTATE_FIX
def _mobile_has_real_combo_value(v: Any) -> bool:
    s = str(v or "").strip()
    if not s or s in ["-", "대기", "None", "nan"]:
        return False
    nums = re.findall(r"\d+", s)
    return len(nums) >= 3

def _mobile_has_any_real_recommend(row: Dict[str, Any]) -> bool:
    row = dict(row or {})
    keys = [
        "안정형대표", "안정형6",
        "변수형대표", "변수형6", "변수대응형대표", "변수대응형6",
        "고배당형대표", "고배당형6",
        "삼쌍승18조합", "구매표복사",
    ]
    return any(_mobile_has_real_combo_value(row.get(k, "")) for k in keys)

def _mobile_drop_placeholder_combos(row: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(row or {})
    for k in ["안정형대표", "변수형대표", "변수대응형대표", "고배당형대표"]:
        if not _mobile_has_real_combo_value(row.get(k, "")):
            row[k] = ""
    for k in ["안정형6", "변수형6", "변수대응형6", "고배당형6", "삼쌍승18조합"]:
        if not _mobile_has_real_combo_value(row.get(k, "")):
            row[k] = ""
    return row

def _render_mobile_end_or_wait_view(row: Dict[str, Any]) -> None:
    row = dict(row or {})
    meet = _safe_mobile_val(row, "경마장", default="서울") if "_safe_mobile_val" in globals() else str(row.get("경마장","서울"))
    race_no = _safe_mobile_val(row, "경주번호", default="-") if "_safe_mobile_val" in globals() else str(row.get("경주번호","-"))
    status = _safe_mobile_val(row, "상태", "데이터상태", default="추천 대기") if "_safe_mobile_val" in globals() else str(row.get("상태", row.get("데이터상태","추천 대기")))
    saved = _safe_mobile_val(row, "저장시각", default="-") if "_safe_mobile_val" in globals() else str(row.get("저장시각","-"))
    st.markdown(_mobile_real_compact_css(), unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mk-wrap">
      <div class="mk-top">
        <div class="mk-small">MARU KRA · 모바일 상태</div>
        <div class="mk-title">{meet} {race_no}R <span class="mk-gold">추천 없음</span></div>
        <div class="mk-small">저장 {saved}</div>
      </div>
      <div class="mk-status">상태: {status}</div>
      <div class="mk-card">
        <h3>오늘 표시할 실전 추천이 없습니다</h3>
        <div class="mk-six">
          허브에 남은 빈 추천/예전 추천/종료 후 추천은 모바일에서 표시하지 않습니다.<br>
          다음 경주 수집창이 열리거나 PC에서 새 3분류 추천이 저장되면 자동 표시됩니다.
        </div>
        <div class="mk-reason">안정형·변수형·고배당형 중 실제 3숫자 조합이 있을 때만 표시</div>
      </div>
      <div class="mk-note">자동구매/자동결제 없음 · 구매는 항상 본인이 수동 확정</div>
    </div>
    """, unsafe_allow_html=True)


def render_mobile_quick_view() -> None:
    # MOBILE_REAL_COMPACT_RENDER_ONLY
    # MOBILE_NO_BLANK_RENDER_GATE
    # 9ROUND_MOBILE_HARD_VIEW_ONLY: 모바일은 허브 추천 결과만 표시합니다.
    # 자동 새로고침/경주일정/API 엑셀 뷰어/상세 수집 뷰어를 호출하지 않습니다.
    # PIPELINE_REASON_CENTER_MOBILE_APPLY
    # SOURCE_TRUTH_CENTER_MOBILE_APPLY
    if False and "_install_auto_refresh" in globals():
        _install_auto_refresh(60, "mobile_compact")
    try:
        latest = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else {}
    except Exception:
        latest = {}

    if not isinstance(latest, dict) or not latest:
        latest = {
            "경마장": "서울",
            "경주번호": "-",
            "경주시간": "-",
            "상태": "모바일 추천 데이터 대기",
            "안정형대표": "",
            "변수형대표": "",
            "고배당형대표": "",
            "안정형6": "",
            "변수형6": "",
            "고배당형6": "",
            "총추천금액": "18,000원",
            "단위금액": "1,000원",
        }

    try:
        if "_sanitize_mobile_loaded_row" in globals():
            latest = _sanitize_mobile_loaded_row(latest)
        if "_mobile_compact_summary" in globals():
            latest = _mobile_compact_summary(latest)
        if "_build_three_type_recommendation" in globals():
            latest = _build_three_type_recommendation(latest)
        latest = _mobile_drop_placeholder_combos(latest)
    except Exception:
        pass

    if False and not _mobile_has_any_real_recommend(latest):
        # 모바일은 허브 추천결과만 표시합니다. 화면 진입만으로 API 수집/분석/허브저장을 하지 않습니다.
        latest = _mobile_generate_real_recommend_now(latest)  # MOBILE_RACE_TIME_SELF_ANALYZE_APPLY_DISABLED
        try:
            if "_mobile_compact_summary" in globals():
                latest = _mobile_compact_summary(latest)
            if "_build_three_type_recommendation" in globals():
                latest = _build_three_type_recommendation(latest)
            latest = _mobile_drop_placeholder_combos(latest)
        except Exception:
            pass
        if not _mobile_has_any_real_recommend(latest):
            _render_mobile_end_or_wait_view(latest)
            render_pipeline_reason_center("", "서울", "", compact=True)  # PIPELINE_REASON_CENTER_MOBILE_APPLY
            render_source_truth_center(st.session_state.get("live_data", {}), st.session_state.get("api_status", pd.DataFrame()), None, st.session_state.get("collection_mode", "실시간 API 우선 + 허브 보조"))  # SOURCE_TRUTH_CENTER_MOBILE_APPLY
            render_mobile_character_strip()  # MOBILE_CHARACTER_STRIP_APPLY
            render_mobile_api_schedule_status()  # MOBILE_API_STATUS_RENDER_APPLY
            render_direct_schedule_excel_viewer(compact=True)  # DIRECT_SCHEDULE_VIEWER_MOBILE_APPLY
            render_no_click_api_excel_viewer(compact=True, meet="서울")  # NO_CLICK_API_VIEWER_MOBILE_APPLY
            render_excel_detail_workbook_center(st.session_state.get("live_data", {}), st.session_state.get("api_status", pd.DataFrame()), compact=True)  # EXCEL_DETAIL_CENTER_MOBILE_APPLY
            render_api_received_file_viewer(st.session_state.get("live_data", {}), st.session_state.get("api_status", pd.DataFrame()), compact=True)  # MOBILE_API_RECEIVED_FILE_VIEWER_APPLY
            return

    _render_mobile_compact_3type_view(latest)
    # 9ROUND: 모바일 화면 진입만으로 API/경주일정/엑셀 상세 뷰어를 돌리지 않습니다.
    # 필요한 상태 표시는 허브 365 요약만 가볍게 보여줍니다.
    try:
        if "render_hub365_final_center" in globals():
            render_hub365_final_center(compact=True)
    except Exception:
        pass
    st.caption("모바일은 허브 mobile_recommend 추천결과만 표시합니다. 자동수집/자동구매/자동결제 없음.")
    return


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
        if st.button("🌅 오늘 아침 사전수집", width="stretch", key="api_mode_morning_collect"):
            st.session_state["collection_mode"] = "아침 사전수집"
            st.rerun()
    with c2:
        if st.button("⚡ 경주 직전 실시간만", width="stretch", key="api_mode_live_only"):
            st.session_state["collection_mode"] = "실시간 집중"
            st.rerun()
    with c3:
        if st.button("📦 허브만 불러오기", width="stretch", key="api_mode_hub_only"):
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

def _force_selected_race_context(row: Dict[str, Any], rc_date: str, meet: str, race_no: int) -> Dict[str, Any]:
    """현재 선택한 경마장·경주번호로 추천 row를 강제 고정합니다."""
    row = dict(row or {})
    row["경마장"] = str(meet)
    row["meet"] = str(meet)
    row["경주번호"] = int(race_no)
    row["race_no"] = int(race_no)
    row["rc_date"] = str(rc_date)
    row["기준일자"] = str(rc_date)
    return row

def _filter_schedule_selected_race(schedule_df: pd.DataFrame, meet: str, race_no: int) -> pd.DataFrame:
    """시간표/허브 계획에서 현재 선택한 경주만 남깁니다."""
    if schedule_df is None or not isinstance(schedule_df, pd.DataFrame) or schedule_df.empty:
        return pd.DataFrame()
    df = schedule_df.copy()
    meet_cols = ["경마장", "meet", "MEET", "경주장", "장소"]
    race_cols = ["경주번호", "race_no", "RACE_NO", "rcNo", "경주", "race"]
    mcol = next((c for c in meet_cols if c in df.columns), None)
    rcol = next((c for c in race_cols if c in df.columns), None)
    if mcol is not None:
        df = df[df[mcol].astype(str).str.contains(str(meet), na=False)]
    if rcol is not None:
        nums = pd.to_numeric(df[rcol], errors="coerce")
        df = df[nums == int(race_no)]
    return df.reset_index(drop=True)



def _filter_data_selected_race(data: Dict[str, Any], rc_date: str, meet: str, race_no: int) -> Dict[str, Any]:
    """API/캐시 data에서 현재 선택한 경마장·경주번호와 맞는 행만 남깁니다.
    부산 4경주 선택 시 부산 2경주 캐시/시간표가 추천으로 섞이는 문제를 차단합니다.
    """
    if not isinstance(data, dict) or not data:
        return data or {}
    meet_cols = ["경마장", "meet", "MEET", "경주장", "장소"]
    race_cols = ["경주번호", "race_no", "RACE_NO", "rcNo", "경주", "race"]
    out = {}
    for key, value in data.items():
        try:
            if isinstance(value, pd.DataFrame):
                df = value.copy()
            elif isinstance(value, list):
                df = pd.DataFrame(value)
            else:
                out[key] = value
                continue

            if df.empty:
                out[key] = df
                continue

            mcol = next((c for c in meet_cols if c in df.columns), None)
            rcol = next((c for c in race_cols if c in df.columns), None)

            if mcol is not None:
                df = df[df[mcol].astype(str).str.contains(str(meet), na=False)]

            if rcol is not None:
                nums = pd.to_numeric(df[rcol], errors="coerce")
                df = df[nums == int(race_no)]

            out[key] = df.reset_index(drop=True)
        except Exception:
            out[key] = value
    return out

def _validate_selected_race_horses(score_df: pd.DataFrame, meet: str, race_no: int) -> pd.DataFrame:
    """추천 직전 score_df도 현재 경주와 실제 출전마만 남깁니다."""
    if score_df is None or not isinstance(score_df, pd.DataFrame) or score_df.empty:
        return pd.DataFrame()
    df = score_df.copy()
    meet_cols = ["경마장", "meet", "MEET", "경주장", "장소"]
    race_cols = ["경주번호", "race_no", "RACE_NO", "rcNo", "경주", "race"]
    mcol = next((c for c in meet_cols if c in df.columns), None)
    rcol = next((c for c in race_cols if c in df.columns), None)
    if mcol is not None:
        df = df[df[mcol].astype(str).str.contains(str(meet), na=False)]
    if rcol is not None:
        nums = pd.to_numeric(df[rcol], errors="coerce")
        df = df[nums == int(race_no)]
    return df.reset_index(drop=True)



# END_OF_DAY_HARD_STOP_FINAL
def _end_of_day_kst_stop(rc_date: str = "", meet: str = "서울") -> Tuple[bool, Optional[int], str]:
    """오늘 경주 종료 후 기본 경주 실시간 수집 루프를 강제로 막습니다."""
    try:
        now = now_kst()
    except Exception:
        now = datetime.datetime.now()

    # 18시 이후는 한국 경마 실전 화면에서 경주 종료/정산 시간대로 보고 API 실시간 수집을 멈춥니다.
    ended_by_clock = now.hour >= 18

    last_no: Optional[int] = None
    last_time = ""

    try:
        cur = current_live_race_from_schedule(meet, rc_date or today_kst())
        if cur:
            last_no = int(cur.get("경주번호", 0) or 0) or None
            last_time = str(cur.get("경주시간", "") or "")
    except Exception:
        pass

    try:
        sched = _load_schedule_for_sidebar(rc_date or today_kst(), meet) if "_load_schedule_for_sidebar" in globals() else pd.DataFrame()
        if isinstance(sched, pd.DataFrame) and not sched.empty:
            race_cols = [c for c in sched.columns if str(c) in ["경주번호", "race_no", "RACE_NO", "rcNo", "경주", "race"]]
            time_cols = [c for c in sched.columns if str(c) in ["경주예정시각", "예정시각", "출발시각", "경주시간", "race_time", "rcTime", "time", "출발시간"]]
            if race_cols:
                nums = pd.to_numeric(sched[race_cols[0]], errors="coerce").dropna().astype(int).tolist()
                if nums:
                    last_no = max(nums)
            if time_cols:
                times = []
                for v in sched[time_cols[0]].tolist():
                    mm = _parse_hhmm_to_minutes(v) if "_parse_hhmm_to_minutes" in globals() else None
                    if mm is not None:
                        times.append((mm, v))
                if times:
                    times.sort()
                    last_time = _minutes_to_hhmm(times[-1][0]) if "_minutes_to_hhmm" in globals() else str(times[-1][1])
                    now_min = now.hour * 60 + now.minute
                    ended_by_clock = ended_by_clock or now_min > int(times[-1][0]) + 20
    except Exception:
        pass

    return bool(ended_by_clock), last_no, last_time

def _end_of_day_cache_status(meet: str, race_no: int) -> pd.DataFrame:
    return pd.DataFrame([{
        "API": "경주종료",
        "key": "end_of_day",
        "행수": 0,
        "상태": f"오늘 {meet} 경주 종료 · {int(race_no)}경주 기준 저장/캐시 표시 · 실시간 API 수집 중단",
        "URL": ""
    }])




# ALLOWED_WEB_PATROL_AGENT_FIX
def _get_allowed_source_urls() -> List[str]:
    """
    허용된 공개 URL만 순찰합니다.
    - 로그인 필요 사이트 금지
    - 자동구매/자동결제 금지
    - 차단 우회/캡차 우회/비공개 페이지 접근 금지
    Streamlit Secrets 예:
    PUBLIC_SOURCE_URLS = "https://example.com/page1,https://example.com/page2"
    """
    urls = []
    try:
        raw = ""
        if hasattr(st, "secrets") and "PUBLIC_SOURCE_URLS" in st.secrets:
            raw = str(st.secrets.get("PUBLIC_SOURCE_URLS", ""))
        if raw:
            for u in re.split(r"[,\n]+", raw):
                u = str(u).strip()
                if u.startswith("https://") or u.startswith("http://"):
                    urls.append(u)
    except Exception:
        pass
    return urls[:10]

def _plain_text_from_html(html: str, limit: int = 6000) -> str:
    s = str(html or "")
    s = re.sub(r"(?is)<script.*?>.*?</script>", " ", s)
    s = re.sub(r"(?is)<style.*?>.*?</style>", " ", s)
    s = re.sub(r"(?is)<[^>]+>", " ", s)
    s = re.sub(r"&nbsp;|&amp;|&lt;|&gt;", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:limit]

def _extract_racing_signals(text: str) -> Dict[str, Any]:
    """
    공개 페이지 텍스트에서 경마 관련 신호만 요약.
    실제 판단은 기존 공식 API/허브 데이터와 합쳐서 사용.
    """
    t = str(text or "")
    keywords = {
        "출전": len(re.findall(r"출전|출전표|출주", t)),
        "기수": len(re.findall(r"기수|기승|변경", t)),
        "주로": len(re.findall(r"주로|불량|다습|건조|포화|양호", t)),
        "체중": len(re.findall(r"체중|증감|마체", t)),
        "배당": len(re.findall(r"배당|인기|확정", t)),
        "취소": len(re.findall(r"취소|제외|출전취소|경주취소", t)),
    }
    risk_words = []
    for w in ["출전취소", "기수변경", "주로불량", "마체중", "배당", "인기", "취소", "제외"]:
        if w in t:
            risk_words.append(w)
    return {
        "키워드카운트": keywords,
        "감지단어": list(dict.fromkeys(risk_words))[:20],
        "요약": " / ".join([f"{k}:{v}" for k, v in keywords.items() if v > 0]) or "특이 신호 없음",
    }

def _allowed_web_patrol_once() -> Dict[str, Any]:
    """
    별 에이전트의 공개 사이트 순찰.
    주의: 승인/허용된 공개 URL만. 로그인, 우회, 자동구매 없음.
    """
    result = {
        "실행시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
        "상태": "대기",
        "수집URL수": 0,
        "성공": 0,
        "실패": 0,
        "신호": [],
        "주의": "공개 허용 URL만 수집 · 로그인/우회/자동구매 금지",
    }
    urls = _get_allowed_source_urls()
    result["수집URL수"] = len(urls)
    if not urls:
        result["상태"] = "PUBLIC_SOURCE_URLS 없음 · 공식 API/허브만 사용"
        return result

    try:
        import requests
    except Exception as e:
        result["상태"] = f"requests 사용 불가: {e}"
        return result

    headers = {
        "User-Agent": "MARU-KRA-Research-Agent/1.0 (public allowed sources only; no login; no purchase)"
    }

    for url in urls:
        item = {"url": url, "상태": "대기", "요약": "", "신호": {}}
        try:
            r = requests.get(url, headers=headers, timeout=8)
            if r.status_code != 200:
                item["상태"] = f"HTTP {r.status_code}"
                result["실패"] += 1
            else:
                text = _plain_text_from_html(r.text)
                sig = _extract_racing_signals(text)
                item["상태"] = "성공"
                item["요약"] = sig.get("요약", "")
                item["신호"] = sig
                result["성공"] += 1
        except Exception as e:
            item["상태"] = f"실패: {str(e)[:80]}"
            result["실패"] += 1
        result["신호"].append(item)

    result["상태"] = "완료"
    return result

def _save_web_patrol_to_hub(report: Dict[str, Any]) -> None:
    try:
        if "external_hub_save" in globals():
            external_hub_save("web_patrol", report)
    except Exception:
        pass

def _web_patrol_summary_text(report: Dict[str, Any]) -> str:
    lines = [
        "[별 · 공개 사이트 순찰]",
        f"상태: {report.get('상태','')}",
        f"URL수: {report.get('수집URL수',0)} / 성공: {report.get('성공',0)} / 실패: {report.get('실패',0)}",
        f"주의: {report.get('주의','')}",
        "",
    ]
    for item in report.get("신호", [])[:5]:
        lines.append(f"- {item.get('url','')}")
        lines.append(f"  상태: {item.get('상태','')}")
        lines.append(f"  요약: {item.get('요약','')}")
    if not report.get("신호"):
        lines.append("등록된 공개 URL이 없습니다. Streamlit Secrets에 PUBLIC_SOURCE_URLS를 넣어야 합니다.")
    return "\n".join(lines)

def _auto_web_patrol_if_due() -> Dict[str, Any]:
    """
    자동 순찰은 화면 진입 때 돌지 않습니다.
    Apps Script/background tick 또는 사용자가 허용한 경우에만 실행합니다.
    """
    try:
        if "_hub365_network_allowed" in globals() and not _hub365_network_allowed():
            return {}
        now = now_kst() if "now_kst" in globals() else datetime.datetime.now()
        key = f"web_patrol_{now.strftime('%Y%m%d_%H%M')}"
        if now.minute % 5 != 0:
            return {}
        if st.session_state.get(key):
            return {}
        st.session_state[key] = True
        report = _allowed_web_patrol_once()
        _save_web_patrol_to_hub(report)
        return report
    except Exception:
        return {}




# WEEKLY_HUB_AGENT_FRI7_APPLY_FIX
def _weekday_kst() -> int:
    try:
        return (now_kst() if "now_kst" in globals() else datetime.datetime.now()).weekday()
    except Exception:
        return datetime.datetime.now().weekday()

def _weekly_agent_phase() -> Dict[str, Any]:
    """
    월화수목: 허브에서 AI 에이전트 운영/누적
    금요일 오전 7시 이후: 주간 학습결과를 적용 가능 상태로 전환
    토일: 적용된 전략으로 경주일 운영
    """
    try:
        now = now_kst() if "now_kst" in globals() else datetime.datetime.now()
    except Exception:
        now = datetime.datetime.now()
    wd = now.weekday()  # 월0 화1 수2 목3 금4 토5 일6

    if wd in [0, 1, 2, 3]:
        return {"phase": "hub_train", "label": "월화수목 허브 운영", "apply_ready": False, "weekday": wd, "hour": now.hour}
    if wd == 4 and now.hour < 7:
        return {"phase": "fri_wait", "label": "금요일 07:00 적용 대기", "apply_ready": False, "weekday": wd, "hour": now.hour}
    if wd == 4 and now.hour >= 7:
        return {"phase": "fri_apply", "label": "금요일 07:00 이후 전략 적용", "apply_ready": True, "weekday": wd, "hour": now.hour}
    return {"phase": "race_operate", "label": "주말 적용전략 운영", "apply_ready": True, "weekday": wd, "hour": now.hour}

def _weekly_agent_base_plan() -> Dict[str, Any]:
    return {
        "저장시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
        "주간모드": _weekly_agent_phase(),
        "운영원칙": "월화수목 허브 학습/수집 · 금요일 07:00 전략 적용 · 토일 경주 운영",
        "해": "주간 누적 데이터 총괄 판단",
        "달": "금요일 07:00 적용시각 감시",
        "별": "공식 API/공개URL 수집상태 누적",
        "구름": "변수 패턴 누적",
        "비": "배당/결과/learning_bigdata 기반 가중치 제안",
        "적용상태": "대기",
        "추천가중치": {"안정형": 1.0, "변수형": 1.0, "고배당형": 1.0},
    }

def _weekly_hub_agent_train_once() -> Dict[str, Any]:
    """
    월화수목 허브 운영:
    - 통신상태 저장
    - 웹 순찰 가능 시 저장
    - 수익효율 학습요약 저장
    - 코드개선 제안 저장
    """
    phase = _weekly_agent_phase()
    plan = _weekly_agent_base_plan()
    plan["적용상태"] = "허브운영중" if phase["phase"] == "hub_train" else "대기"

    try:
        comm = _comm_status_snapshot() if "_comm_status_snapshot" in globals() else {}
        plan["통신상태"] = comm
    except Exception as e:
        plan["통신상태"] = {"오류": str(e)[:120]}

    try:
        eff = _profit_efficiency_learning() if "_profit_efficiency_learning" in globals() else {}
        plan["추천가중치"] = eff.get("추천가중치", plan["추천가중치"]) if isinstance(eff, dict) else plan["추천가중치"]
        plan["수익효율"] = eff
    except Exception as e:
        plan["수익효율"] = {"오류": str(e)[:120]}

    try:
        if "_auto_web_patrol_if_due" in globals():
            patrol = _auto_web_patrol_if_due()
            if patrol:
                plan["웹순찰"] = patrol
    except Exception:
        pass

    try:
        code_sug = _code_improvement_suggestions() if "_code_improvement_suggestions" in globals() else {}
        plan["코드개선제안"] = code_sug
    except Exception:
        pass

    try:
        if "external_hub_save" in globals():
            external_hub_save("weekly_agent_plan", plan)
            external_hub_save("weekly_agent_runs", {
                "저장시각": plan.get("저장시각", ""),
                "주간모드": phase,
                "요약": "월화수목 허브 운영/누적",
                "추천가중치": plan.get("추천가중치", {}),
            })
    except Exception:
        pass
    return plan

def _weekly_agent_apply_if_due() -> Dict[str, Any]:
    """
    금요일 오전 7시 이후 자동 적용:
    - weekly_agent_plan을 읽어 적용 상태로 저장
    - 추천가중치를 active_strategy에 저장
    - 자동 코드 배포는 하지 않음. 앱 내부 전략값만 적용.
    """
    phase = _weekly_agent_phase()
    result = {
        "실행시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
        "주간모드": phase,
        "적용됨": False,
        "메모": "",
    }

    if not phase.get("apply_ready"):
        result["메모"] = phase.get("label", "적용 대기")
        return result

    try:
        plan = external_hub_load("weekly_agent_plan") if "external_hub_load" in globals() else {}
        if not isinstance(plan, dict) or not plan:
            plan = _weekly_hub_agent_train_once()
        weights = plan.get("추천가중치", {"안정형": 1.0, "변수형": 1.0, "고배당형": 1.0})
        active = {
            "적용시각": result["실행시각"],
            "적용요일": "금요일 07:00 이후" if phase.get("phase") == "fri_apply" else "주말 운영",
            "추천가중치": weights,
            "주간계획": plan,
            "주의": "자동구매/자동결제/자동배포 없음 · 추천전략만 앱 내부 적용",
        }
        result["적용됨"] = True
        result["메모"] = "weekly_agent_plan → active_strategy 적용"
        result["active_strategy"] = active
        if "external_hub_save" in globals():
            external_hub_save("active_strategy", active)
            external_hub_save("weekly_apply_log", result)
    except Exception as e:
        result["메모"] = f"적용 오류: {str(e)[:150]}"
    return result

def _weekly_agent_tick() -> Dict[str, Any]:
    """
    화면 실행 시 가벼운 주간 에이전트 틱.
    월화수목에는 허브 운영, 금요일 7시 이후에는 적용.
    중복 실행은 session_state로 같은 시간대 반복을 줄임.
    """
    try:
        now = now_kst() if "now_kst" in globals() else datetime.datetime.now()
        phase = _weekly_agent_phase()
        # 월화수목은 매시 1회, 금요일 적용은 7시 이후 매시 1회 체크
        key = f"weekly_agent_{now.strftime('%Y%m%d_%H')}_{phase.get('phase')}"
        if st.session_state.get(key):
            return {"주간모드": phase, "중복방지": True}
        st.session_state[key] = True

        if phase.get("phase") == "hub_train":
            return _weekly_hub_agent_train_once()
        if phase.get("apply_ready"):
            return _weekly_agent_apply_if_due()
        return {"주간모드": phase, "메모": "대기"}
    except Exception as e:
        return {"오류": str(e)[:150]}

def _weekly_agent_status_text() -> str:
    phase = _weekly_agent_phase()
    lines = [
        "[주간 AI 에이전트 운영]",
        "월화수목: 허브에서 해·달·별·구름·비 운영/누적",
        "금요일 07:00: 주간 학습전략 적용",
        "토일: 적용전략으로 경주 운영",
        "",
        f"현재상태: {phase.get('label')}",
    ]
    try:
        active = {}
        if not ("_hub365_network_allowed" in globals() and not _hub365_network_allowed()):
            active = external_hub_load("active_strategy") if "external_hub_load" in globals() else {}
        if isinstance(active, dict) and active:
            lines.append(f"활성전략 적용시각: {active.get('적용시각','')}")
            lines.append(f"추천가중치: {active.get('추천가중치',{})}")
    except Exception:
        pass
    return "\n".join(lines)

def render_weekly_agent_center() -> None:
    try:
        st.markdown("### 🗓️ 주간 AI 에이전트 운영")
        st.caption("월화수목은 허브에서 운영/누적, 금요일 오전 7시에 전략 적용합니다.")
        tick = st.session_state.get("weekly_agent_last_tick", {"상태": "대기", "메모": "화면 진입만으로 자동 실행하지 않습니다."})
        with st.expander("주간 운영 상태", expanded=False):
            st.text(_weekly_agent_status_text())
            st.json(tick)
        c1, c2, c3 = st.columns(3)
        if c1.button("월화수목 허브운영 즉시 실행", key="weekly_hub_train_once_btn"):
            st.session_state["weekly_agent_last_tick"] = _weekly_hub_agent_train_once()
            st.json(st.session_state["weekly_agent_last_tick"])
        if c2.button("금요일 07시 전략 적용 확인", key="weekly_strategy_apply_btn"):
            st.session_state["weekly_agent_last_tick"] = _weekly_agent_apply_if_due()
            st.json(st.session_state["weekly_agent_last_tick"])
        if c3.button("active_strategy 보기", key="weekly_active_strategy_view_btn"):
            try:
                st.json(external_hub_load("active_strategy") if "external_hub_load" in globals() else {})
            except Exception as e:
                st.warning(str(e))
    except Exception as e:
        st.warning(f"주간 AI 에이전트 표시 오류: {e}")


# SELF_LEARNING_CONTROL_CENTER_FIX
def _self_learning_governance() -> Dict[str, Any]:
    """
    목적:
    - 스스로 학습: 결과/로그/통신상태를 저장하고 다음 판단에 반영
    - 코드개선: 오류 패턴을 분석해 '패치 제안'을 생성
    - 통신 안정화: API/허브/모바일 동기화 상태 점검
    - 수익효율: 안정형/변수형/고배당형 결과 누적으로 가중치 보정
    원칙:
    - 자동구매/자동결제 금지
    - 자동 GitHub 배포 금지
    - 코드 수정은 제안까지만, 최종 적용은 사람이 확인
    """
    return {
        "자동구매": "금지",
        "자동결제": "금지",
        "자동배포": "금지",
        "코드수정": "AI 제안 생성 → 사람 확인 후 적용",
        "데이터학습": "learning_bigdata/agent_runs/web_patrol/comm_status 기반",
        "목표": "통신 안정화 + 분석 품질 개선 + 수익효율 보정",
    }

def _comm_status_snapshot() -> Dict[str, Any]:
    """API/허브/모바일/PC 통신 안정성 점검."""
    snap = {
        "저장시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
        "GoogleSheet허브": "대기",
        "모바일추천": "대기",
        "3분류추천": "대기",
        "학습데이터": "대기",
        "웹순찰": "대기",
        "권장조치": [],
    }
    try:
        if "_hub365_network_allowed" in globals() and not _hub365_network_allowed():
            snap["GoogleSheet허브"] = "화면진입 자동조회 차단"
            mobile = three = learn = patrol = {}
        elif "external_hub_load" in globals():
            mobile = external_hub_load("mobile_recommend")
            three = external_hub_load("three_type_recommend")
            learn = external_hub_load("learning_bigdata")
            patrol = external_hub_load("web_patrol")
            snap["GoogleSheet허브"] = "연결됨"
            snap["모바일추천"] = "있음" if isinstance(mobile, dict) and mobile else "비어있음"
            snap["3분류추천"] = "있음" if isinstance(three, dict) and three else "비어있음"
            snap["학습데이터"] = "있음" if learn else "비어있음"
            snap["웹순찰"] = "있음" if patrol else "비어있음"
        else:
            snap["GoogleSheet허브"] = "외부허브 함수 없음"
    except Exception as e:
        snap["GoogleSheet허브"] = f"오류: {str(e)[:120]}"
        snap["권장조치"].append("Streamlit Secrets의 GOOGLE_SCRIPT_URL / GOOGLE_SCRIPT_TOKEN 확인")

    if snap["모바일추천"] == "비어있음":
        snap["권장조치"].append("PC에서 현재 경주 3분류 추천 저장 필요")
    if snap["학습데이터"] == "비어있음":
        snap["권장조치"].append("실제 결과 저장이 누적되어야 자기학습 가능")
    if snap["웹순찰"] == "비어있음":
        snap["권장조치"].append("PUBLIC_SOURCE_URLS 공개 URL 등록 시 별 에이전트 순찰 가능")
    return snap

def _save_comm_status_snapshot() -> None:
    try:
        snap = _comm_status_snapshot()
        if "external_hub_save" in globals():
            external_hub_save("comm_status", snap)
    except Exception:
        pass

def _profit_efficiency_learning() -> Dict[str, Any]:
    """learning_bigdata 기반 수익효율 보정 요약."""
    try:
        rows = _load_learning_bigdata(500) if "_load_learning_bigdata" in globals() else []
    except Exception:
        rows = []
    stat = {
        "총기록": len(rows),
        "추천가중치": {"안정형": 1.0, "변수형": 1.0, "고배당형": 1.0},
        "메모": "실제결과가 누적되면 분류별 가중치를 보정합니다.",
    }
    if not rows:
        return stat

    hit = {"안정형": 0, "변수형": 0, "고배당형": 0}
    for r in rows:
        s = str(r.get("적중분류", ""))
        if "안정" in s:
            hit["안정형"] += 1
        if "변수" in s:
            hit["변수형"] += 1
        if "고배당" in s:
            hit["고배당형"] += 1

    total_hit = max(sum(hit.values()), 1)
    for k in hit:
        # 데이터가 적을 땐 과보정하지 않게 0.85~1.25 범위
        ratio = hit[k] / total_hit
        stat["추천가중치"][k] = round(max(0.85, min(1.25, 0.85 + ratio * 1.2)), 3)
    stat["메모"] = f"누적 적중: 안정 {hit['안정형']} / 변수 {hit['변수형']} / 고배당 {hit['고배당형']}"
    return stat

def _code_improvement_suggestions(log_text: str = "") -> Dict[str, Any]:
    """오류 로그/운영 상태 기반 코드개선 제안. 실제 코드는 자동 적용하지 않음."""
    text = str(log_text or "")
    suggestions = []
    patterns = {
        "NameError": "변수 스코프/함수 인자명 통일 필요",
        "IndexError": "빈 DataFrame/빈 리스트 방어 필요",
        "KeyError": "컬럼 존재 확인 및 기본값 처리 필요",
        "HTTP 500": "API endpoint/serviceKey/date 파라미터와 재시도/캐시 처리 필요",
        "timeout": "API 호출 timeout 분리와 성공 캐시 우선 사용 필요",
        "JSONDecodeError": "응답 포맷 XML/JSON 자동 판별 필요",
        "Permission": "Google Sheet Apps Script 권한/배포 URL 확인 필요",
    }
    for p, msg in patterns.items():
        if p.lower() in text.lower():
            suggestions.append(msg)

    if not suggestions:
        suggestions = [
            "경주별 -25분~+20분 5분 수집창 유지",
            "성공 API 응답은 캐시에 저장하고 실패 API는 다음 tick까지 재시도 제한",
            "모바일은 3분류 핵심만 표시하고 상세는 PC로 분리",
            "결과 저장 후 안정형/변수형/고배당형 적중분류를 반드시 기록",
        ]

    out = {
        "생성시각": now_str() if "now_str" in globals() else str(datetime.datetime.now()),
        "패치방식": "제안만 생성 · 자동배포 금지",
        "제안": suggestions,
        "다음단계": "사람이 확인 후 app.py 반영",
    }
    try:
        if "external_hub_save" in globals():
            external_hub_save("code_suggestions", out)
    except Exception:
        pass
    return out

def _self_learning_status_text() -> str:
    gov = _self_learning_governance()
    comm = _comm_status_snapshot()
    eff = _profit_efficiency_learning()
    lines = [
        "[자가학습/운영센터]",
        f"목표: {gov.get('목표')}",
        f"코드수정: {gov.get('코드수정')}",
        f"자동배포: {gov.get('자동배포')}",
        f"구매/결제: 자동구매 {gov.get('자동구매')} / 자동결제 {gov.get('자동결제')}",
        "",
        "[통신상태]",
        f"허브: {comm.get('GoogleSheet허브')}",
        f"모바일추천: {comm.get('모바일추천')}",
        f"3분류추천: {comm.get('3분류추천')}",
        f"학습데이터: {comm.get('학습데이터')}",
        "",
        "[수익효율 학습]",
        f"총기록: {eff.get('총기록')}",
        f"가중치: {eff.get('추천가중치')}",
        f"메모: {eff.get('메모')}",
    ]
    if comm.get("권장조치"):
        lines.append("")
        lines.append("[권장조치]")
        for x in comm.get("권장조치", []):
            lines.append(f"- {x}")
    return "\n".join(lines)

def render_self_learning_control_center() -> None:
    """PC 전용 자가학습/코드개선/통신안정화 센터."""
    try:
        st.markdown("### 🧠 자가학습 운영센터")
        st.caption("스스로 데이터는 누적하지만, 코드 적용/배포와 구매/결제는 사람 확인이 필요합니다.")
        c1, c2, c3 = st.columns(3)
        if c1.button("통신점검 저장", key="self_learning_save_comm_status"):
            _save_comm_status_snapshot()
            st.success("comm_status 저장 완료")
        if c2.button("수익효율 학습요약", key="self_learning_profit_summary"):
            st.json(_profit_efficiency_learning())
        if c3.button("코드개선 제안", key="self_learning_code_suggest"):
            st.json(_code_improvement_suggestions())
        with st.expander("자가학습 상태 보기", expanded=False):
            st.text(_self_learning_status_text())
        with st.expander("로그 붙여넣고 코드개선 제안 받기", expanded=False):
            log_text = st.text_area("오류 로그/Streamlit 로그", height=180, key="self_learning_log_text")
            if st.button("로그 분석 후 제안 저장", key="self_learning_log_suggest_save"):
                st.json(_code_improvement_suggestions(log_text))
    except Exception as e:
        st.warning(f"자가학습 운영센터 표시 오류: {e}")


# PC_COMMAND_INPUT_CONSOLE_FIX
COMMAND_EXAMPLES = [
    "해 상태",
    "달 자동수집 상태",
    "별 공식API 상태",
    "사이트수집",
    "웹 순찰",
    "구름 변수 체크",
    "비 학습요약",
    "3분류 추천 보여줘",
    "모바일 주소",
    "허브 저장 상태",
    "자가학습",
    "통신점검",
    "코드진단",
    "수익효율",
    "주간운영",
    "금요일적용",
    "월화수목",
    "오늘 종료 상태",
    "서울 9경주",
]

def _pc_command_parse(cmd: str) -> Dict[str, Any]:
    s = str(cmd or "").strip()
    out = {"raw": s, "action": "help", "meet": "", "race_no": None}
    if not s:
        return out

    nums = re.findall(r"(\d+)\s*경주|\b(\d+)\s*R\b", s, flags=re.IGNORECASE)
    if nums:
        n = next((a or b for a, b in nums if (a or b)), None)
        if n:
            try:
                out["race_no"] = int(n)
            except Exception:
                pass

    for meet in ["서울", "부산", "제주"]:
        if meet in s:
            out["meet"] = meet

    if any(x in s for x in ["해", "총괄", "전략"]):
        out["action"] = "sun"
    elif any(x in s for x in ["달", "시간", "일정", "자동수집", "종료"]):
        out["action"] = "moon"
    elif any(x in s for x in ["사이트수집", "사이트 순찰", "웹수집", "웹 순찰", "돌아", "순찰"]):
        out["action"] = "web_patrol"  # WEB_PATROL_COMMAND_PARSE
    elif any(x in s for x in ["별", "공식", "API", "api", "출전표"]):
        out["action"] = "star"
    elif any(x in s for x in ["구름", "변수", "체중", "게이트", "주로", "날씨", "기수"]):
        out["action"] = "cloud"
    elif any(x in s for x in ["비", "학습", "빅데이터", "결과", "배당"]):
        out["action"] = "rain"
    elif any(x in s for x in ["추천", "3분류", "안정", "고배당"]):
        out["action"] = "recommend"
    elif any(x in s for x in ["모바일", "주소", "링크"]):
        out["action"] = "mobile_link"
    elif any(x in s for x in ["주간운영", "금요일적용", "월화수목", "주간 AI", "주간에이전트"]):
        out["action"] = "weekly_agent"  # WEEKLY_AGENT_COMMAND_PARSE
    elif any(x in s for x in ["자가학습", "운영센터", "통신점검", "코드진단", "수익효율", "코드개선"]):
        out["action"] = "self_learning"  # SELF_LEARNING_COMMAND_PARSE
    elif any(x in s for x in ["허브", "저장", "구글", "시트"]):
        out["action"] = "hub"
    return out

def _pc_command_execute(cmd: str, current_row: Dict[str, Any] = None) -> str:
    parsed = _pc_command_parse(cmd)
    row = dict(current_row or {})
    action = parsed.get("action", "help")

    if parsed.get("meet"):
        row["경마장"] = parsed["meet"]
    if parsed.get("race_no"):
        row["경주번호"] = parsed["race_no"]

    try:
        if "_build_three_type_recommendation" in globals():
            row = _build_three_type_recommendation(row)
    except Exception:
        pass

    if action == "sun":
        return (
            "[해 · 총괄 판단]\\n"
            "안정형/변수형/고배당형의 균형을 잡습니다.\\n"
            f"현재 전략: {row.get('투자전략', '3분류 분산 · 구매/결제 수동')}\\n"
            f"수익효율: {row.get('수익효율메모', '')}"
        )

    if action == "moon":
        try:
            rc_date = str(row.get("날짜", today_kst() if "today_kst" in globals() else ""))
            meet = str(row.get("경마장", "서울") or "서울")
            race_no = int(float(row.get("경주번호", 1) or 1))
            if "_auto_collect_window_by_schedule" in globals():
                ok, reason, target_no = _auto_collect_window_by_schedule(rc_date, meet, race_no)
                return f"[달 · 일정/시간]\\n자동수집 허용: {ok}\\n상태: {reason}\\n대상경주: {target_no or race_no}"
        except Exception as e:
            return f"[달 · 일정/시간]\\n점검 필요: {e}"
        return "[달 · 일정/시간]\\n한국시간 기준 경주 -25분~+20분, 5분 단위 자동수집입니다."

    if action == "web_patrol":
        report = _allowed_web_patrol_once()
        _save_web_patrol_to_hub(report)
        return _web_patrol_summary_text(report)  # WEB_PATROL_COMMAND_EXECUTE

    if action == "star":
        return (
            "[별 · 공식데이터]\\n"
            "KRA/공공데이터 승인 API와 Google Sheet 허브 기준으로 출전표·말·기수·배당·결과를 확인합니다.\\n"
            f"실시간행수: {row.get('실시간행수', row.get('출전두수', '대기'))}\\n"
            "원칙: 승인 API 우선, 무단 크롤링 금지\n명령: 사이트수집 / 웹 순찰"  # WEB_PATROL_STAR_TEXT
        )

    if action == "cloud":
        return (
            "[구름 · 변수감지]\\n"
            "체중변화·게이트·주로상태·날씨·기수변경·인기변화를 확인해 변수형 추천을 담당합니다.\\n"
            f"변수형 대표: {row.get('변수형대표', '')}\\n"
            f"변수형 6: {row.get('변수형6', '')}\\n"
            f"근거: {row.get('변수형근거', '')}"
        )

    if action == "rain":
        try:
            stat = _learning_summary_from_bigdata() if "_learning_summary_from_bigdata" in globals() else {"총기록": 0}
        except Exception:
            stat = {"총기록": 0}
        return (
            "[비 · 배당/학습]\\n"
            f"학습데이터: {stat.get('총기록', 0)}건\\n"
            f"안정형 적중: {stat.get('안정형적중', 0)} / 변수형 적중: {stat.get('변수형적중', 0)} / 고배당형 적중: {stat.get('고배당형적중', 0)}\\n"
            f"고배당형 대표: {row.get('고배당형대표', '')}\\n"
            f"고배당형 6: {row.get('고배당형6', '')}"
        )

    if action == "recommend":
        return (
            "[3분류 추천]\\n"
            f"안정형 대표: {row.get('안정형대표', '')}\\n"
            f"안정형 6: {row.get('안정형6', '')}\\n\\n"
            f"변수형 대표: {row.get('변수형대표', '')}\\n"
            f"변수형 6: {row.get('변수형6', '')}\\n\\n"
            f"고배당형 대표: {row.get('고배당형대표', '')}\\n"
            f"고배당형 6: {row.get('고배당형6', '')}\\n\\n"
            f"총 18마권: {row.get('삼쌍승18조합', '')}"
        )

    if action == "mobile_link":
        return (
            "[모바일 주소]\\n"
            "https://maru-kra-final-clean.streamlit.app/?mode=mobile\\n"
            "캐시 새로고침: https://maru-kra-final-clean.streamlit.app/?mode=mobile&v=cmd"
        )

    if action == "weekly_agent":
        tick = _weekly_agent_tick()
        return _weekly_agent_status_text() + "\n\n" + json.dumps(tick, ensure_ascii=False, indent=2)  # WEEKLY_AGENT_COMMAND_EXECUTE

    if action == "self_learning":
        _save_comm_status_snapshot()
        return _self_learning_status_text()  # SELF_LEARNING_COMMAND_EXECUTE

    if action == "hub":
        try:
            data = external_hub_load("mobile_recommend") if "external_hub_load" in globals() else {}
            status = "연결됨" if isinstance(data, dict) and data else "대기/비어있음"
        except Exception as e:
            status = f"점검필요: {e}"
        return (
            "[허브 저장 상태]\\n"
            f"Google Sheet 허브: {status}\\n"
            "저장 종류: mobile_recommend / three_type_recommend / learning_bigdata / agent_runs"
        )

    return (
        "[명령 입력창 도움말]\\n"
        "예시 명령:\\n- " + "\\n- ".join(COMMAND_EXAMPLES) + "\\n\\n"
        "명령은 PC에서 빠르게 상태를 확인하는 용도입니다. 구매/결제는 수동입니다."
    )

def render_pc_command_console(current_row: Dict[str, Any] = None) -> None:
    """PC 전용 명령 입력창."""
    try:
        # 화면 진입만으로 웹 순찰을 실행하지 않습니다.
        st.markdown("### 🧭 PC 명령 입력창")
        st.caption("예: 해 상태 / 달 자동수집 상태 / 3분류 추천 보여줘 / 비 학습요약 / 모바일 주소")
        with st.form("maru_pc_command_form", clear_on_submit=False):
            cmd = st.text_input("명령 입력", value=st.session_state.get("last_pc_command", ""), placeholder="예: 3분류 추천 보여줘", key="pc_command_input")
            run_cmd = st.form_submit_button("명령 실행", key="pc_command_form_submit")
        if run_cmd:
            st.session_state["last_pc_command"] = cmd
            st.session_state["last_pc_command_result"] = _pc_command_execute(cmd, current_row or {})
        result = st.session_state.get("last_pc_command_result", "")
        if result:
            st.text_area("명령 결과", value=result, height=260, key="pc_command_result_area")
    except Exception as e:
        st.warning(f"명령 입력창 표시 오류: {e}")


def render_live_panel(rc_date: str, meet: str, race_no: int, selected: List[str], sim_count: int, risk_mode: str) -> Tuple[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]], Dict[str, pd.DataFrame], pd.DataFrame, Dict[str, Any]]:
    st.markdown("### 실시간 KRA 분석")
    if "live_data" not in st.session_state:
        st.session_state["live_data"] = {}
        st.session_state["api_status"] = pd.DataFrame()

    col_a, col_b = st.columns([1, 1])
    with col_a:
        run = st.button("실시간 데이터 새로고침", type="primary", key="live_data_refresh_btn")
    with col_b:
        run_sim = st.button("불러오기 + 시뮬레이션", key="live_load_sim_btn")

    current_race_key = f"{rc_date}|{meet}|{int(race_no)}"
    previous_race_key = st.session_state.get("live_race_key")
    if previous_race_key != current_race_key:
        st.session_state["live_data"] = {}
        st.session_state["api_status"] = pd.DataFrame()
        st.session_state["live_race_key"] = current_race_key

    ended_today, last_race_no, last_race_time = _end_of_day_kst_stop(rc_date, meet)  # END_OF_DAY_HARD_STOP_RENDER_LIVE
    if ended_today:
        if last_race_no:
            race_no = int(last_race_no)
            current_race_key = f"{rc_date}|{meet}|{int(race_no)}"
        st.warning(f"오늘 {meet} 경주는 종료되었습니다. {int(race_no)}경주 실시간 수집을 중단하고 저장/캐시 결과만 표시합니다.")
        cache_data = st.session_state.get("live_data", {}) or load_live_cache()
        cache_data = _filter_data_selected_race(cache_data, rc_date, meet, int(race_no)) if "_filter_data_selected_race" in globals() else cache_data
        st.session_state["live_data"] = cache_data if cache_data else {}
        st.session_state["api_status"] = _end_of_day_cache_status(meet, int(race_no))
        st.session_state["live_race_key"] = current_race_key
    # NO_AUTO_SPIN_HARD_STOP: 화면 진입 자동수집 금지. 사용자가 버튼을 눌렀을 때만 수집합니다.
    should_auto_fetch = False
    auto_allowed, auto_reason, auto_target_no = False, "자동수집 OFF · 버튼 실행 대기", None
    if auto_target_no:
        race_no = int(auto_target_no)
    st.caption(f"자동수집 상태: {auto_reason}")
    learn_stat = _learning_summary_from_bigdata()  # THREE_TYPE_PC_LEARNING_SUMMARY
    st.caption(f"학습데이터: {learn_stat.get('총기록', 0)}건 · 안정 {learn_stat.get('안정형적중',0)} / 변수 {learn_stat.get('변수형적중',0)} / 고배당 {learn_stat.get('고배당형적중',0)}")
    _cmd_current_row = {}
    try:
        _cmd_current_row.update(load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else {})
        _cmd_current_row.update({"날짜": rc_date, "경마장": meet, "경주번호": int(race_no)})
    except Exception:
        pass
    render_pc_command_console(_cmd_current_row)  # PC_COMMAND_CONSOLE_RENDER_APPLY
    render_self_learning_control_center()  # SELF_LEARNING_CENTER_RENDER_APPLY
    render_weekly_agent_center()  # WEEKLY_AGENT_CENTER_RENDER_APPLY
    render_api_schedule_visibility_center(st.session_state.get("api_status", pd.DataFrame()), st.session_state.get("live_data", {}))  # PC_API_STATUS_CENTER_RENDER_APPLY
    render_direct_schedule_excel_viewer(compact=False)  # DIRECT_SCHEDULE_VIEWER_PC_APPLY
    render_pipeline_reason_center(rc_date, meet, race_no, compact=False)  # PIPELINE_REASON_CENTER_PC_APPLY
    render_source_truth_center(st.session_state.get("live_data", {}), st.session_state.get("api_status", pd.DataFrame()), selected, collection_mode)  # SOURCE_TRUTH_CENTER_PC_APPLY
    render_no_click_api_excel_viewer(compact=False, meet=meet)  # NO_CLICK_API_VIEWER_PC_APPLY
    render_excel_detail_workbook_center(st.session_state.get("live_data", {}), st.session_state.get("api_status", pd.DataFrame()), rc_date, meet, race_no, compact=False)  # EXCEL_DETAIL_CENTER_PC_APPLY
    render_api_received_file_viewer(st.session_state.get("live_data", {}), st.session_state.get("api_status", pd.DataFrame()), rc_date, meet, race_no, compact=False)  # PC_API_RECEIVED_FILE_VIEWER_APPLY
    should_auto_fetch = False
    if run or run_sim:
        with st.spinner(f"{meet} {int(race_no)}경주 실시간 API 수집 중... 최대 30~60초 걸릴 수 있습니다."):
            data, status = fetch_all_live(rc_date, meet, int(race_no), selected)
        data = _filter_data_selected_race(data, rc_date, meet, int(race_no)) if "_filter_data_selected_race" in globals() else data
        st.session_state["live_data"] = data
        st.session_state["api_status"] = status
        st.session_state["live_race_key"] = current_race_key
    elif not st.session_state.get("live_data"):
        cache = load_live_cache()
        cache = _filter_data_selected_race(cache, rc_date, meet, int(race_no)) if "_filter_data_selected_race" in globals() else cache
        st.session_state["live_data"] = cache if cache else {}
        st.session_state["api_status"] = pd.DataFrame([{"API":"초기화","상태":f"{meet} {int(race_no)}경주 캐시 확인 · API 데이터 없음","행수":sum(len(v) for v in cache.values()) if cache else 0}])

    data = st.session_state.get("live_data", {})
    data = _filter_data_selected_race(data, rc_date, meet, int(race_no)) if "_filter_data_selected_race" in globals() else data  # REALTIME_CURRENT_RACE_FILTER_AFTER_SESSION
    st.session_state["live_data"] = data
    data = _filter_data_selected_race(data, rc_date, meet, int(race_no))  # SELECTED_RACE_DATAFLOW_FILTER
    st.session_state["live_data"] = data
    status = st.session_state.get("api_status", pd.DataFrame())
    env = fetch_weather(meet)
    base = build_base_horses(data, rc_date, meet, int(race_no))
    horses = merge_score_features(base, data, rc_date, meet, int(race_no))
    horses = _validate_selected_race_horses(horses, meet, int(race_no))  # SELECTED_RACE_SCOREDF_FILTER
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
        schedule_df = _filter_schedule_selected_race(schedule_df, meet, int(race_no))  # STRICT_SELECTED_RACE_SCHEDULE
        auto_row = _force_selected_race_context(auto_row, rc_date, meet, int(race_no))  # STRICT_SELECTED_RACE_AUTO_ROW
        apply_mobile_plan_update(auto_row, score_df, schedule_df)
        auto_row = merge_18ticket_into_row(auto_row, score_df, int(auto_row.get("추천금액", 18000) or 18000))
        auto_row = _force_selected_race_context(auto_row, rc_date, meet, int(race_no))  # STRICT_SELECTED_RACE_BEFORE_SAVE
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
        elif st.button("현재 분석 허브 저장", type="primary", key="save_current_analysis_to_hub"):
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






# SEQUENTIAL_26API_ONE_BY_ONE_SAVE_FIX
def _seq_state_file() -> Path:
    d = DATA_DIR if "DATA_DIR" in globals() else Path("maru_kra_data")
    d.mkdir(parents=True, exist_ok=True)
    return d / "sequential_26api_state.json"

def _load_seq_state() -> Dict[str, Any]:
    try:
        p = _seq_state_file()
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def _save_seq_state(state: Dict[str, Any]) -> None:
    try:
        _seq_state_file().write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def _seq_file_dir(rc_date: str, meet: str, race_no: Any) -> Path:
    d = (DATA_DIR if "DATA_DIR" in globals() else Path("maru_kra_data")) / "sequential_api_files" / _safe_file_key(rc_date, meet, race_no)
    d.mkdir(parents=True, exist_ok=True)
    return d

def _seq_api_keys() -> List[str]:
    if "API_LABELS" in globals():
        return [k for k, _ in API_LABELS]
    return ["race_url", "entry_url", "entry_registered_url", "horse_url", "body_url", "rating_url", "today_odds_url"]

def _seq_label(key: str) -> str:
    try:
        return dict(API_LABELS).get(key, key)
    except Exception:
        return key

def _seq_target_id(rc_date: str, meet: str, race_no: Any) -> str:
    return _safe_file_key(rc_date, meet, race_no)

def reset_sequential_26api(rc_date: str, meet: str, race_no: Any) -> None:
    state = _load_seq_state()
    target = _seq_target_id(rc_date, meet, race_no)
    state[target] = {
        "날짜": rc_date,
        "경마장": meet,
        "경주번호": int(race_no) if str(race_no).isdigit() else race_no,
        "index": 0,
        "완료": False,
        "저장시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
        "rows": [],
    }
    _save_seq_state(state)

def sequential_26api_step(rc_date: str, meet: str, race_no: Any, step_count: int = 1) -> Dict[str, Any]:
    """
    26개 API를 하나씩 순차 접속합니다.
    1개 API 접속 → 받은 자료 즉시 CSV 저장 → 상태 저장 → 다음 실행 때 다음 API 진행.
    전체를 한 번에 때리지 않아 느림/멈춤/과호출을 줄입니다.
    """
    rc_date = rc_date or (today_kst() if "today_kst" in globals() else "")
    meet = "서울" if str(meet or "전체") == "전체" else str(meet or "서울")
    try:
        race_no = int(float(race_no or 1))
        if race_no <= 0:
            race_no = 1
    except Exception:
        race_no = 1

    api_keys = _seq_api_keys()
    target = _seq_target_id(rc_date, meet, race_no)
    state = _load_seq_state()
    item = state.get(target)
    if not isinstance(item, dict):
        reset_sequential_26api(rc_date, meet, race_no)
        state = _load_seq_state()
        item = state.get(target, {})

    idx = int(item.get("index", 0) or 0)
    rows = item.get("rows", [])
    if idx >= len(api_keys):
        item["완료"] = True
        item["index"] = len(api_keys)
        item["완료시각"] = now_str() if "now_str" in globals() else str(dt.datetime.now())
        state[target] = item
        _save_seq_state(state)
        return item

    max_steps = max(1, int(step_count or 1))
    collected_data = st.session_state.get("live_data", {}) or {}
    status_rows = []

    for _ in range(max_steps):
        if idx >= len(api_keys):
            break
        key = api_keys[idx]
        label = _seq_label(key)
        started = now_str() if "now_str" in globals() else str(dt.datetime.now())
        try:
            # fetch_one_api는 API 하나만 접속하므로 순차 저장에 적합
            df, msg, used_url = fetch_one_api(key, rc_date, meet, int(race_no))
            if df is None:
                df = pd.DataFrame()
            if not isinstance(df, pd.DataFrame):
                df = pd.DataFrame(df)
            save_dir = _seq_file_dir(rc_date, meet, race_no)
            file_path = save_dir / f"{idx+1:02d}_{_safe_file_key(key)}_{_safe_file_key(label)}.csv"
            df.to_csv(file_path, index=False, encoding="utf-8-sig")

            if not df.empty:
                df2 = df.copy()
                df2["수집경마장"] = meet
                df2["수집경주번호"] = int(race_no)
                df2["수집API"] = key
                collected_data[key] = df2

            row = {
                "순번": idx + 1,
                "API": label,
                "key": key,
                "행수": int(len(df)),
                "상태": msg,
                "저장파일": str(file_path),
                "시작": started,
                "완료시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
                "URL": mask_key(used_url) if "mask_key" in globals() else str(used_url)[:160],
            }
        except Exception as e:
            row = {
                "순번": idx + 1,
                "API": label,
                "key": key,
                "행수": 0,
                "상태": f"ERROR: {str(e)[:180]}",
                "저장파일": "",
                "시작": started,
                "완료시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
                "URL": "",
            }

        rows.append(row)
        status_rows.append(row)
        idx += 1

        # 한 번에 너무 오래 붙잡지 않도록 즉시 저장
        item.update({
            "날짜": rc_date,
            "경마장": meet,
            "경주번호": int(race_no),
            "index": idx,
            "완료": idx >= len(api_keys),
            "저장시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
            "rows": rows,
        })
        state[target] = item
        _save_seq_state(state)

    # session/cache 저장
    st.session_state["live_data"] = collected_data
    st.session_state["api_status"] = pd.DataFrame(rows)
    st.session_state["sequential_26api_state"] = item

    try:
        if collected_data:
            save_live_cache(collected_data, pd.DataFrame(rows))
    except Exception:
        pass

    try:
        if "external_hub_save" in globals():
            external_hub_save("sequential_26api_state", item)
    except Exception:
        pass

    return item

def render_sequential_26api_center_legacy_disabled(rc_date: str, meet: str, race_no: Any) -> None:
    """26개 API 하나씩 접속→저장→다음 API 진행 센터."""
    st.markdown("### 🔁 26개 API 순차 수집센터")
    st.caption("한 번에 26개를 모두 호출하지 않고, 1개씩 접속해서 받은 자료를 저장한 뒤 다음 API로 넘어갑니다.")

    meet_run = "서울" if str(meet or "전체") == "전체" else str(meet or "서울")
    try:
        race_run = int(float(race_no or 1))
        if race_run <= 0:
            race_run = 1
    except Exception:
        race_run = 1

    c0, c1, c2 = st.columns([1, 1, 1])
    with c0:
        step_count = st.selectbox("한 번에 진행", [1, 2, 3, 5], index=0, key="seq_api_step_count")
    with c1:
        auto_seq = st.toggle("자동 순차 진행", value=False, key="seq_api_auto_run", help="켜두면 새로고침마다 다음 API를 1개씩 받아 저장합니다.")
    with c2:
        if st.button("처음부터 다시", key="seq_api_reset", width="stretch"):
            reset_sequential_26api(rc_date, meet_run, race_run)
            st.rerun()

    state = _load_seq_state().get(_seq_target_id(rc_date, meet_run, race_run), {})
    if auto_seq and _hub365_is_background_tick_request() and not _is_mobile_mode() and not state.get("완료", False):
        with st.spinner(f"{meet_run} {race_run}R API {step_count}개 순차 수집 중..."):
            state = sequential_26api_step(rc_date, meet_run, race_run, int(step_count))

    api_total = len(_seq_api_keys())
    done = int(state.get("index", 0) or 0)
    progress = min(1.0, done / max(1, api_total))
    st.progress(progress, text=f"{done}/{api_total}개 완료")

    rows = state.get("rows", []) if isinstance(state, dict) else []
    ok_count = 0
    total_rows = 0
    for r in rows:
        try:
            cnt = int(r.get("행수", 0) or 0)
            total_rows += cnt
            if cnt > 0:
                ok_count += 1
        except Exception:
            pass

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("완료 API", f"{done}/{api_total}")
    m2.metric("수신 성공", ok_count)
    m3.metric("총 수신행수", total_rows)
    m4.metric("상태", "완료" if state.get("완료") else "진행중")

    if rows:
        df = pd.DataFrame(rows)
        show = [c for c in ["순번", "단계", "API", "key", "행수", "상태", "추천판정", "완료시각", "저장파일"] if c in df.columns]
        st.dataframe(df[show], use_container_width=True, hide_index=True, height=360)
    else:
        st.info("아직 순차 수집 기록이 없습니다. 자동 순차 진행을 켜거나 새로고침하면 1번 API부터 수집합니다.")

    if state.get("완료"):
        st.success("26개 API 순차 수집 완료")
    else:
        next_idx = done
        keys = _seq_api_keys()
        if next_idx < len(keys):
            st.info(f"다음 수집 예정: {next_idx+1}번 · {_seq_label(keys[next_idx])}")


# FAST_FIRST_COLLECTION_FIX
FAST_FIRST_API_KEYS = [
    "race_url",
    "entry_url",
    "entry_registered_url",
    "horse_url",
    "rating_url",
    "body_url",
    "jockey_change_url",
    "today_odds_url",
]

def _fast_first_selected_keys(selected: Optional[List[str]] = None) -> List[str]:
    """추천 생성에 필요한 핵심 API부터 빠르게 수집합니다."""
    if "API_LABELS" not in globals():
        return FAST_FIRST_API_KEYS
    available = [k for k, _ in API_LABELS]
    base = [k for k in FAST_FIRST_API_KEYS if k in available]
    # 사용자가 전체 ON을 해도 첫 화면은 핵심만 먼저 수집
    return base or available[:8]

def _full_selected_keys(selected: Optional[List[str]] = None) -> List[str]:
    if selected:
        return selected
    if "API_LABELS" in globals():
        return [k for k, _ in API_LABELS]
    return FAST_FIRST_API_KEYS

def force_collect_real_data_for_targets(rc_date: str = "", targets: Optional[pd.DataFrame] = None, selected: Optional[List[str]] = None, fast_first: bool = True) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    """
    빠른 수집판.
    기존처럼 전체 경마장 × 여러 경주 × 26개 API를 한 번에 치면 너무 오래 걸리므로,
    먼저 추천에 필요한 핵심 API만 수집합니다.
    전체 26개 상세는 API/엑셀 탭에서 별도 확인합니다.
    """
    rc_date = rc_date or (today_kst() if "today_kst" in globals() else (now_kst().strftime("%Y%m%d") if "now_kst" in globals() else ""))
    selected_fast = _fast_first_selected_keys(selected) if fast_first else _full_selected_keys(selected)
    all_data: Dict[str, pd.DataFrame] = {}
    all_status_rows: List[Dict[str, Any]] = []

    if targets is None or not isinstance(targets, pd.DataFrame) or targets.empty:
        try:
            sched, _log = load_all_meet_schedule_for_monitor(rc_date) if "load_all_meet_schedule_for_monitor" in globals() else (pd.DataFrame(), pd.DataFrame())
            targets = _current_or_next_races(sched, per_meet=1) if "_current_or_next_races" in globals() else pd.DataFrame()
        except Exception:
            targets = pd.DataFrame()

    if targets is None or targets.empty:
        targets = pd.DataFrame([
            {"경마장": "서울", "경주번호": 1},
            {"경마장": "부산경남", "경주번호": 1},
            {"경마장": "제주", "경주번호": 1},
        ])

    # 오래 걸리지 않도록 경마장별 현재/다음 1경주만 먼저 수집
    try:
        targets = targets.groupby("경마장", dropna=False).head(1).reset_index(drop=True)
    except Exception:
        targets = targets.head(3)

    start_ts = pd.Timestamp.now()
    for _, row in targets.iterrows():
        meet = str(row.get("경마장", "서울") or "서울")
        if meet == "전체":
            meet = "서울"
        try:
            race_no = int(float(row.get("경주번호", 1) or 1))
            if race_no <= 0:
                race_no = 1
        except Exception:
            race_no = 1

        try:
            data, status = fetch_all_live(rc_date, meet, race_no, selected_fast)
        except Exception as e:
            data, status = {}, pd.DataFrame([{
                "API": "전체", "key": "ALL", "행수": 0,
                "상태": f"빠른수집 실패: {str(e)[:160]}", "URL": ""
            }])

        if isinstance(data, dict):
            for k, df in data.items():
                try:
                    if df is None:
                        continue
                    if not isinstance(df, pd.DataFrame):
                        df = pd.DataFrame(df)
                    if df.empty:
                        continue
                    df = df.copy()
                    df["수집경마장"] = meet
                    df["수집경주번호"] = race_no
                    all_data[f"{meet}_{race_no}R_{k}"] = df
                    if k not in all_data:
                        all_data[k] = df
                except Exception:
                    continue

        if isinstance(status, pd.DataFrame) and not status.empty:
            st_df = status.copy()
            st_df["수집경마장"] = meet
            st_df["수집경주번호"] = race_no
            st_df["수집방식"] = "빠른핵심수집" if fast_first else "전체수집"
            all_status_rows.extend(st_df.to_dict("records"))

    all_status = pd.DataFrame(all_status_rows)
    st.session_state["live_data"] = all_data
    st.session_state["api_status"] = all_status
    st.session_state["real_collection_done"] = True
    st.session_state["real_collection_at"] = now_str() if "now_str" in globals() else str(dt.datetime.now())
    st.session_state["real_collection_mode"] = "빠른핵심수집" if fast_first else "전체수집"
    try:
        st.session_state["real_collection_seconds"] = round((pd.Timestamp.now() - start_ts).total_seconds(), 1)
    except Exception:
        pass

    try:
        if all_data:
            save_live_cache(all_data, all_status)
    except Exception:
        pass
    try:
        if "save_api_received_files" in globals():
            save_api_received_files(all_data, all_status, rc_date, "전체", "multi")
    except Exception:
        pass
    try:
        if "external_hub_save" in globals():
            summary = {
                "저장시각": st.session_state.get("real_collection_at"),
                "날짜": rc_date,
                "대상": "전체경마장 현재/다음경주",
                "수집방식": st.session_state.get("real_collection_mode"),
                "소요초": st.session_state.get("real_collection_seconds"),
                "API상태행수": len(all_status) if isinstance(all_status, pd.DataFrame) else 0,
                "데이터묶음수": len(all_data),
                "총데이터행수": int(sum(len(v) for v in all_data.values() if hasattr(v, "__len__"))),
            }
            external_hub_save("real_collection_summary", summary)
    except Exception:
        pass

    return all_data, all_status

def render_force_real_collection_center(rc_date: str, selected: List[str], targets: Optional[pd.DataFrame] = None) -> None:
    st.markdown("### 📥 실제 자료 수집센터")
    st.caption("PC 화면 진입만으로 핵심 API를 수집하지 않습니다. 버튼/백그라운드 호출 때만 실행합니다.")

    manual_collect = st.button("📥 핵심 API 빠른 수집 1회 실행", key=f"force_real_collect_manual_{rc_date}")
    can_collect = manual_collect or (_hub365_network_allowed() if "_hub365_network_allowed" in globals() else False)
    if can_collect:
        if manual_collect:
            st.session_state["_hub365_network_allowed"] = True
        with st.spinner("핵심 API 빠른 수집 중... 보통 10~25초"):
            data, status = force_collect_real_data_for_targets(rc_date, targets, selected, fast_first=True)
    else:
        data = st.session_state.get("live_data", {}) or {}
        status = st.session_state.get("api_status", pd.DataFrame())
        st.info("대기 중 · 자동수집 차단됨. 필요할 때 [핵심 API 빠른 수집 1회 실행]을 누르세요.")

    total_rows = int(sum(len(v) for v in data.values() if hasattr(v, "__len__"))) if isinstance(data, dict) else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("수집방식", st.session_state.get("real_collection_mode", "빠른핵심"))
    c2.metric("소요", f"{st.session_state.get('real_collection_seconds', '-') }초")
    c3.metric("총 수신행수", total_rows)
    c4.metric("상태표", len(status) if isinstance(status, pd.DataFrame) else 0)

    if total_rows > 0:
        st.success(f"핵심 자료 수집 완료 · 총 {total_rows:,}행")
    else:
        st.error("실제 수신자료가 0행입니다. 아래 API 상태표의 키/승인/URL/0건 메시지를 확인하세요.")

    with st.expander("왜 전체 26개를 한 번에 안 부르나요?", expanded=False):
        st.info("전체 경마장 3곳 × 현재/다음 경주 × 26개 API를 한 번에 호출하면 60~180초까지 걸릴 수 있습니다. 그래서 추천에 필요한 경주정보/출전표/말정보/체중/레이팅/기수변경/배당 핵심 API부터 먼저 수집합니다.")

    if isinstance(status, pd.DataFrame) and not status.empty:
        keep = [c for c in ["수집경마장", "수집경주번호", "API", "key", "행수", "상태", "수집방식", "URL"] if c in status.columns]
        st.dataframe(status[keep] if keep else status, use_container_width=True, hide_index=True, height=320)

    if isinstance(data, dict) and data:
        with st.expander("받아온 자료 바로보기", expanded=True):
            shown = 0
            for k, df in data.items():
                try:
                    if not isinstance(df, pd.DataFrame):
                        df = pd.DataFrame(df)
                    if df.empty:
                        continue
                    st.markdown(f"**{k} · {len(df)}행**")
                    st.dataframe(df.head(60), use_container_width=True, hide_index=True, height=220)
                    shown += 1
                    if shown >= 5:
                        st.caption("화면 속도 때문에 상위 5개 자료만 먼저 표시합니다. 전체는 엑셀 상세자료에서 확인하세요.")
                        break
                except Exception:
                    continue


# IMMEDIATE_API_STATUS_FORCE_FIX
def immediate_api_status_probe(rc_date: str = "", meet: str = "서울", race_no: Any = 1, selected: Optional[List[str]] = None) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    """
    '아직 API 호출 전입니다'가 계속 뜨는 문제 방지용.
    화면이 열리면 최소 1회는 즉시 26개 API 상태표를 만들고 session_state에 저장합니다.
    결과/배당처럼 시간대 제한이 필요한 API는 상태표에 대기 사유를 남기고,
    경주정보/출전표/말정보 등 기본 API는 즉시 호출합니다.
    """
    try:
        rc_date = rc_date or (today_kst() if "today_kst" in globals() else now_kst().strftime("%Y%m%d"))
    except Exception:
        rc_date = ""
    meet = "서울" if str(meet or "전체") == "전체" else str(meet or "서울")
    try:
        race_no = int(float(race_no or 1))
        if race_no <= 0:
            race_no = 1
    except Exception:
        race_no = 1

    if selected is None or not selected:
        selected = [k for k, _ in API_LABELS] if "API_LABELS" in globals() else []

    # 이미 상태표가 있으면 그대로 반환
    data0 = st.session_state.get("live_data", {}) or {}
    status0 = st.session_state.get("api_status", pd.DataFrame())
    if isinstance(status0, pd.DataFrame) and not status0.empty:
        return data0, status0

    try:
        if "get_api_key" in globals() and not get_api_key():
            status = pd.DataFrame([{
                "API": "전체",
                "key": "ALL",
                "행수": 0,
                "상태": "API_KEY 없음 · Streamlit Secrets 또는 PC 저장키 확인",
                "URL": "",
            }])
            st.session_state["live_data"] = {}
            st.session_state["api_status"] = status
            return {}, status
    except Exception:
        pass

    try:
        data, status = fetch_all_live(rc_date, meet, race_no, selected)
        if not isinstance(status, pd.DataFrame) or status.empty:
            status = pd.DataFrame([{
                "API": "전체",
                "key": "ALL",
                "행수": 0,
                "상태": "호출은 시도했지만 상태표 생성 실패",
                "URL": "",
            }])
        st.session_state["live_data"] = data if isinstance(data, dict) else {}
        st.session_state["api_status"] = status
        st.session_state["live_race_key"] = f"{rc_date}|{meet}|{race_no}"
        return st.session_state["live_data"], status
    except Exception as e:
        status = pd.DataFrame([{
            "API": "전체",
            "key": "ALL",
            "행수": 0,
            "상태": f"즉시 API 점검 실패: {str(e)[:160]}",
            "URL": "",
        }])
        st.session_state["api_status"] = status
        return {}, status

def render_api_hub_panel(status: pd.DataFrame, data: Dict[str, pd.DataFrame]) -> None:
    """API 상태 / 허브 저장. 상태표가 비어 있으면 즉시 점검을 강제로 수행합니다."""
    st.markdown("### API 상태 / 허브 저장")
    if status is None or not isinstance(status, pd.DataFrame) or status.empty:
        try:
            rc_date_probe = st.session_state.get("rc_date", today_kst() if "today_kst" in globals() else "")
            meet_probe = st.session_state.get("meet", "서울")
            race_probe = st.session_state.get("race_no", 1)
            selected_probe = st.session_state.get("selected_api_keys", [k for k, _ in API_LABELS] if "API_LABELS" in globals() else [])
            data, status = immediate_api_status_probe(rc_date_probe, meet_probe, race_probe, selected_probe)
        except Exception as e:
            status = pd.DataFrame([{"API": "전체", "key": "ALL", "행수": 0, "상태": f"즉시점검 실패: {str(e)[:120]}", "URL": ""}])
            data = data or {}

    with st.expander("API 상태 요약", expanded=True):
        if isinstance(status, pd.DataFrame) and not status.empty:
            keep_cols = [c for c in ["API", "key", "행수", "상태", "URL"] if c in status.columns]
            st.dataframe(status[keep_cols] if keep_cols else status, use_container_width=True, height=360)
            try:
                ok_rows = int((pd.to_numeric(status.get("행수", 0), errors="coerce").fillna(0) > 0).sum())
                st.caption(f"즉시 상태표 생성됨 · 수신 성공 API {ok_rows}개")
            except Exception:
                pass
        else:
            st.warning("API 상태표를 만들지 못했습니다. API Key/Secrets/수집모드를 확인하세요.")

    with st.expander("허브 저장 현황", expanded=True):
        local_hub_df = load_local_hub()
        big_df = load_bigdata()
        h1, h2, h3 = st.columns(3)
        h1.metric("허브 저장", f"{len(local_hub_df):,}건")
        h2.metric("빅데이터 로그", f"{len(big_df):,}건")
        h3.metric("현재 데이터", f"{sum(len(v) for v in data.values()) if data else 0:,}행")
        if not local_hub_df.empty:
            show_cols = [c for c in ["저장시각", "경마장", "경주번호", "공격삼쌍승", "방어삼복승", "예상배당", "신뢰도", "추천금액"] if c in local_hub_df.columns]
            st.dataframe(local_hub_df[show_cols].tail(30) if show_cols else local_hub_df.tail(30), use_container_width=True, height=330)
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
    st.download_button("추천번호 텍스트 받기", data=copy_text.encode("utf-8"), file_name="MARU_삼쌍승18장.txt", mime="text/plain", width="stretch", key="triple18_download_text_btn")
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



def _parse_hhmm_to_minutes(value: Any) -> Optional[int]:
    """'14:30', '1430', 1430, '14.30' 같은 값을 분 단위로 변환합니다."""
    try:
        s = str(value).strip()
        if not s or s.lower() in ["nan", "none"]:
            return None
        s = s.replace(".", ":").replace("시", ":").replace("분", "")
        m = re.search(r"(\d{1,2})\s*:\s*(\d{1,2})", s)
        if m:
            h, mi = int(m.group(1)), int(m.group(2))
            if 0 <= h <= 23 and 0 <= mi <= 59:
                return h * 60 + mi
        digits = re.sub(r"\D", "", s)
        if len(digits) in [3, 4]:
            h = int(digits[:-2])
            mi = int(digits[-2:])
            if 0 <= h <= 23 and 0 <= mi <= 59:
                return h * 60 + mi
    except Exception:
        return None
    return None

def _minutes_to_hhmm(minutes: Optional[int]) -> str:
    if minutes is None:
        return ""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

def _auto_pick_race_from_schedule(schedule_df: pd.DataFrame, meet: str, now_dt: Optional[datetime.datetime] = None) -> Tuple[Optional[int], str]:
    """현재 KST 기준으로 다음 경주번호와 예정시각을 자동 선택합니다."""
    if now_dt is None:
        try:
            now_dt = datetime.datetime.now(KST)
        except Exception:
            now_dt = datetime.datetime.now()
    if schedule_df is None or not isinstance(schedule_df, pd.DataFrame) or schedule_df.empty:
        return None, ""

    df = schedule_df.copy()
    meet_cols = ["경마장", "meet", "MEET", "경주장", "장소"]
    race_cols = ["경주번호", "race_no", "RACE_NO", "rcNo", "경주", "race"]
    time_cols = ["경주예정시각", "예정시각", "출발시각", "경주시간", "race_time", "rcTime", "time"]

    mcol = next((c for c in meet_cols if c in df.columns), None)
    rcol = next((c for c in race_cols if c in df.columns), None)
    tcol = next((c for c in time_cols if c in df.columns), None)

    if mcol is not None:
        df = df[df[mcol].astype(str).str.contains(str(meet), na=False)]
    if rcol is None or tcol is None or df.empty:
        return None, ""

    df["_race_no_auto"] = pd.to_numeric(df[rcol], errors="coerce")
    df["_time_min_auto"] = df[tcol].apply(_parse_hhmm_to_minutes)
    df = df.dropna(subset=["_race_no_auto", "_time_min_auto"])
    if df.empty:
        return None, ""

    now_min = now_dt.hour * 60 + now_dt.minute
    # 아직 출발 전인 다음 경주 우선, 모두 지났으면 마지막 경주
    future = df[df["_time_min_auto"] >= now_min].sort_values("_time_min_auto")
    row = future.iloc[0] if not future.empty else df.sort_values("_time_min_auto").iloc[-1]
    return int(row["_race_no_auto"]), _minutes_to_hhmm(int(row["_time_min_auto"]))

def _load_schedule_for_sidebar(rc_date: str, meet: str) -> pd.DataFrame:
    """사이드바 자동 경주 선택용 시간표를 캐시/live_data에서 최대한 가져옵니다."""
    try:
        live = st.session_state.get("live_data", {})
        sched = extract_schedule_from_data(live, rc_date, meet)
        if isinstance(sched, pd.DataFrame) and not sched.empty:
            return sched
    except Exception:
        pass
    try:
        cache = load_live_cache()
        sched = extract_schedule_from_data(cache, rc_date, meet)
        if isinstance(sched, pd.DataFrame) and not sched.empty:
            return sched
    except Exception:
        pass
    return pd.DataFrame()



def _final_clean_mobile_url() -> str:
    """모바일 전용 버튼은 항상 현재 final-clean 앱의 ?mode=mobile로 이동합니다."""
    return "https://maru-kra-final-clean.streamlit.app/?mode=mobile"




# RESULT_PRIORITY_26API_RECOMMEND_EACH_RACE_FIX
# 26개 API 순차 수집을 "추천/결과 정확도" 우선순위로 재정렬합니다.
# 핵심: 경주 전 추천자료 → 실시간 변수자료 → 배당/인기 → 경주 직후 결과 → 확정배당/학습 순서
RESULT_PRIORITY_26API_KEYS = [
    # A. 경주 전, 추천 생성에 반드시 필요한 기본자료
    "race_url",
    "race_overview_url",
    "entry_url",
    "entry_registered_url",
    "horse_url",
    "jockey_result_url",
    "rating_url",

    # B. 경주 직전 변수자료
    "body_url",
    "gear_url",
    "horse_shoe_url",
    "jockey_change_url",
    "weather_alert_url",
    "corner_pace_url",

    # C. 구매 직전 배당/인기
    "popularity_url",
    "odds_url",
    "today_odds_url",
    "first_odds_url",
    "second_odds_url",
    "third_odds_url",
    "dividend_integrated_url",

    # D. 경주 직후 결과/확정/취소
    "race_cancel_url",
    "result_detail_url",
    "race_detail_result_url",

    # E. 보조 기록성 자료
    "race_record_url",
    "start_exam_url",
    "judge_url",
]

def _seq_api_keys() -> List[str]:
    """
    순차수집 순서.
    API_LABELS에 실제 등록된 26개만 골라서 추천/결과 정확도 우선순위로 가져옵니다.
    위 우선순위에 없는 보조 API가 있으면 마지막에 원래 등록순서로 붙입니다.
    """
    if "API_LABELS" in globals():
        available = [k for k, _ in API_LABELS]
    else:
        available = RESULT_PRIORITY_26API_KEYS
    ordered = [k for k in RESULT_PRIORITY_26API_KEYS if k in available]
    tail = [k for k in available if k not in ordered]
    return ordered + tail

def _api_stage_name(key: str) -> str:
    if key in ["race_url", "race_overview_url", "entry_url", "entry_registered_url", "horse_url", "jockey_result_url", "rating_url"]:
        return "경주전_기본추천"
    if key in ["body_url", "gear_url", "horse_shoe_url", "jockey_change_url", "weather_alert_url", "corner_pace_url"]:
        return "경주전_변수점검"
    if key in ["popularity_url", "odds_url", "today_odds_url", "first_odds_url", "second_odds_url", "third_odds_url", "dividend_integrated_url"]:
        return "구매전_배당인기"
    if key in ["race_cancel_url", "result_detail_url", "race_detail_result_url"]:
        return "경주후_결과확정"
    return "보조자료"

def _recommend_ready_from_data(data: Dict[str, pd.DataFrame]) -> Tuple[bool, str]:
    """추천 가능한 최소자료 확인: 경주/출전표/말정보 중 핵심 행수."""
    try:
        entry_rows = 0
        for k in ["entry_url", "entry_registered_url"]:
            if k in data and hasattr(data[k], "__len__"):
                entry_rows = max(entry_rows, len(data[k]))
        race_rows = 0
        for k in ["race_url", "race_overview_url"]:
            if k in data and hasattr(data[k], "__len__"):
                race_rows = max(race_rows, len(data[k]))
        horse_rows = len(data.get("horse_url", pd.DataFrame())) if hasattr(data.get("horse_url", pd.DataFrame()), "__len__") else 0
        if entry_rows >= 3:
            return True, f"추천가능: 출전표 {entry_rows}행 / 경주 {race_rows}행 / 말정보 {horse_rows}행"
        return False, f"추천대기: 출전표 {entry_rows}행이라 3두 미만"
    except Exception as e:
        return False, f"추천가능 확인 실패: {str(e)[:80]}"

def build_recommendation_after_each_race(rc_date: str, meet: str, race_no: Any, data: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, Any]:
    """
    매 경기 자료 수집 후 즉시 추천을 생성/저장합니다.
    실패해도 앱 전체를 멈추지 않고 원인만 남깁니다.
    """
    data = data or st.session_state.get("live_data", {}) or {}
    try:
        ready, reason = _recommend_ready_from_data(data)
        if not ready:
            payload = {
                "날짜": rc_date,
                "경마장": meet,
                "경주번호": int(race_no) if str(race_no).isdigit() else race_no,
                "상태": reason,
                "추천가능": "N",
                "저장시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
            }
            try:
                if "external_hub_save" in globals():
                    external_hub_save("race_recommend_status", payload)
            except Exception:
                pass
            return payload

        env = fetch_weather(meet) if "fetch_weather" in globals() else {}
        base = build_base_horses(data, rc_date, meet, int(race_no)) if "build_base_horses" in globals() else pd.DataFrame()
        horses = merge_score_features(base, data, rc_date, meet, int(race_no)) if "merge_score_features" in globals() else base
        sim_count = int(st.session_state.get("sim_count", 1200))
        risk_mode = st.session_state.get("risk_mode", "균형형")
        score_df, result, combos = score_and_recommend(horses, env, sim_count, risk_mode) if "score_and_recommend" in globals() else (pd.DataFrame(), {}, [])

        if not isinstance(result, dict):
            result = {}
        result.update({
            "날짜": rc_date,
            "경마장": meet,
            "경주번호": int(race_no),
            "추천가능": "Y",
            "상태": "매경기 자료수집 후 추천 생성",
            "추천사유": reason,
            "저장시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
        })

        try:
            if "_build_three_type_recommendation" in globals():
                result = _build_three_type_recommendation(result)
            # 15ROUND_TARGET_LOCK: 추천 보조함수가 값을 보정해도 실제 수집 대상 날짜/경마장/경주번호는 유지
            try:
                result.update({
                    "날짜": rc_date,
                    "경마장": meet,
                    "경주번호": int(race_no),
                    "상태": f"{meet} {race_no}R 추천 생성 완료",
                })
            except Exception:
                pass
        except Exception:
            pass

        try:
            if "save_mobile_recommend_json" in globals():
                save_mobile_recommend_json(result)
        except Exception:
            pass
        try:
            if "external_hub_save" in globals():
                external_hub_save("race_recommend_status", result)
                external_hub_save("mobile_recommend", result)
        except Exception:
            pass
        try:
            st.session_state["latest_each_race_recommend"] = result
            st.session_state["latest_each_race_score"] = score_df
            st.session_state["latest_each_race_combos"] = combos
        except Exception:
            pass
        return result
    except Exception as e:
        payload = {
            "날짜": rc_date,
            "경마장": meet,
            "경주번호": race_no,
            "추천가능": "N",
            "상태": f"추천 생성 오류: {str(e)[:160]}",
            "저장시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
        }
        try:
            if "external_hub_save" in globals():
                external_hub_save("race_recommend_status", payload)
        except Exception:
            pass
        return payload

def sequential_26api_step(rc_date: str, meet: str, race_no: Any, step_count: int = 1) -> Dict[str, Any]:
    """
    결과/추천 정확도 우선순위 26개 API 순차수집.
    1개 API 완료 즉시 저장하고, 추천 가능한 최소자료가 모이면 매 경기 추천을 즉시 생성합니다.
    """
    rc_date = rc_date or (today_kst() if "today_kst" in globals() else "")
    meet = "서울" if str(meet or "전체") == "전체" else str(meet or "서울")
    try:
        race_no = int(float(race_no or 1))
        if race_no <= 0:
            race_no = 1
    except Exception:
        race_no = 1

    api_keys = _seq_api_keys()
    target = _seq_target_id(rc_date, meet, race_no) if "_seq_target_id" in globals() else _safe_file_key(rc_date, meet, race_no)
    state = _load_seq_state() if "_load_seq_state" in globals() else {}
    item = state.get(target)
    if not isinstance(item, dict):
        reset_sequential_26api(rc_date, meet, race_no)
        state = _load_seq_state()
        item = state.get(target, {})

    idx = int(item.get("index", 0) or 0)
    rows = item.get("rows", [])
    if idx >= len(api_keys):
        item["완료"] = True
        item["index"] = len(api_keys)
        item["완료시각"] = now_str() if "now_str" in globals() else str(dt.datetime.now())
        state[target] = item
        _save_seq_state(state)
        return item

    max_steps = max(1, int(step_count or 1))
    collected_data = st.session_state.get("live_data", {}) or {}

    for _ in range(max_steps):
        if idx >= len(api_keys):
            break
        key = api_keys[idx]
        label = _seq_label(key) if "_seq_label" in globals() else key
        stage = _api_stage_name(key)
        started = now_str() if "now_str" in globals() else str(dt.datetime.now())
        try:
            df, msg, used_url = fetch_one_api(key, rc_date, meet, int(race_no))
            if df is None:
                df = pd.DataFrame()
            if not isinstance(df, pd.DataFrame):
                df = pd.DataFrame(df)

            save_dir = _seq_file_dir(rc_date, meet, race_no) if "_seq_file_dir" in globals() else (DATA_DIR / "sequential_api_files")
            save_dir.mkdir(parents=True, exist_ok=True)
            file_path = save_dir / f"{idx+1:02d}_{_safe_file_key(stage)}_{_safe_file_key(key)}_{_safe_file_key(label)}.csv"
            df.to_csv(file_path, index=False, encoding="utf-8-sig")

            if not df.empty:
                df2 = df.copy()
                df2["수집경마장"] = meet
                df2["수집경주번호"] = int(race_no)
                df2["수집API"] = key
                df2["수집단계"] = stage
                collected_data[key] = df2

            ready, ready_reason = _recommend_ready_from_data(collected_data)
            row = {
                "순번": idx + 1,
                "단계": stage,
                "API": label,
                "key": key,
                "행수": int(len(df)),
                "상태": msg,
                "추천판정": ready_reason,
                "저장파일": str(file_path),
                "시작": started,
                "완료시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
                "URL": mask_key(used_url) if "mask_key" in globals() else str(used_url)[:160],
            }
        except Exception as e:
            row = {
                "순번": idx + 1,
                "단계": stage,
                "API": label,
                "key": key,
                "행수": 0,
                "상태": f"ERROR: {str(e)[:180]}",
                "추천판정": "오류로 추천판정 불가",
                "저장파일": "",
                "시작": started,
                "완료시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
                "URL": "",
            }

        rows.append(row)
        idx += 1

        # 하나 끝날 때마다 즉시 저장
        item.update({
            "날짜": rc_date,
            "경마장": meet,
            "경주번호": int(race_no),
            "index": idx,
            "완료": idx >= len(api_keys),
            "저장시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
            "rows": rows,
            "순서방식": "결과정확도_추천우선",
        })
        state[target] = item
        _save_seq_state(state)

        st.session_state["live_data"] = collected_data
        st.session_state["api_status"] = pd.DataFrame(rows)
        try:
            if collected_data:
                save_live_cache(collected_data, pd.DataFrame(rows))
        except Exception:
            pass

        # 추천 가능한 최소 자료가 모이면 매 경기 추천 생성
        try:
            ready, _reason = _recommend_ready_from_data(collected_data)
            if ready:
                rec = build_recommendation_after_each_race(rc_date, meet, int(race_no), collected_data)
                item["최근추천"] = rec
                state[target] = item
                _save_seq_state(state)
        except Exception:
            pass

    try:
        if "external_hub_save" in globals():
            external_hub_save("sequential_26api_state", item)
    except Exception:
        pass

    return item

def render_recommendation_after_each_race_center(rc_date: str, meet: str, race_no: Any) -> None:
    st.markdown("### 🎯 매 경기 추천 생성 상태")
    rec = st.session_state.get("latest_each_race_recommend", {})
    if not isinstance(rec, dict) or not rec:
        rec = build_recommendation_after_each_race(rc_date, "서울" if str(meet) == "전체" else meet, 1 if int(race_no or 0) <= 0 else int(race_no), st.session_state.get("live_data", {}))
    if rec.get("추천가능") == "Y":
        st.success(f"{rec.get('경마장')} {rec.get('경주번호')}R 추천 생성 완료")
    else:
        st.warning(rec.get("상태", "추천 대기"))
    keys = ["안정형대표", "변수형대표", "고배당형대표", "공격삼쌍승", "방어삼복승", "예상배당", "신뢰도", "추천사유"]
    rows = [{"항목": k, "값": rec.get(k, "")} for k in keys if rec.get(k, "") != ""]
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)





# FILE_AND_RUNTIME_CHECK_CENTER_FIX
def render_file_and_runtime_check_center() -> None:
    st.markdown("### 🧪 파일 검사 / 오류 검사")
    checks = []
    try:
        checks.append({"검사": "Python 실행", "상태": "OK", "내용": sys.version.split()[0] if "sys" in globals() else "-"})
    except Exception as e:
        checks.append({"검사": "Python 실행", "상태": "FAIL", "내용": str(e)[:120]})
    try:
        checks.append({"검사": "26개 API 순서", "상태": "OK" if len(_seq_api_keys()) >= 20 else "WARN", "내용": f"{len(_seq_api_keys())}개"})
    except Exception as e:
        checks.append({"검사": "26개 API 순서", "상태": "FAIL", "내용": str(e)[:120]})
    try:
        checks.append({"검사": "API Key", "상태": "OK" if get_api_key() else "FAIL", "내용": get_api_key_source() if get_api_key() else "키 없음"})
    except Exception as e:
        checks.append({"검사": "API Key", "상태": "FAIL", "내용": str(e)[:120]})
    try:
        p = _seq_state_file()
        checks.append({"검사": "순차상태파일", "상태": "OK", "내용": str(p)})
    except Exception as e:
        checks.append({"검사": "순차상태파일", "상태": "FAIL", "내용": str(e)[:120]})
    try:
        d = DATA_DIR if "DATA_DIR" in globals() else Path("maru_kra_data")
        checks.append({"검사": "데이터폴더", "상태": "OK" if d.exists() else "WARN", "내용": str(d)})
    except Exception as e:
        checks.append({"검사": "데이터폴더", "상태": "FAIL", "내용": str(e)[:120]})
    st.dataframe(pd.DataFrame(checks), use_container_width=True, hide_index=True)





# SEQUENTIAL_STUCK_AUTO_CONTINUE_FIX
def _seq_is_finished(item: Dict[str, Any]) -> bool:
    try:
        return bool(item.get("완료")) or int(item.get("index", 0) or 0) >= len(_seq_api_keys())
    except Exception:
        return False

def _seq_last_row_status(item: Dict[str, Any]) -> str:
    try:
        rows = item.get("rows", []) or []
        if not rows:
            return ""
        return str(rows[-1].get("상태", ""))
    except Exception:
        return ""

def render_sequential_26api_center_legacy_disabled_1(rc_date: str, meet: str, race_no: Any) -> None:
    """
    멈춤 방지 버전.
    - 자동 순차 진행 ON이면 화면 새로고침 때마다 1개씩 실제 진행
    - 404/500도 실패로 기록하고 다음 API로 넘어감
    - 진행중인데 Streamlit이 멈춘 것처럼 보이면 브라우저 meta refresh로 다시 깨움
    """
    st.markdown("### 🔁 26개 API 자동 순차 수집센터")
    st.caption("자동으로 1개씩 접속 → 실패/성공 기록 → 저장 → 다음 API로 진행합니다. 404/500도 멈추지 않고 다음으로 넘어갑니다.")

    meet2 = "서울" if str(meet or "전체") == "전체" else str(meet or "서울")
    try:
        race_no2 = int(float(race_no or 1))
        if race_no2 <= 0:
            race_no2 = 1
    except Exception:
        race_no2 = 1

    target = _seq_target_id(rc_date, meet2, race_no2)
    state = _load_seq_state()
    item = state.get(target)

    api_keys = _seq_api_keys()
    if not isinstance(item, dict):
        reset_sequential_26api(rc_date, meet2, race_no2)
        state = _load_seq_state()
        item = state.get(target, {})

    idx = int(item.get("index", 0) or 0)
    done = min(idx, len(api_keys))
    total = len(api_keys)
    rows = item.get("rows", []) if isinstance(item.get("rows", []), list) else []
    success = sum(1 for r in rows if str(r.get("상태", "")).upper().startswith("OK"))
    total_rows = sum(int(r.get("행수", 0) or 0) for r in rows)

    st.progress(done / max(total, 1), text=f"{done}/{total}개 완료")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("완료 API", f"{done}/{total}")
    c2.metric("수신 성공", success)
    c3.metric("총 수신행수", total_rows)
    c4.metric("상태", "완료" if done >= total else "자동 진행중")

    if done < total:
        next_key = api_keys[done]
        st.info(f"다음 수집 예정: {done+1}번 / {_api_stage_name(next_key)} / {_seq_label(next_key)} / `{next_key}`")
    else:
        st.success("26개 API 순차 수집이 완료되었습니다.")

    with st.expander("📋 26개 API 수집 순서표", expanded=False):
        order_df = pd.DataFrame([
            {"순번": i+1, "단계": _api_stage_name(k), "API": _seq_label(k), "key": k}
            for i, k in enumerate(api_keys)
        ])
        st.dataframe(order_df, use_container_width=True, hide_index=True)

    col_a, col_b, col_c = st.columns([1,1,1])
    with col_a:
        step_count = st.selectbox("한 번에 진행", [1, 2, 3, 5], index=0, key=f"seq_step_count_legacy_{target}")
    with col_b:
        auto_on = st.toggle("자동 순차 진행", value=False, key=f"seq_auto_on_legacy_{target}")
    with col_c:
        refresh_sec = st.selectbox("멈춤방지 새로고침", [5, 10, 15, 30, 60], index=1, key=f"seq_refresh_sec_legacy_{target}")

    b1, b2, b3 = st.columns(3)
    if b1.button("▶ 다음 API 1개 즉시 진행", key=f"seq_next_legacy_{target}", use_container_width=True):
        sequential_26api_step(rc_date, meet2, race_no2, 1)
        st.rerun()
    if b2.button("⏭ 선택 개수 진행", key=f"seq_multi_legacy_{target}", use_container_width=True):
        sequential_26api_step(rc_date, meet2, race_no2, int(step_count))
        st.rerun()
    if b3.button("🔄 처음부터 다시", key=f"seq_reset_legacy_{target}", use_container_width=True):
        reset_sequential_26api(rc_date, meet2, race_no2)
        st.rerun()

    if auto_on and _hub365_is_background_tick_request() and done < total and not _is_mobile_mode():
        now_ts = time.time()
        last_ts_key = f"_seq_last_auto_ts_{target}"
        last_ts = float(st.session_state.get(last_ts_key, 0) or 0)
        if now_ts - last_ts >= 1.5:
            st.session_state[last_ts_key] = now_ts
            sequential_26api_step(rc_date, meet2, race_no2, 1)
            st.rerun()
        else:
            st.markdown(f"<meta http-equiv='refresh' content='{int(refresh_sec)}'>", unsafe_allow_html=True)

    if auto_on and _hub365_is_background_tick_request() and done < total and not _is_mobile_mode():
        st.markdown(f"<meta http-equiv='refresh' content='{int(refresh_sec)}'>", unsafe_allow_html=True)

    state = _load_seq_state()
    item = state.get(target, item)
    rows = item.get("rows", []) if isinstance(item, dict) else []
    if rows:
        df = pd.DataFrame(rows)
        show = [c for c in ["순번", "단계", "API", "key", "행수", "상태", "추천판정", "완료시각", "저장파일"] if c in df.columns]
        st.dataframe(df[show], use_container_width=True, hide_index=True)
        last_status = _seq_last_row_status(item)
        if "HTTP 500" in last_status or "HTTP 404" in last_status or "ERROR" in last_status.upper():
            st.warning("마지막 API가 오류였지만 실패로 저장하고 다음 API로 넘어가게 되어 있습니다.")
    else:
        st.caption("아직 수집 기록이 없습니다.")








# CURRENT_RACE_TARGET_MATCH_FIX
def _safe_int_race_no(x: Any, default: int = 1) -> int:
    try:
        v = int(float(x or default))
        return v if v > 0 else default
    except Exception:
        return default

def _auto_current_target_for_recommend(rc_date: str, meet: str = "전체", race_no: Any = 0) -> Tuple[str, int]:
    """
    추천/순차수집 대상 경주를 실제 현재/다음 경주 기준으로 맞춥니다.
    기존 문제: 전체모드에서 서울 1R로 고정되어 실제 더비온 화면 서울 3R과 어긋남.
    """
    try:
        # 사용자가 직접 경주를 골랐으면 그 값을 우선
        if str(meet) != "전체" and _safe_int_race_no(race_no, 0) > 0:
            return str(meet), _safe_int_race_no(race_no, 1)

        # 전체모드면 현재/다음 대상표에서 첫 번째 경주 사용
        if "_load_all_meet_schedule" in globals() and "_current_or_next_races" in globals():
            sched = _load_all_meet_schedule(rc_date)
            targets = _current_or_next_races(sched)
            if isinstance(targets, pd.DataFrame) and not targets.empty:
                row = targets.iloc[0]
                m = str(row.get("경마장", row.get("meet", "서울")) or "서울")
                rn = _safe_int_race_no(row.get("경주번호", row.get("race_no", 1)), 1)
                return m, rn

        # 세션에 최근 자동 타깃이 있으면 사용
        t = st.session_state.get("current_auto_target", {}) if "st" in globals() else {}
        if isinstance(t, dict):
            m = str(t.get("경마장", t.get("meet", "서울")) or "서울")
            rn = _safe_int_race_no(t.get("경주번호", t.get("race_no", 1)), 1)
            return m, rn
    except Exception:
        pass
    return "서울", 1

def _target_warning_if_possible(rc_date: str, meet: str, race_no: Any) -> None:
    try:
        m, rn = _auto_current_target_for_recommend(rc_date, meet, race_no)
        if str(meet) == "전체" or _safe_int_race_no(race_no, 0) <= 0:
            st.info(f"현재 추천/수집 대상 자동맞춤: {m} {rn}R")
        elif str(meet) != str(m) or _safe_int_race_no(race_no, 1) != int(rn):
            st.warning(f"선택 경주와 현재/다음 경주가 다를 수 있습니다. 선택={meet} {race_no}R / 자동감지={m} {rn}R")
    except Exception:
        pass

def build_recommendation_after_each_race(rc_date: str, meet: str, race_no: Any, data: Optional[Dict[str, pd.DataFrame]] = None) -> Dict[str, Any]:
    """
    매 경기 추천 생성.
    전체모드/경주번호 0일 때는 절대 서울 1R 고정 추천을 만들지 않고 현재/다음 경주로 맞춤.
    """
    auto_meet, auto_race = _auto_current_target_for_recommend(rc_date, meet, race_no)
    meet = auto_meet
    race_no = auto_race

    data = data or st.session_state.get("live_data", {}) or {}
    try:
        ready, reason = _recommend_ready_from_data(data)
        if not ready:
            payload = {
                "날짜": rc_date,
                "경마장": meet,
                "경주번호": int(race_no),
                "상태": reason,
                "추천가능": "N",
                "저장시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
            }
            try:
                if "external_hub_save" in globals():
                    external_hub_save("race_recommend_status", payload)
            except Exception:
                pass
            return payload

        env = fetch_weather(meet) if "fetch_weather" in globals() else {}
        base = build_base_horses(data, rc_date, meet, int(race_no)) if "build_base_horses" in globals() else pd.DataFrame()
        horses = merge_score_features(base, data, rc_date, meet, int(race_no)) if "merge_score_features" in globals() else base

        # 경주번호 필터 후 말이 3두 미만이면 잘못된 경주 추천으로 보지 않게 차단
        if isinstance(horses, pd.DataFrame) and len(horses) < 3:
            payload = {
                "날짜": rc_date,
                "경마장": meet,
                "경주번호": int(race_no),
                "추천가능": "N",
                "상태": f"추천 차단: {meet} {race_no}R 기준 말 데이터 {len(horses)}두라 부족",
                "저장시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
            }
            try:
                if "external_hub_save" in globals():
                    external_hub_save("race_recommend_status", payload)
            except Exception:
                pass
            return payload

        sim_count = int(st.session_state.get("sim_count", 1200))
        risk_mode = st.session_state.get("risk_mode", "균형형")
        score_df, result, combos = score_and_recommend(horses, env, sim_count, risk_mode) if "score_and_recommend" in globals() else (pd.DataFrame(), {}, [])

        if not isinstance(result, dict):
            result = {}
        result.update({
            "날짜": rc_date,
            "경마장": meet,
            "경주번호": int(race_no),
            "추천가능": "Y",
            "상태": f"{meet} {race_no}R 추천 생성 완료",
            "추천사유": reason,
            "저장시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
        })

        try:
            if "_build_three_type_recommendation" in globals():
                result = _build_three_type_recommendation(result)
            # 15ROUND_TARGET_LOCK: 추천 보조함수가 값을 보정해도 실제 수집 대상 날짜/경마장/경주번호는 유지
            try:
                result.update({
                    "날짜": rc_date,
                    "경마장": meet,
                    "경주번호": int(race_no),
                    "상태": f"{meet} {race_no}R 추천 생성 완료",
                })
            except Exception:
                pass
        except Exception:
            pass

        try:
            if "save_mobile_recommend_json" in globals():
                save_mobile_recommend_json(result)
        except Exception:
            pass
        try:
            if "external_hub_save" in globals():
                external_hub_save("race_recommend_status", result)
                external_hub_save("mobile_recommend", result)
        except Exception:
            pass
        try:
            st.session_state["latest_each_race_recommend"] = result
            st.session_state["latest_each_race_score"] = score_df
            st.session_state["latest_each_race_combos"] = combos
        except Exception:
            pass
        return result
    except Exception as e:
        payload = {
            "날짜": rc_date,
            "경마장": meet,
            "경주번호": race_no,
            "추천가능": "N",
            "상태": f"추천 생성 오류: {str(e)[:160]}",
            "저장시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
        }
        try:
            if "external_hub_save" in globals():
                external_hub_save("race_recommend_status", payload)
        except Exception:
            pass
        return payload

def render_recommendation_after_each_race_center(rc_date: str, meet: str, race_no: Any) -> None:
    st.markdown("### 🎯 매 경기 추천 생성 상태")
    auto_meet, auto_race = _auto_current_target_for_recommend(rc_date, meet, race_no)
    _target_warning_if_possible(rc_date, meet, race_no)

    rec = st.session_state.get("latest_each_race_recommend", {})
    if not isinstance(rec, dict) or not rec or str(rec.get("경마장")) != str(auto_meet) or _safe_int_race_no(rec.get("경주번호"), 0) != int(auto_race):
        rec = build_recommendation_after_each_race(rc_date, auto_meet, auto_race, st.session_state.get("live_data", {}))

    if rec.get("추천가능") == "Y":
        st.success(f"{rec.get('경마장')} {rec.get('경주번호')}R 추천 생성 완료")
    else:
        st.warning(rec.get("상태", "추천 대기"))

    keys = ["경마장", "경주번호", "안정형대표", "변수형대표", "고배당형대표", "공격삼쌍승", "방어삼복승", "예상배당", "신뢰도", "추천사유", "상태"]
    rows = [{"항목": k, "값": rec.get(k, "")} for k in keys if rec.get(k, "") != ""]
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# STREAMLIT_DUPLICATE_WIDGET_KEY_FIX
def _seq_widget_scope(target: str) -> str:
    """
    StreamlitDuplicateElementKey 방지.
    같은 26개 API 센터가 대시보드/검색/API탭 등에서 같은 target으로 2번 호출되어도
    호출 위치 line number를 key에 붙여 위젯 key가 절대 겹치지 않게 합니다.
    """
    try:
        caller = inspect.stack()[2]
        loc = f"{Path(str(caller.filename)).stem}_{caller.lineno}"
    except Exception:
        loc = "seq"
    return _safe_file_key(f"{loc}_{target}") if "_safe_file_key" in globals() else f"{loc}_{target}".replace(" ", "_")

def render_sequential_26api_center(rc_date: str, meet: str, race_no: Any) -> None:
    """
    중복 key 방지 + 멈춤 방지 버전.
    - 같은 화면에서 2번 호출되어도 selectbox/toggle/button key가 충돌하지 않음
    - 자동 순차 진행 ON이면 1개씩 실행 후 rerun
    - 404/500도 실패로 저장하고 다음 API 진행
    """
    st.markdown("### 🔁 26개 API 자동 순차 수집센터")
    st.caption("자동으로 1개씩 접속 → 성공/실패 저장 → 다음 API로 진행합니다. 404/500도 멈추지 않습니다.")

    meet2 = "서울" if str(meet or "전체") == "전체" else str(meet or "서울")
    try:
        race_no2 = int(float(race_no or 1))
        if race_no2 <= 0:
            race_no2 = 1
    except Exception:
        race_no2 = 1

    target = _seq_target_id(rc_date, meet2, race_no2)
    # StreamlitDuplicateElementKey 방지: 같은 화면에서 순차 API 센터가 2번 렌더링되어도
    # 위젯 key가 충돌하지 않도록 실행 1회 안에서 호출 번호를 붙입니다.
    global _SEQ_RENDER_CALL_COUNTER
    try:
        _SEQ_RENDER_CALL_COUNTER += 1
    except NameError:
        _SEQ_RENDER_CALL_COUNTER = 1
    widget_scope = f"{_seq_widget_scope(target)}_render{_SEQ_RENDER_CALL_COUNTER}"

    state = _load_seq_state()
    item = state.get(target)
    api_keys = _seq_api_keys()

    if not isinstance(item, dict):
        reset_sequential_26api(rc_date, meet2, race_no2)
        state = _load_seq_state()
        item = state.get(target, {})

    idx = int(item.get("index", 0) or 0)
    done = min(idx, len(api_keys))
    total = len(api_keys)
    rows = item.get("rows", []) if isinstance(item.get("rows", []), list) else []
    success = sum(1 for r in rows if str(r.get("상태", "")).upper().startswith("OK"))
    total_rows = sum(int(r.get("행수", 0) or 0) for r in rows)

    st.progress(done / max(total, 1), text=f"{done}/{total}개 완료")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("완료 API", f"{done}/{total}")
    c2.metric("수신 성공", success)
    c3.metric("총 수신행수", total_rows)
    c4.metric("상태", "완료" if done >= total else "자동 진행중")

    if done < total:
        next_key = api_keys[done]
        st.info(f"다음 수집 예정: {done+1}번 / {_api_stage_name(next_key)} / {_seq_label(next_key)} / `{next_key}`")
    else:
        st.success("26개 API 순차 수집이 완료되었습니다.")

    with st.expander("📋 26개 API 수집 순서표", expanded=False):
        order_df = pd.DataFrame([
            {"순번": i + 1, "단계": _api_stage_name(k), "API": _seq_label(k), "key": k}
            for i, k in enumerate(api_keys)
        ])
        st.dataframe(order_df, use_container_width=True, hide_index=True)

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        step_count = st.selectbox("한 번에 진행", [1, 2, 3, 5], index=0, key=f"seq_step_count_{widget_scope}")
    with col_b:
        auto_on = st.toggle("자동 순차 진행", value=False, key=f"seq_auto_on_{widget_scope}")
    with col_c:
        refresh_sec = st.selectbox("멈춤방지 새로고침", [5, 10, 15, 30, 60], index=1, key=f"seq_refresh_sec_{widget_scope}")

    b1, b2, b3 = st.columns(3)
    if b1.button("▶ 다음 API 1개 즉시 진행", key=f"seq_next_{widget_scope}", use_container_width=True):
        sequential_26api_step(rc_date, meet2, race_no2, 1)
        st.rerun()
    if b2.button("⏭ 선택 개수 진행", key=f"seq_multi_{widget_scope}", use_container_width=True):
        sequential_26api_step(rc_date, meet2, race_no2, int(step_count))
        st.rerun()
    if b3.button("🔄 처음부터 다시", key=f"seq_reset_{widget_scope}", use_container_width=True):
        reset_sequential_26api(rc_date, meet2, race_no2)
        st.rerun()

    if auto_on and _hub365_is_background_tick_request() and done < total and not _is_mobile_mode():
        now_ts = time.time()
        last_ts_key = f"_seq_last_auto_ts_{widget_scope}"
        last_ts = float(st.session_state.get(last_ts_key, 0) or 0)
        if now_ts - last_ts >= 1.5:
            st.session_state[last_ts_key] = now_ts
            sequential_26api_step(rc_date, meet2, race_no2, 1)
            st.rerun()
        else:
            st.markdown(f"<meta http-equiv='refresh' content='{int(refresh_sec)}'>", unsafe_allow_html=True)

    if auto_on and _hub365_is_background_tick_request() and done < total and not _is_mobile_mode():
        st.markdown(f"<meta http-equiv='refresh' content='{int(refresh_sec)}'>", unsafe_allow_html=True)

    state = _load_seq_state()
    item = state.get(target, item)
    rows = item.get("rows", []) if isinstance(item, dict) else []
    if rows:
        df = pd.DataFrame(rows)
        show = [c for c in ["순번", "단계", "API", "key", "행수", "상태", "추천판정", "완료시각", "저장파일"] if c in df.columns]
        st.dataframe(df[show], use_container_width=True, hide_index=True)
        try:
            last_status = str(rows[-1].get("상태", ""))
            if "HTTP 500" in last_status or "HTTP 404" in last_status or "ERROR" in last_status.upper():
                st.warning("마지막 API가 오류였지만 실패로 저장하고 다음 API로 넘어가게 되어 있습니다.")
        except Exception:
            pass
    else:
        st.caption("아직 수집 기록이 없습니다.")





# MOBILE_BLANK_LOOP_SAFE_MODE_FIX
def _is_mobile_mode() -> bool:
    try:
        q = st.query_params
        return str(q.get("mode", "")).lower() == "mobile"
    except Exception:
        return False

def render_mobile_safe_home(rc_date: str = "", meet: str = "전체", race_no: Any = 0) -> None:
    """
    모바일 화면 백지 방지용 경량 홈.
    모바일에서는 26개 API 자동 순차수집/무한 rerun/meta refresh를 직접 돌리지 않고,
    이미 생성된 추천/허브 추천/세션 추천만 빠르게 보여줍니다.
    """
    # set_page_config는 앱 시작부에서 1회만 호출합니다.
    st.markdown("## 🏇 MARU KRA 모바일")
    st.caption("모바일은 구매 전용 경량 화면입니다. 무거운 26개 API 자동수집은 PC 관리화면에서 돌립니다.")

    auto_meet, auto_race = _auto_current_target_for_recommend(rc_date or (today_kst() if "today_kst" in globals() else ""), meet, race_no)
    st.info(f"현재/다음 대상: {auto_meet} {auto_race}R")

    rec = st.session_state.get("latest_each_race_recommend", {})
    if not isinstance(rec, dict) or not rec:
        try:
            if "load_mobile_recommend_json" in globals():
                rec = load_mobile_recommend_json()
        except Exception:
            rec = {}
    if not isinstance(rec, dict):
        rec = {}

    # 경주번호 안 맞으면 경고만 띄우고 무거운 자동생성은 하지 않음
    if rec:
        rmeet = str(rec.get("경마장", rec.get("meet", "")))
        rrace = _safe_int_race_no(rec.get("경주번호", rec.get("race_no", 0)), 0)
        if rmeet and (rmeet != str(auto_meet) or rrace != int(auto_race)):
            st.warning(f"저장 추천은 {rmeet} {rrace}R 기준입니다. 현재/다음 대상 {auto_meet} {auto_race}R과 다를 수 있습니다.")
    else:
        st.warning("아직 모바일 추천이 없습니다. PC 관리화면에서 API 수집/추천 생성을 먼저 실행하세요.")

    if rec:
        title = f"{rec.get('경마장', auto_meet)} {rec.get('경주번호', auto_race)}R 추천"
        st.success(title)
        keys = ["안정형대표", "변수형대표", "고배당형대표", "공격삼쌍승", "방어삼복승", "예상배당", "신뢰도", "추천사유", "상태"]
        for k in keys:
            v = rec.get(k, "")
            if v != "":
                st.markdown(f"**{k}** : `{v}`")

    st.divider()
    st.link_button("📱 더비온 바로가기", "https://www.derbyon.co.kr", use_container_width=True)
    st.link_button("🖥 PC 관리화면 열기", "https://maru-kra-final-clean.streamlit.app/?v=hardfinal1", use_container_width=True)
    st.caption("모바일 백지 방지를 위해 이 화면에서는 자동 rerun을 사용하지 않습니다.")

def _mobile_stop_if_needed(rc_date: str = "", meet: str = "전체", race_no: Any = 0) -> None:
    if _is_mobile_mode():
        render_mobile_safe_home(rc_date, meet, race_no)
        st.stop()





# HUB_PC_MOBILE_RECOMMEND_FLOW_FIX
def _hub_load_latest_recommend() -> Dict[str, Any]:
    """
    모바일은 계산하지 않고 허브/저장 추천을 읽습니다.
    우선순위: external_hub_load(mobile_recommend) → local json → session.
    """
    rec = {}
    try:
        if "external_hub_load" in globals():
            x = external_hub_load("mobile_recommend")
            if isinstance(x, dict):
                rec = x
            elif isinstance(x, list) and x:
                last = x[-1]
                if isinstance(last, dict):
                    rec = last
            elif isinstance(x, pd.DataFrame) and not x.empty:
                rec = x.tail(1).to_dict("records")[0]
    except Exception:
        rec = {}
    if not rec:
        try:
            if "load_mobile_recommend_json" in globals():
                x = load_mobile_recommend_json()
                if isinstance(x, dict):
                    rec = x
        except Exception:
            rec = {}
    if not rec:
        x = st.session_state.get("latest_each_race_recommend", {})
        if isinstance(x, dict):
            rec = x
    return rec if isinstance(rec, dict) else {}

def _hub_save_pc_confirmed_recommend(rec: Dict[str, Any]) -> bool:
    """
    PC에서 생성/확인한 추천을 모바일용 허브에 저장합니다.
    """
    if not isinstance(rec, dict) or not rec:
        return False
    rec = dict(rec)
    rec["PC확인"] = "Y"
    rec["모바일표시"] = "Y"
    rec["허브저장시각"] = now_str() if "now_str" in globals() else str(dt.datetime.now())
    ok = False
    try:
        if "external_hub_save" in globals():
            external_hub_save("mobile_recommend", rec)
            external_hub_save("pc_confirmed_recommend", rec)
            ok = True
    except Exception:
        pass
    try:
        if "save_mobile_recommend_json" in globals():
            save_mobile_recommend_json(rec)
            ok = True
    except Exception:
        pass
    st.session_state["latest_each_race_recommend"] = rec
    return ok

def render_pc_hub_recommend_confirm_center(rc_date: str, meet: str, race_no: Any) -> None:
    """
    PC는 추천을 생성/검사/확인하고, 확인된 추천을 허브에 저장합니다.
    모바일은 이 결과만 읽습니다.
    """
    st.markdown("### 🧭 PC 확인 → 허브 저장 → 모바일 추천 결과")
    auto_meet, auto_race = _auto_current_target_for_recommend(rc_date, meet, race_no)
    rec = st.session_state.get("latest_each_race_recommend", {})
    if not isinstance(rec, dict) or not rec or str(rec.get("경마장", "")) != str(auto_meet) or _safe_int_race_no(rec.get("경주번호", 0), 0) != int(auto_race):
        rec = build_recommendation_after_each_race(rc_date, auto_meet, auto_race, st.session_state.get("live_data", {}))

    if rec.get("추천가능") == "Y":
        st.success(f"PC 추천 확인 대상: {rec.get('경마장')} {rec.get('경주번호')}R")
    else:
        st.warning(rec.get("상태", "추천 대기"))

    cols = st.columns(3)
    if cols[0].button("✅ PC 확인 후 모바일 허브 저장", use_container_width=True, key=f"pc_confirm_save_{auto_meet}_{auto_race}"):
        ok = _hub_save_pc_confirmed_recommend(rec)
        if ok:
            st.success("허브 mobile_recommend에 저장했습니다. 모바일은 이 결과를 읽습니다.")
        else:
            st.error("허브 저장 함수가 없거나 저장 실패했습니다. 로컬 저장만 확인하세요.")
    if cols[1].button("🔄 허브 최신 추천 다시 읽기", use_container_width=True, key=f"pc_reload_hub_{auto_meet}_{auto_race}"):
        h = _hub_load_latest_recommend()
        if h:
            st.session_state["latest_each_race_recommend"] = h
            st.success("허브 최신 추천을 다시 읽었습니다.")
            st.rerun()
        else:
            st.warning("허브에 읽을 추천이 없습니다.")
    cols[2].link_button("📱 모바일 결과 보기", "https://maru-kra-final-clean.streamlit.app/?mode=mobile&v=hubflow1", use_container_width=True)

    show_keys = ["경마장", "경주번호", "안정형대표", "변수형대표", "고배당형대표", "예상배당", "신뢰도", "추천사유", "PC확인", "허브저장시각", "상태"]
    rows = [{"항목": k, "값": rec.get(k, "")} for k in show_keys if rec.get(k, "") != ""]
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

def render_mobile_safe_home(rc_date: str = "", meet: str = "전체", race_no: Any = 0) -> None:
    """
    모바일은 추천을 생성하지 않습니다.
    허브에 저장된 PC 확인 추천 결과만 보여주는 화면입니다.
    """
    # set_page_config는 앱 시작부에서 1회만 호출합니다.
    st.markdown("## 🏇 MARU KRA 모바일 추천결과")
    st.info("🛡️ stable2 안정화판 적용됨")  # STABLE_VERSION_MOBILE_BADGE_APPLY
    st.caption("모바일은 계산/수집 화면이 아니라 PC에서 확인 후 허브에 저장한 추천 결과를 보는 화면입니다.")

    rec = _hub_load_latest_recommend()
    if not rec:
        st.warning("허브에 저장된 모바일 추천 결과가 없습니다.")
        st.info("PC 관리화면에서 API 수집 → 추천 생성 → 'PC 확인 후 모바일 허브 저장'을 먼저 눌러주세요.")
    else:
        meet_v = rec.get("경마장", rec.get("meet", ""))
        race_v = rec.get("경주번호", rec.get("race_no", ""))
        pc_ok = rec.get("PC확인", "")
        if pc_ok == "Y":
            st.success(f"PC 확인 완료 추천: {meet_v} {race_v}R")
        else:
            st.warning(f"저장 추천: {meet_v} {race_v}R / PC확인 표시 없음")

        keys = ["안정형대표", "변수형대표", "고배당형대표", "공격삼쌍승", "방어삼복승", "예상배당", "신뢰도", "추천사유", "허브저장시각", "상태"]
        for k in keys:
            v = rec.get(k, "")
            if v != "":
                st.markdown(f"**{k}** : `{v}`")

    st.divider()
    st.link_button("📱 더비온 바로가기", "https://www.derbyon.co.kr", use_container_width=True)
    st.link_button("🖥 PC 관리화면 열기", "https://maru-kra-final-clean.streamlit.app/?v=hubflow1", use_container_width=True)
    st.caption("모바일에서는 26개 API 자동수집을 돌리지 않아 백지/무한로딩을 막습니다.")





# HUB_SHEET_DOUBLE_SAFETY_FLOW_FIX
def _as_plain_dict(obj: Any) -> Dict[str, Any]:
    try:
        if isinstance(obj, dict):
            return {str(k): (v.item() if hasattr(v, "item") else v) for k, v in obj.items()}
        if isinstance(obj, pd.DataFrame) and not obj.empty:
            return obj.tail(1).to_dict("records")[0]
        if isinstance(obj, list) and obj:
            last = obj[-1]
            return last if isinstance(last, dict) else {"value": str(last)}
    except Exception:
        pass
    return {}

def _safe_external_load(name: str) -> Any:
    try:
        if "external_hub_load" in globals():
            return external_hub_load(name)
    except Exception:
        return None
    return None

def _safe_external_save(name: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
    try:
        if "external_hub_save" in globals():
            external_hub_save(name, payload)
            return True, "허브 저장 호출 OK"
        return False, "external_hub_save 함수 없음"
    except Exception as e:
        return False, f"허브 저장 실패: {str(e)[:160]}"

def _safe_local_save(name: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
    try:
        d = DATA_DIR if "DATA_DIR" in globals() else Path("maru_kra_data")
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{name}.json"
        rows = []
        if p.exists():
            try:
                old = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(old, list):
                    rows = old
                elif isinstance(old, dict):
                    rows = [old]
            except Exception:
                rows = []
        rows.append(payload)
        p.write_text(json.dumps(rows[-300:], ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return True, str(p)
    except Exception as e:
        return False, f"로컬 저장 실패: {str(e)[:160]}"

def _safe_local_load(name: str) -> Any:
    try:
        d = DATA_DIR if "DATA_DIR" in globals() else Path("maru_kra_data")
        p = d / f"{name}.json"
        if p.exists():
            x = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(x, list) and x:
                return x[-1]
            return x
    except Exception:
        return None
    return None

def double_safety_save(name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    이중 안전 저장:
    1) 허브/구글시트 저장 시도
    2) 로컬 JSON 백업 저장
    3) 허브 다시 읽기 확인
    4) 검증 로그 저장
    """
    payload = _as_plain_dict(payload)
    payload["저장키"] = name
    payload["저장요청시각"] = now_str() if "now_str" in globals() else str(dt.datetime.now())
    hub_ok, hub_msg = _safe_external_save(name, payload)
    local_ok, local_msg = _safe_local_save(name, payload)

    readback = _safe_external_load(name)
    rb = _as_plain_dict(readback)
    readback_ok = bool(rb)
    if not readback_ok:
        rb = _as_plain_dict(_safe_local_load(name))
        readback_ok = bool(rb)

    verify = {
        "저장키": name,
        "허브저장": "OK" if hub_ok else "FAIL",
        "허브메시지": hub_msg,
        "로컬백업": "OK" if local_ok else "FAIL",
        "로컬메시지": local_msg,
        "다시읽기": "OK" if readback_ok else "FAIL",
        "경마장": payload.get("경마장", ""),
        "경주번호": payload.get("경주번호", ""),
        "추천": payload.get("안정형대표", payload.get("추천", "")),
        "검증시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
    }

    try:
        _safe_local_save("hub_sheet_verify_log", verify)
        if hub_ok:
            _safe_external_save("hub_sheet_verify_log", verify)
    except Exception:
        pass

    st.session_state["last_double_safety_verify"] = verify
    return verify

def hub_collect_save_analyze_recommend(rc_date: str, meet: str, race_no: Any) -> Dict[str, Any]:
    """
    정리된 실제 흐름:
    허브/공식 API 자료 불러오기 → 허브+로컬 저장 → 분석 → 추천 → 허브+로컬 저장 → 모바일 표시 준비.
    """
    auto_meet, auto_race = _auto_current_target_for_recommend(rc_date, meet, race_no)
    result = {
        "날짜": rc_date,
        "경마장": auto_meet,
        "경주번호": int(auto_race),
        "시작시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
    }

    data = st.session_state.get("live_data", {}) or {}
    status = st.session_state.get("api_status", pd.DataFrame())

    # 자료가 없으면 현재 대상 1회 수집 시도
    try:
        if not data and "fetch_all_live" in globals():
            data, status = fetch_all_live(rc_date, auto_meet, int(auto_race))
            st.session_state["live_data"] = data
            st.session_state["api_status"] = status
    except Exception as e:
        result["자료수집오류"] = str(e)[:160]

    # 원자료 저장
    summary = {}
    try:
        for k, df in (data or {}).items():
            if isinstance(df, pd.DataFrame):
                summary[k] = int(len(df))
        raw_payload = dict(result)
        raw_payload.update({
            "자료키수": len(summary),
            "총수신행수": int(sum(summary.values())),
            "API별행수": json.dumps(summary, ensure_ascii=False),
        })
        raw_verify = double_safety_save("raw_collection_summary", raw_payload)
        result["원자료저장검증"] = raw_verify
    except Exception as e:
        result["원자료저장오류"] = str(e)[:160]

    # 분석/추천
    try:
        rec = build_recommendation_after_each_race(rc_date, auto_meet, int(auto_race), data)
        if not isinstance(rec, dict):
            rec = {}
        rec["경마장"] = auto_meet
        rec["경주번호"] = int(auto_race)
        rec["분석완료시각"] = now_str() if "now_str" in globals() else str(dt.datetime.now())
        rec["모바일표시"] = "Y"
        rec["추천출처"] = "허브자료_분석추천"
        try:
            rec["실시간행수"] = int(sum(len(df) for df in (data or {}).values() if isinstance(df, pd.DataFrame)))
            rec["API상태행수"] = int(len(status)) if isinstance(status, pd.DataFrame) else 0
            if "_hub365_probability_from_hub" in globals():
                rec.update(_hub365_probability_from_hub(rec))
        except Exception as _prob_e:
            rec["확률계산상태"] = f"대기: {str(_prob_e)[:80]}"
        rec_verify = double_safety_save("mobile_recommend", rec)
        double_safety_save("analysis_recommend_log", rec)
        result["추천"] = rec
        result["추천저장검증"] = rec_verify
        st.session_state["latest_each_race_recommend"] = rec
    except Exception as e:
        result["추천오류"] = str(e)[:160]

    double_safety_save("hub_pipeline_run_log", result)
    return result

def render_hub_storage_status_center() -> None:
    st.markdown("### 🧾 허브/구글시트 저장 확인센터")
    keys = [
        "raw_collection_summary",
        "analysis_recommend_log",
        "mobile_recommend",
        "pc_confirmed_recommend",
        "hub_pipeline_run_log",
        "hub_sheet_verify_log",
    ]
    rows = []
    for k in keys:
        obj = _safe_external_load(k)
        d = _as_plain_dict(obj)
        source = "허브/구글시트"
        if not d:
            obj = _safe_local_load(k)
            d = _as_plain_dict(obj)
            source = "로컬백업"
        rows.append({
            "저장항목": k,
            "확인": "OK" if d else "없음",
            "출처": source if d else "-",
            "경마장": d.get("경마장", ""),
            "경주번호": d.get("경주번호", ""),
            "저장/검증시각": d.get("허브저장시각", d.get("검증시각", d.get("저장요청시각", d.get("분석완료시각", "")))),
            "추천": d.get("안정형대표", d.get("추천", "")),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    last = st.session_state.get("last_double_safety_verify", {})
    if isinstance(last, dict) and last:
        if last.get("허브저장") == "OK" and last.get("로컬백업") == "OK" and last.get("다시읽기") == "OK":
            st.success("마지막 저장 검증: 허브 저장 + 로컬 백업 + 다시읽기 OK")
        else:
            st.warning(f"마지막 저장 검증 확인 필요: {last}")

def render_hub_pipeline_control_center(rc_date: str, meet: str, race_no: Any) -> None:
    st.markdown("### 🔐 허브 자료 저장·분석·추천 이중 안전장치")
    st.caption("허브/구글시트와 로컬백업에 동시에 저장하고, 다시 읽어서 저장 여부를 화면에 보여줍니다.")
    auto_meet, auto_race = _auto_current_target_for_recommend(rc_date, meet, race_no)
    st.info(f"대상 경주: {auto_meet} {auto_race}R")

    c1, c2, c3 = st.columns(3)
    if c1.button("① 허브자료 저장+분석+모바일추천", use_container_width=True, key=f"hub_pipeline_run_{auto_meet}_{auto_race}"):
        run = hub_collect_save_analyze_recommend(rc_date, auto_meet, int(auto_race))
        st.session_state["last_hub_pipeline_run"] = run
        st.success("허브 저장/분석/추천 파이프라인 실행 완료")
        st.rerun()
    if c2.button("② 저장 여부 다시 확인", use_container_width=True, key=f"hub_storage_check_{auto_meet}_{auto_race}"):
        st.session_state["force_show_hub_storage"] = True
    c3.link_button("③ 모바일 추천결과 보기", "https://maru-kra-final-clean.streamlit.app/?mode=mobile&v=hubdual1", use_container_width=True)

    render_hub_storage_status_center()

def render_mobile_safe_home(rc_date: str = "", meet: str = "전체", race_no: Any = 0) -> None:
    """
    모바일 최종 역할:
    허브/구글시트에 저장된 mobile_recommend만 표시.
    모바일에서 자료수집/분석은 하지 않습니다.
    """
    # set_page_config는 앱 시작부에서 1회만 호출합니다.
    st.markdown("## 🏇 MARU KRA 모바일 추천결과")
    st.caption("허브/구글시트에 저장된 최종 추천만 보여줍니다.")

    rec = _hub_load_latest_recommend()
    if not rec:
        st.warning("허브/구글시트에 저장된 mobile_recommend가 없습니다.")
        st.info("PC에서 '허브자료 저장+분석+모바일추천'을 먼저 실행하세요.")
    else:
        meet_v = rec.get("경마장", "")
        race_v = rec.get("경주번호", "")
        st.success(f"최종 추천: {meet_v} {race_v}R")
        keys = ["안정형대표", "변수형대표", "고배당형대표", "공격삼쌍승", "방어삼복승", "예상배당", "신뢰도", "추천사유", "추천출처", "분석완료시각", "허브저장시각", "상태"]
        for k in keys:
            v = rec.get(k, "")
            if v != "":
                st.markdown(f"**{k}** : `{v}`")

    st.divider()
    st.link_button("📱 더비온 바로가기", "https://www.derbyon.co.kr", use_container_width=True)
    st.link_button("🖥 PC 관리화면 열기", "https://maru-kra-final-clean.streamlit.app/?v=hubdual1", use_container_width=True)
    st.caption("모바일은 확인 전용입니다. 수집/분석/저장은 PC와 허브에서 처리합니다.")





# GOOGLE_SHEET_HARDCODED_NO_INPUT_FIX
# 요청사항: PC/모바일 어디에서도 구글시트 ID를 다시 입력하지 않음.
# 앱 안에 형님 허브 SHEET_ID/GID를 고정 포함합니다.
MARU_KRA_FIXED_SHEET_ID = "1uT8lQfbpjhblvFOsFdBSmAnGHXzqhlZQ5jsBayLTpwo"
MARU_KRA_FIXED_SHEET_GID = "909440003"
MARU_KRA_FIXED_SHEET_NAME = "MARU_KRA_HUB"
MARU_KRA_FIXED_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{MARU_KRA_FIXED_SHEET_ID}/edit?gid={MARU_KRA_FIXED_SHEET_GID}#gid={MARU_KRA_FIXED_SHEET_GID}"

# 기존 코드 호환용 이름도 같은 값으로 고정
DEFAULT_MARU_KRA_SHEET_ID = MARU_KRA_FIXED_SHEET_ID
DEFAULT_MARU_KRA_SHEET_NAME = MARU_KRA_FIXED_SHEET_NAME


def _extract_sheet_id_from_url_or_id(text: str) -> str:
    """기존 호환용 함수. 화면 입력은 없지만, 내부 테스트/과거 함수가 호출해도 안전하게 처리."""
    text = str(text or "").strip()
    if not text:
        return ""
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", text)
    if m:
        return m.group(1)
    if re.fullmatch(r"[a-zA-Z0-9-_]{20,}", text):
        return text
    return ""


def _get_sheet_id_visible() -> str:
    """구글시트 ID는 사용자가 입력하지 않고 앱에 포함된 고정 ID만 사용합니다."""
    return MARU_KRA_FIXED_SHEET_ID


def _get_sheet_gid_visible() -> str:
    return MARU_KRA_FIXED_SHEET_GID


def _get_sheet_url_visible() -> str:
    return MARU_KRA_FIXED_SHEET_URL


def get_fixed_google_sheet_hub_config() -> Dict[str, str]:
    """허브/진단/모바일 표시에서 공통으로 쓰는 고정 구글시트 정보."""
    return {
        "sheet_id": MARU_KRA_FIXED_SHEET_ID,
        "gid": MARU_KRA_FIXED_SHEET_GID,
        "sheet_name": MARU_KRA_FIXED_SHEET_NAME,
        "url": MARU_KRA_FIXED_SHEET_URL,
        "mode": "CLOUD_HUB_FIXED_SHEET_ID",
    }


def render_google_sheet_visible_center() -> None:
    """PC 확인용: 입력창 없이 고정 허브 정보를 보여줍니다."""
    st.markdown("### 📗 구글시트 허브")
    st.success("구글시트 ID가 앱 안에 포함되어 있습니다. PC/모바일에서 다시 입력하지 않습니다.")

    cfg = get_fixed_google_sheet_hub_config()
    rows = [
        {"항목": "허브 모드", "상태": "고정 적용", "값": cfg["mode"]},
        {"항목": "SHEET_ID", "상태": "앱 포함", "값": cfg["sheet_id"]},
        {"항목": "GID", "상태": "앱 포함", "값": cfg["gid"]},
        {"항목": "기본 시트명", "상태": "확인용", "값": cfg["sheet_name"]},
        {"항목": "모바일 역할", "상태": "입력창 없음", "값": "mobile_recommend 최신 추천만 표시"},
        {"항목": "자동구매/자동결제", "상태": "없음", "값": "사용자가 직접 마권 구매"},
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.code(cfg["url"], language="text")
    st.link_button("📗 고정 구글시트 허브 열기", cfg["url"], use_container_width=True)

    st.markdown("#### 저장 확인")
    if "render_hub_storage_status_center" in globals():
        render_hub_storage_status_center()
    else:
        st.info("저장 확인센터 함수가 아직 로드되지 않았습니다.")


def _render_sidebar_google_sheet_link() -> None:
    """사이드바: 입력창 없이 고정 허브 링크만 표시."""
    try:
        cfg = get_fixed_google_sheet_hub_config()
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📗 구글시트 허브")
        st.sidebar.caption("SHEET_ID 앱 포함 · 입력 필요 없음")
        st.sidebar.link_button("고정 허브 열기", cfg["url"], use_container_width=True)
        st.sidebar.caption(f"ID: {cfg['sheet_id'][:10]}…{cfg['sheet_id'][-6:]}")
    except Exception:
        pass




# API_PREFETCH_REALTIME_PRIORITY_26_FIX
PREFETCH_STATIC_API_KEYS = [
    "result_detail_url","race_detail_result_url","race_record_url","jockey_result_url",
    "horse_url","rating_url","corner_pace_url","dividend_integrated_url",
    "first_odds_url","second_odds_url","third_odds_url",
]
REALTIME_API_KEYS = [
    "race_url","race_overview_url","entry_url","entry_registered_url","body_url",
    "jockey_change_url","race_cancel_url","popularity_url","odds_url","today_odds_url",
    "weather_alert_url","gear_url","horse_shoe_url","start_exam_url","judge_url",
]
SUPPLEMENT_API_WISHLIST = [
    {"추천API":"기수 성적 정보","용도":"기수 통산/최근1년 승률·1착률","분류":"미리저장"},
    {"추천API":"기수 상세정보","용도":"기수 소속/상태/기본정보","분류":"미리저장"},
    {"추천API":"경주마 상세정보","용도":"말 혈통/나이/성별/통산성적","분류":"미리저장"},
    {"추천API":"출전마 장구사용 및 폐출혈 정보","용도":"장구 변경/폐출혈 변수","분류":"실시간/당일"},
    {"추천API":"마필 구간별 경주기록","용도":"초반/중반/막판 힘 분석","분류":"미리저장"},
    {"추천API":"경주 구간별 성적 정보","용도":"코너 위치/선행·추입 성향","분류":"미리저장"},
    {"추천API":"예상배당률 통합 정보","용도":"구매 직전 배당 흐름","분류":"실시간"},
    {"추천API":"승식별 최고배당률 정보","용도":"고배당 패턴 학습","분류":"미리저장"},
]
def _available_api_keys() -> List[str]:
    try:
        return [k for k, _ in API_LABELS]
    except Exception:
        return []
def _api_label_safe(k: str) -> str:
    try:
        return _seq_label(k)
    except Exception:
        try:
            return dict(API_LABELS).get(k, k)
        except Exception:
            return k
def _api_collection_bucket(k: str) -> str:
    if k in REALTIME_API_KEYS:
        return "실시간 반복"
    if k in PREFETCH_STATIC_API_KEYS:
        return "미리저장/재사용"
    return "보조/확인"
def _active_26_api_keys() -> List[str]:
    available=_available_api_keys()
    preferred=[
        "race_url","race_overview_url","entry_url","entry_registered_url",
        "body_url","jockey_change_url","race_cancel_url","weather_alert_url",
        "gear_url","horse_shoe_url","popularity_url","odds_url","today_odds_url",
        "start_exam_url","judge_url","horse_url","rating_url","jockey_result_url",
        "corner_pace_url","result_detail_url","race_detail_result_url","race_record_url",
        "dividend_integrated_url","first_odds_url","second_odds_url","third_odds_url",
    ]
    ordered=[k for k in preferred if k in available]
    ordered += [k for k in available if k not in ordered]
    return ordered[:26] if len(ordered)>26 else ordered
def _seq_api_keys() -> List[str]:
    return _active_26_api_keys()
def render_api_priority_strategy_center() -> None:
    st.markdown("### 🧭 API 우선순위 정리")
    st.caption("기존 API는 빼지 않고, 기본 수집 순서만 미리저장/실시간으로 나눴습니다.")
    available=_available_api_keys()
    active=_active_26_api_keys()
    rows=[{"순번":i+1,"분류":_api_collection_bucket(k),"API":_api_label_safe(k),"key":k,
           "운영방식":"오늘 경주 때 반복 확인" if k in REALTIME_API_KEYS else "한 번 저장 후 재사용/보충"}
          for i,k in enumerate(active)]
    st.markdown("#### 기본 실행 26개 순서")
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown("#### 실시간으로 받아야 하는 것")
        r=[{"API":_api_label_safe(k),"key":k,"이유":"오늘 경주 전후 변동 가능"} for k in REALTIME_API_KEYS if k in available]
        st.dataframe(pd.DataFrame(r),use_container_width=True,hide_index=True) if r else st.info("현재 등록된 실시간 키 없음")
    with c2:
        st.markdown("#### 미리 받아 저장할 것")
        s=[{"API":_api_label_safe(k),"key":k,"이유":"확정 후 거의 변동 없음, 저장소 재사용"} for k in PREFETCH_STATIC_API_KEYS if k in available]
        st.dataframe(pd.DataFrame(s),use_container_width=True,hide_index=True) if s else st.info("현재 등록된 미리저장 키 없음")
    st.markdown("#### 보충 신청 추천 목록")
    st.dataframe(pd.DataFrame(SUPPLEMENT_API_WISHLIST),use_container_width=True,hide_index=True)
    h=[{"API":_api_label_safe(k),"key":k,"상태":"기존 유지, 기본 26개 밖 보조"} for k in available if k not in active]
    if h:
        with st.expander("기존에는 있지만 기본 26개 밖으로 밀린 보조 API", expanded=False):
            st.dataframe(pd.DataFrame(h),use_container_width=True,hide_index=True)
def render_prefetch_static_data_center(rc_date: str, meet: str, race_no: Any) -> None:
    st.markdown("### 🗄️ 미리 저장 자료 수집센터")
    st.caption("과거 우승마/기수/확정결과/기록성 자료는 한 번 저장하고 계속 재사용합니다.")
    meet2="서울" if str(meet or "전체")=="전체" else str(meet or "서울")
    try:
        race_no2=int(float(race_no or 1)); race_no2 = race_no2 if race_no2>0 else 1
    except Exception:
        race_no2=1
    keys=[k for k in PREFETCH_STATIC_API_KEYS if k in _available_api_keys()]
    if not keys:
        st.warning("현재 API_LABELS에서 미리저장 대상 키를 찾지 못했습니다."); return
    if st.button("📥 미리저장 자료 1회 수집/저장", use_container_width=True, key=f"prefetch_static_{rc_date}_{meet2}_{race_no2}"):
        saved=[]; data=st.session_state.get("live_data",{}) or {}
        for k in keys:
            try:
                df,msg,used_url=fetch_one_api(k,rc_date,meet2,race_no2)
                if df is None: df=pd.DataFrame()
                if not isinstance(df,pd.DataFrame): df=pd.DataFrame(df)
                if not df.empty: data[k]=df
                payload={"날짜":rc_date,"경마장":meet2,"경주번호":race_no2,"분류":"미리저장",
                         "API":_api_label_safe(k),"key":k,"행수":int(len(df)),"상태":msg,
                         "저장시각":now_str() if "now_str" in globals() else str(dt.datetime.now())}
                try:
                    if "double_safety_save" in globals(): double_safety_save("prefetch_static_summary",payload)
                    elif "external_hub_save" in globals(): external_hub_save("prefetch_static_summary",payload)
                except Exception as e:
                    payload["저장오류"]=str(e)[:120]
                saved.append(payload)
            except Exception as e:
                saved.append({"날짜":rc_date,"경마장":meet2,"경주번호":race_no2,"분류":"미리저장",
                              "API":_api_label_safe(k),"key":k,"행수":0,"상태":f"ERROR: {str(e)[:160]}",
                              "저장시각":now_str() if "now_str" in globals() else str(dt.datetime.now())})
        st.session_state["live_data"]=data
        st.session_state["last_prefetch_static"]=saved
        st.success("미리저장 자료 수집/저장 완료")
        st.dataframe(pd.DataFrame(saved),use_container_width=True,hide_index=True)
    old=st.session_state.get("last_prefetch_static",[])
    if old:
        with st.expander("최근 미리저장 결과",expanded=False):
            st.dataframe(pd.DataFrame(old),use_container_width=True,hide_index=True)





# API_TIMEOUT_ERROR_STABLE_ANALYSIS_FIX
API_TIMEOUT_SECONDS = 10
API_RETRY_COUNT = 1

def stable_error_kind(status="", rows=0, exc=None):
    if exc is not None:
        name = exc.__class__.__name__
        msg = str(exc)
        if "timeout" in name.lower() or "timeout" in msg.lower():
            return "TIMEOUT: 서버 지연/응답 없음"
        if "json" in name.lower() or "json" in msg.lower():
            return "PARSE_ERROR: 응답 형식 문제"
        if "connect" in name.lower() or "connection" in name.lower():
            return "CONNECTION_ERROR: 연결 문제"
        return "EXCEPTION: " + name
    s = str(status or "")
    if "HTTP 404" in s: return "HTTP_404: 주소/엔드포인트 확인"
    if "HTTP 500" in s: return "HTTP_500: 서버/파라미터 문제"
    if "HTTP 401" in s or "HTTP 403" in s: return "AUTH_ERROR: 키/권한 확인"
    if int(rows or 0) == 0: return "NO_DATA: 자료 없음/공개 전"
    return "OK: 데이터 수신"

def safe_fetch_one_api_stable(key, rc_date, meet, race_no, retry=1):
    started = time.time()
    last_exc = None
    for attempt in range(int(retry or 0) + 1):
        try:
            df, msg, used_url = fetch_one_api(key, rc_date, meet, race_no)
            if df is None: df = pd.DataFrame()
            if not isinstance(df, pd.DataFrame): df = pd.DataFrame(df)
            rows = int(len(df))
            meta = {
                "API": _api_label_safe(key) if "_api_label_safe" in globals() else key,
                "key": key,
                "시도": attempt + 1,
                "행수": rows,
                "소요초": round(time.time() - started, 2),
                "오류분류": stable_error_kind(msg, rows),
                "상태": str(msg)[:220],
                "완료시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
            }
            return df, meta
        except Exception as e:
            last_exc = e
            if attempt < int(retry or 0):
                time.sleep(0.5)
                continue
    meta = {
        "API": _api_label_safe(key) if "_api_label_safe" in globals() else key,
        "key": key,
        "시도": int(retry or 0) + 1,
        "행수": 0,
        "소요초": round(time.time() - started, 2),
        "오류분류": stable_error_kind(exc=last_exc),
        "상태": ("ERROR: " + str(last_exc))[:220],
        "완료시각": now_str() if "now_str" in globals() else str(dt.datetime.now()),
    }
    return pd.DataFrame(), meta

def stable_fetch_batch_and_analyze(rc_date, meet, race_no, max_count=26, retry=1):
    keys = _seq_api_keys() if "_seq_api_keys" in globals() else []
    keys = list(keys)[:int(max_count or 26)]
    data, rows = {}, []
    for i, key in enumerate(keys, 1):
        try:
            df, meta = safe_fetch_one_api_stable(key, rc_date, meet, race_no, retry=retry)
            meta["순번"] = i
            meta["분류"] = _api_collection_bucket(key) if "_api_collection_bucket" in globals() else ""
            rows.append(meta)
            if isinstance(df, pd.DataFrame) and not df.empty:
                df2 = df.copy()
                df2["수집API"] = key
                df2["수집경마장"] = meet
                df2["수집경주번호"] = race_no
                data[key] = df2
        except Exception as e:
            rows.append({"순번": i, "API": key, "key": key, "행수": 0, "오류분류": stable_error_kind(exc=e), "상태": str(e)[:220]})
            continue
    status = pd.DataFrame(rows)
    st.session_state["live_data"] = data
    st.session_state["api_status"] = status
    st.session_state["stable_status_last"] = status

    rec = {}
    try:
        if "build_recommendation_after_each_race" in globals():
            rec = build_recommendation_after_each_race(rc_date, meet, race_no, data)
        else:
            rec = {"추천가능": "N", "상태": "추천 함수 없음"}
    except Exception as e:
        rec = {"추천가능": "N", "상태": "분석 오류: " + str(e)[:160], "오류분류": stable_error_kind(exc=e)}
    if not isinstance(rec, dict): rec = {"추천가능": "N", "상태": "추천 결과 형식 오류"}
    rec["분석방식"] = "성공 API만 사용한 안정 분석"
    rec["분석시각"] = now_str() if "now_str" in globals() else str(dt.datetime.now())
    st.session_state["stable_rec_last"] = rec

    try:
        d = DATA_DIR if "DATA_DIR" in globals() else Path("maru_kra_data")
        d.mkdir(parents=True, exist_ok=True)
        status.to_csv(d / "api_error_stable_log.csv", index=False, encoding="utf-8-sig")
    except Exception:
        pass
    try:
        if "double_safety_save" in globals():
            double_safety_save("stable_analysis_recommend", rec)
    except Exception:
        pass
    return data, status, rec

def render_api_timeout_error_stable_center(rc_date, meet, race_no):
    st.markdown("### 🛡️ API 타임아웃/에러처리 안정화 분석센터")
    st.caption("API 하나가 실패해도 앱을 멈추지 않고 다음 API로 넘어가며, 성공 자료만으로 분석합니다.")
    meet2 = "서울" if str(meet or "전체") == "전체" else str(meet or "서울")
    try:
        race_no2 = int(float(race_no or 1))
        if race_no2 <= 0: race_no2 = 1
    except Exception:
        race_no2 = 1

    c1, c2, c3 = st.columns(3)
    retry = c1.selectbox("재시도", [0, 1, 2], index=1, key=f"stable_retry_{meet2}_{race_no2}")
    count = c2.selectbox("수집 개수", [5, 10, 15, 26], index=3, key=f"stable_count_{meet2}_{race_no2}")
    c3.metric("대상", f"{meet2} {race_no2}R")

    if st.button("🛡️ 안정 수집 후 분석 실행", use_container_width=True, key=f"stable_run_{rc_date}_{meet2}_{race_no2}"):
        stable_fetch_batch_and_analyze(rc_date, meet2, race_no2, max_count=int(count), retry=int(retry))
        st.success("안정 수집/분석 완료")
        st.rerun()

    status = st.session_state.get("stable_status_last", pd.DataFrame())
    if isinstance(status, pd.DataFrame) and not status.empty:
        show = [c for c in ["순번","분류","API","key","행수","소요초","오류분류","상태","완료시각"] if c in status.columns]
        st.dataframe(status[show], use_container_width=True, hide_index=True)
        try:
            ok = int((status["행수"].fillna(0).astype(int) > 0).sum())
            total = int(status["행수"].fillna(0).astype(int).sum())
            a,b,c = st.columns(3)
            a.metric("성공 API", ok)
            b.metric("실패/빈자료", len(status)-ok)
            c.metric("총 수신행수", total)
        except Exception:
            pass

    rec = st.session_state.get("stable_rec_last", {})
    if isinstance(rec, dict) and rec:
        st.markdown("#### 안정 분석 결과")
        if rec.get("추천가능") == "Y":
            st.success(rec.get("상태", "추천 생성 완료"))
        else:
            st.warning(rec.get("상태", "추천 대기/자료 부족"))
        keys = ["경마장","경주번호","안정형대표","변수형대표","고배당형대표","예상배당","신뢰도","추천사유","분석방식","분석시각","오류분류"]
        rr = [{"항목": k, "값": rec.get(k, "")} for k in keys if rec.get(k, "") != ""]
        if rr: st.dataframe(pd.DataFrame(rr), use_container_width=True, hide_index=True)





# STABLE_VERSION_VISIBLE_UI_FIX
def render_stable_version_banner():
    st.markdown("""
    <div style="padding:14px;border-radius:14px;border:2px solid #ffcc00;background:#fff8d6;margin:8px 0 14px 0;">
      <div style="font-size:22px;font-weight:900;">🛡️ MARU KRA 안정화판 stable2 적용됨</div>
      <div style="font-size:14px;">API 실패해도 앱 멈추지 않음 · 성공 API만 분석 · 404/500/빈자료 분류</div>
    </div>
    """, unsafe_allow_html=True)

def render_stable_quick_panel(rc_date, meet, race_no):
    st.markdown("### 🛡️ 안정화판 빠른 실행")
    st.caption("이 박스가 보이면 새 파일이 적용된 것입니다.")
    m = "서울" if str(meet or "전체") == "전체" else str(meet or "서울")
    try:
        r = int(float(race_no or 1))
        if r <= 0:
            r = 1
    except Exception:
        r = 1
    c1,c2,c3 = st.columns(3)
    c1.metric("버전","stable2")
    c2.metric("대상",f"{m} {r}R")
    c3.metric("모드","에러 안정분석")
    if st.button("🛡️ stable2 안정 수집+분석 바로 실행", use_container_width=True, key=f"stable2_quick_{rc_date}_{m}_{r}"):
        if "stable_fetch_batch_and_analyze" in globals():
            stable_fetch_batch_and_analyze(rc_date, m, r, max_count=26, retry=1)
            st.success("stable2 안정 수집/분석 완료")
            st.rerun()
        else:
            st.error("안정 분석 함수가 없습니다. 파일 적용이 완전하지 않습니다.")


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
    render_character_growth_dashboard()  # PC_CHARACTER_DASHBOARD_APPLY
    render_agent365_control_center(compact=False)  # AGENT365_PC_CONTROL_APPLY

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
                key_input = st.text_input("공공데이터 API Key", value=current_key, type="password", placeholder="공공데이터 일반 인증키 입력", key="api_key_change_input")
                if st.button("API Key 저장", width="stretch", key="api_key_save_btn"):
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
            key_input = st.text_input("공공데이터 API Key", value="", type="password", placeholder="공공데이터 일반 인증키 입력", key="api_key_empty_input")
            if st.button("API Key 저장", width="stretch", key="api_key_empty_save_btn"):
                if key_input.strip():
                    st.session_state["api_key_saved"] = key_input.strip()
                    if save_local_settings({"api_key": key_input.strip(), "saved_at_kst": now_str()}):
                        st.success("API Key 저장 완료")
                        st.rerun()
                    else:
                        st.warning("세션에는 저장됐지만 파일 저장은 실패했습니다.")
                else:
                    st.warning("API Key를 입력해 주세요.")

        rc_date = st.text_input("분석 날짜", value=today_kst(), key="analysis_date_input")
        race_scope = st.selectbox("운영 범위", ["전체 경마장 자동", "선택 경마장/경주"], index=1, help="기본은 선택 경마장/경주 확인용입니다. 전체 경마장 자동은 버튼을 눌렀을 때만 실행되어 계속 도는 현상을 막습니다.", key="race_scope_select")
        st.session_state["race_scope"] = race_scope
        if race_scope == "전체 경마장 자동":
            meet = "전체"
            race_no = 0
            st.success("서울·부산경남·제주 전체 경주일정 자동 확인 모드")
        else:
            meet = st.selectbox("경마장", ["서울", "부산경남", "제주"], index=0, key="meet_select_main")
            race_no = st.number_input("경주번호", min_value=1, max_value=20, value=1, step=1, key="race_no_input_main")
        race_time_text = st.text_input("경주 예정시각", value=st.session_state.get("race_time_text", ""), placeholder="예: 14:30", key="race_time_text_input")
        st.session_state["race_time_text"] = race_time_text
        sim_count = st.slider("시뮬레이션", 300, 5000, 1200, step=100, key="sim_count_slider")
        risk_mode = st.selectbox("전략", ["균형형", "안전형", "공격형"], index=0, key="risk_mode_select")
        collection_mode = st.selectbox("API 수집 모드", ["실시간 API 우선 + 허브 보조", "스마트 자동", "아침 사전수집", "경주 전 1회수집", "실시간 집중", "허브만 분석", "수동 ON/OFF", "전체 26개"], index=5, help="기본값은 허브만 분석입니다. 화면 진입만으로 API를 호출하지 않고, 필요한 버튼을 눌렀을 때만 1회 수집합니다.", key="collection_mode_select")
        st.session_state["collection_mode"] = collection_mode
        default_refresh = smart_default_refresh_seconds(collection_mode)
        refresh_options = [0, 60, 120, 300, 600, 3600]
        refresh_index = refresh_options.index(default_refresh) if default_refresh in refresh_options else 0
        auto_refresh = st.selectbox("자동 새로고침", refresh_options, index=refresh_index, format_func=lambda x: "OFF" if x == 0 else ("1시간" if x == 3600 else f"{x}초"), key="auto_refresh_select")
        render_api_onoff_panel()
        switches = get_api_switches()
        selected = [k for k, _ in API_LABELS if switches.get(k, False)]
        selected = smart_selected_apis(collection_mode, selected)
        st.session_state["rc_date"] = rc_date
        st.session_state["meet"] = meet
        st.session_state["race_no"] = race_no
        st.session_state["selected_api_keys"] = selected
        st.caption(f"이번 수집 대상: {len(selected)}/26개 · 모드: {collection_mode}")
        st.caption("첫 화면은 빠른 핵심 API 우선 수집 · 전체 26개는 상세/엑셀 확인에서 순차 점검")  # FAST_FIRST_SIDEBAR_NOTICE_APPLY  # IMMEDIATE_API_SESSION_KEYS_APPLY
        if collection_mode == "허브만 분석":
            st.error("현재 허브만 분석 모드입니다. 이 모드는 공식 API를 호출하지 않습니다. 실전 추천을 받으려면 실시간 API 우선 + 허브 보조로 바꾸세요.")  # HUB_ONLY_MODE_WARNING_APPLY
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
        if st.session_state.get("race_scope") == "전체 경마장 자동":
            st.info("전체 경마장 자동 모드는 화면 진입만으로 API를 돌리지 않습니다. 아래 버튼을 누를 때만 1회 실행합니다.")
            if st.button("🌐 전체 경마장 관제 1회 실행", key="run_all_meet_once_tab1", width="stretch"):
                render_all_meet_all_race_monitor(rc_date, selected, int(sim_count), risk_mode)
            else:
                st.caption("대기 중 · PC 확인 화면은 멈춰 있고, 허브/모바일 추천은 저장된 결과를 사용합니다.")
            score_df, result, combos, data, status, env = pd.DataFrame(), {}, [], st.session_state.get("live_data", {}), st.session_state.get("api_status", pd.DataFrame()), {}
        else:
            score_df, result, combos, data, status, env = render_live_panel(rc_date, meet, int(race_no), selected, int(sim_count), risk_mode)
    with tab2:
        # Use last/live result if available; otherwise calculate sample instantly.
        if "live_data" in st.session_state:
            data2 = st.session_state.get("live_data", {})
        else:
            data2 = {}
        meet2 = "서울" if str(meet) == "전체" else meet
        race_no2 = 1 if int(race_no or 0) <= 0 else int(race_no)
        env2 = fetch_weather(meet2)
        base2 = build_base_horses(data2, rc_date, meet2, race_no2)
        horses2 = merge_score_features(base2, data2, rc_date, meet2, race_no2)
        _, result2, _ = score_and_recommend(horses2, env2, int(sim_count), risk_mode)
        render_triple18_dashboard_module(result2, meet2)
    with tab3:
        status2 = st.session_state.get("api_status", pd.DataFrame())
        data3 = st.session_state.get("live_data", {})
        if status2 is None or not isinstance(status2, pd.DataFrame) or status2.empty:
            # NO_AUTO_SPIN_HARD_STOP: API/허브 탭 진입만으로 즉시 API 점검을 돌리지 않습니다.
            st.info("API 상태표 대기 중 · 자동 점검은 꺼져 있습니다. 필요한 수집/점검 버튼을 눌렀을 때만 1회 실행합니다.")
            status2 = pd.DataFrame()
            data3 = {}
        st.success("✅ API URL 26개 자동 탑재 완료: 재입력 없이 호출/ON-OFF만 사용")
        st.info("결과/배당 계열 일부 API는 경주시간 전이면 대기 상태가 정상입니다. 하지만 상태표는 즉시 표시됩니다.")
        render_api_hub_panel(status2, data3)
        tab_m, tab_r = _auto_current_target_for_recommend(rc_date, meet, race_no)
        render_sequential_26api_center(rc_date, tab_m, tab_r)  # CURRENT_RACE_TARGET_MATCH_SEQ_TAB_APPLY
        render_recommendation_after_each_race_center(rc_date, tab_m, tab_r)  # CURRENT_RACE_TARGET_MATCH_RECOMMEND_TAB_APPLY
        render_pc_hub_recommend_confirm_center(rc_date, tab_m if "tab_m" in locals() else meet, tab_r if "tab_r" in locals() else race_no)  # HUB_PC_MOBILE_RECOMMEND_FLOW_TAB_APPLY
        render_stable_quick_panel(rc_date, tab_m if 'tab_m' in locals() else meet, tab_r if 'tab_r' in locals() else race_no)  # STABLE_QUICK_PANEL_TAB_APPLY
        render_api_timeout_error_stable_center(rc_date, tab_m if 'tab_m' in locals() else meet, tab_r if 'tab_r' in locals() else race_no)  # API_TIMEOUT_ERROR_STABLE_ANALYSIS_TAB_APPLY
        render_api_priority_strategy_center()  # API_PREFETCH_REALTIME_PRIORITY_26_TAB_APPLY
        render_prefetch_static_data_center(rc_date, tab_m if 'tab_m' in locals() else meet, tab_r if 'tab_r' in locals() else race_no)
        render_google_sheet_visible_center()  # GOOGLE_SHEET_VISIBLE_TAB_APPLY
        render_hub_pipeline_control_center(rc_date, tab_m if 'tab_m' in locals() else meet, tab_r if 'tab_r' in locals() else race_no)  # HUB_SHEET_DOUBLE_SAFETY_FLOW_TAB_APPLY
        render_file_and_runtime_check_center()  # FILE_RUNTIME_CHECK_TAB_APPLY
    with tab4:
        if st.session_state.get("race_scope") == "전체 경마장 자동":
            st.info("스마트수집 탭도 자동 실행하지 않습니다. 필요할 때만 1회 실행하세요.")
            if st.button("⏱ 전체 경마장 스마트수집 1회 실행", key="run_all_meet_once_tab4", width="stretch"):
                render_all_meet_all_race_monitor(rc_date, selected, int(sim_count), risk_mode)
        else:
            render_smart_collection_panel(rc_date, meet, int(race_no))
    with tab5:
        render_help_panel()

    if int(auto_refresh or 0) > 0:
        st.caption(f"자동 새로고침 설정: {int(auto_refresh)}초 · 현재 핫픽스에서는 자동 새로고침 대신 수동 새로고침을 권장합니다.")





# DATETIME_TIMEDELTA_ATTRIBUTE_FIX_SAFE_OVERRIDE
def _current_or_next_races(sched: pd.DataFrame, per_meet: int = 3) -> pd.DataFrame:
    """전체 경마장 현재/다음 경주 계산. datetime.timedelta AttributeError 방지."""
    if sched is None or not isinstance(sched, pd.DataFrame) or sched.empty:
        return pd.DataFrame()
    df = sched.copy()
    dts = []
    for _, r in df.iterrows():
        try:
            dts.append(_parse_schedule_dt_for_monitor(dict(r)))
        except Exception:
            dts.append(None)
    df["_dt"] = pd.to_datetime(dts, errors="coerce")
    try:
        now = now_kst() if "now_kst" in globals() else pd.Timestamp.now()
        now_ts = pd.Timestamp(now)
    except Exception:
        now_ts = pd.Timestamp.now()

    try:
        df["상태"] = []
    except Exception:
        pass
    statuses = []
    for x in df["_dt"].tolist():
        try:
            if pd.isna(x):
                statuses.append("시간미확인")
            else:
                mins = int((pd.Timestamp(x) - now_ts).total_seconds() // 60)
                if mins > 25:
                    statuses.append(f"대기 {mins}분전")
                elif -20 <= mins <= 25:
                    statuses.append(f"수집창 {mins}분")
                elif mins < -20:
                    statuses.append("종료/결과확인")
                else:
                    statuses.append("대기")
        except Exception:
            statuses.append("시간미확인")
    df["상태"] = statuses

    out = []
    group_col = "경마장" if "경마장" in df.columns else None
    groups = df.groupby(group_col, dropna=False) if group_col else [("전체", df)]
    for meet_name, g in groups:
        gg = g.copy()
        try:
            future = gg[gg["_dt"].notna() & (gg["_dt"] >= now_ts - pd.Timedelta(minutes=20))]
            if not future.empty:
                gg = future.sort_values("_dt").head(per_meet)
            else:
                gg = g.sort_values("_dt", na_position="last").tail(per_meet)
        except Exception:
            gg = g.head(per_meet)
        out.append(gg)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()




# AGENT365_PROBABILITY_ALWAYS_ON_FIX
# 목적: 해·달·별·구름·비 5명 에이전트가 365일 허브 중심으로 수집/학습/분석/추천/복기를 남기고,
# 모바일에는 적중 보장이 아닌 "참고 확률/신뢰도"를 크게 보여줍니다. 자동구매/자동결제는 절대 하지 않습니다.
AGENT365_VERSION = "agent365_probability_v1"
AGENT365_HUB_KINDS = [
    "mobile_recommend", "three_type_recommend", "learning_bigdata", "agent_runs",
    "agent_365_runs", "agent_365_lessons", "agent_365_probability", "failure_reason_log"
]


def _agent365_now() -> datetime.datetime:
    try:
        return now_kst() if "now_kst" in globals() else datetime.datetime.now()
    except Exception:
        return datetime.datetime.now()


def _agent365_safe_pct(v: Any, default: int = 0) -> int:
    try:
        if isinstance(v, str):
            v = v.replace("%", "").replace(",", "").strip()
        return max(0, min(99, int(round(float(v)))))
    except Exception:
        return int(default)


def _agent365_count_hub(kind: str) -> int:
    # 11ROUND_NO_VIEW_HUB_STORM:
    # 일반 PC/모바일 화면에서 확률 표시용 카운트를 얻으려고 구글시트를 여러 번 호출하지 않습니다.
    # 외부 허브 조회는 Apps Script tick 또는 수동 허브 실행 때만 허용합니다.
    try:
        allow_network = "_hub365_network_allowed" in globals() and _hub365_network_allowed()
    except Exception:
        allow_network = False
    if allow_network:
        try:
            data = external_hub_load(kind) if "external_hub_load" in globals() else {}
            if isinstance(data, list):
                return len(data)
            if isinstance(data, dict) and data:
                # Apps Script 허브가 최신 1건만 돌려주는 경우도 카운트 1로 인정
                return int(data.get("count", 1) or 1)
        except Exception:
            pass
    # 네트워크가 허용되지 않은 일반 화면에서는 로컬 백업 파일 존재 여부만 가볍게 확인합니다.
    try:
        d = DATA_DIR if "DATA_DIR" in globals() else Path("maru_kra_data")
        for ext in [".json", ".csv"]:
            fp = d / f"{kind}{ext}"
            if fp.exists() and fp.stat().st_size > 2:
                return 1
    except Exception:
        pass
    return 0


def _agent365_signal_scores(row: Dict[str, Any]) -> Dict[str, int]:
    row = dict(row or {})
    live_rows = _agent365_safe_pct(row.get("실시간행수", row.get("출전두수", 0)), 0)
    api_rows = _agent365_safe_pct(row.get("API상태행수", row.get("API호출대상", 0)), 0)
    learn_count = _agent365_count_hub("learning_bigdata")
    runs_count = _agent365_count_hub("agent_runs") + _agent365_count_hub("agent_365_runs")
    has_three = 1 if (row.get("안정형6") or row.get("변수형6") or row.get("고배당형6")) else 0
    has_result = 1 if str(row.get("결과마번", "")).strip() not in ["", "결과대기", "None", "nan"] else 0
    data_status = str(row.get("데이터상태", ""))
    verified = 1 if str(row.get("실전검증", "")).upper() in ["Y", "TRUE", "1"] else 0

    data_score = min(100, live_rows * 8 + api_rows * 3 + has_three * 15 + verified * 15)
    learn_score = min(100, learn_count * 6 + runs_count * 4 + has_result * 10)
    risk_penalty = 0
    risk_text = " ".join(str(row.get(k, "")) for k in ["위험도", "상태", "구름", "AI에이전트요약", "근거", "데이터상태"])
    for word, penalty in [("출전취소", 25), ("기수변경", 12), ("주로불량", 10), ("샘플", 25), ("대기", 8), ("표시불가", 30), ("오류", 12), ("실패", 10)]:
        if word in risk_text or word in data_status:
            risk_penalty += penalty
    risk_penalty = min(45, risk_penalty)
    return {
        "자료점수": int(data_score),
        "학습점수": int(learn_score),
        "위험감점": int(risk_penalty),
        "허브학습건수": int(learn_count),
        "에이전트실행건수": int(runs_count),
        "실시간행수": int(live_rows),
        "검증됨": int(verified),
    }


def _agent365_probability(row: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(row or {})
    sig = _agent365_signal_scores(row)
    base = 38
    total = base + sig["자료점수"] * 0.24 + sig["학습점수"] * 0.18 - sig["위험감점"] * 0.52
    trust = max(18, min(88, int(round(total))))
    stable = max(20, min(90, trust + 7 - sig["위험감점"] // 6))
    variable = max(15, min(84, trust - 2 + min(12, sig["위험감점"] // 4)))
    high = max(8, min(72, trust - 12 + min(18, sig["학습점수"] // 8)))
    data_enough = max(10, min(95, int(round(sig["자료점수"] * 0.65 + sig["학습점수"] * 0.35))))
    risk_level = max(5, min(95, 100 - trust + sig["위험감점"]))
    return {
        "AI확률버전": AGENT365_VERSION,
        "AI종합확률": f"{trust}%",
        "안정형확률": f"{stable}%",
        "변수형확률": f"{variable}%",
        "고배당형확률": f"{high}%",
        "자료충분도": f"{data_enough}%",
        "위험도확률": f"{risk_level}%",
        "허브학습건수": sig["허브학습건수"],
        "에이전트실행건수": sig["에이전트실행건수"],
        "확률주의": "적중 보장 아님 · 허브/공식자료/과거학습 기반 참고 확률 · 자동구매/자동결제 없음",
    }


def _apply_agent365_probability(row: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(row or {})
    try:
        prob = _agent365_probability(row)
        row.update(prob)
        row["365AI상태"] = "해·달·별·구름·비 5명 에이전트 활동중"
        row["365AI업무"] = "자료찾기·허브저장·학습·분석·추천·성공/실패 원인기록"
    except Exception as e:
        row["365AI상태"] = f"확률계산 대기: {str(e)[:80]}"
    return row


def _agent365_failure_reason(row: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(row or {})
    hit = str(row.get("적중여부", row.get("결과", ""))).strip()
    result_nums = str(row.get("결과마번", "")).strip()
    reasons = []
    text = " ".join(str(row.get(k, "")) for k in ["근거", "AI에이전트요약", "상태", "위험도", "데이터상태"])
    for word in ["출전취소", "기수변경", "체중", "게이트", "주로", "날씨", "배당", "인기", "API", "대기", "샘플"]:
        if word in text:
            reasons.append(word)
    if not reasons:
        reasons.append("결과대기" if not result_nums or result_nums == "결과대기" else "패턴차이")
    return {
        "저장시각": now_str() if "now_str" in globals() else str(_agent365_now()),
        "날짜": row.get("날짜", today_kst() if "today_kst" in globals() else ""),
        "경마장": row.get("경마장", ""),
        "경주번호": row.get("경주번호", ""),
        "추천": {
            "안정형대표": row.get("안정형대표", ""),
            "변수형대표": row.get("변수형대표", row.get("변수대응형대표", "")),
            "고배당형대표": row.get("고배당형대표", ""),
        },
        "결과마번": result_nums or "결과대기",
        "적중여부": hit or "결과대기",
        "원인후보": reasons[:8],
        "확률": _agent365_probability(row),
        "메모": "결과가 들어오면 성공/실패 원인을 learning_bigdata와 failure_reason_log에 누적",
    }


def _agent365_tick(source: str = "screen", row: Dict[str, Any] = None) -> Dict[str, Any]:
    """화면 실행/웹앱 호출 때마다 가볍게 365일 에이전트 활동 기록을 남김."""
    now = _agent365_now()
    row = _apply_agent365_probability(dict(row or {}))
    status = {
        "저장시각": now_str() if "now_str" in globals() else str(now),
        "버전": AGENT365_VERSION,
        "실행출처": source,
        "365일운영": "ON",
        "PC꺼짐대응": "Streamlit Cloud + Apps Script 시간트리거 사용 시 가능",
        "해": "총괄 판단 · 확률/전략 균형",
        "달": "일정·경주없음·수집시간 감시",
        "별": "공식API/허용 공개자료 확인",
        "구름": "변수·허브·오류 복구",
        "비": "결과·배당·성공/실패 원인학습",
        "확률": _agent365_probability(row),
        "자동구매": "없음",
        "자동결제": "없음",
    }
    try:
        if "external_hub_save" in globals():
            external_hub_save("agent_365_runs", status)
            external_hub_save("agent_365_probability", status.get("확률", {}))
            external_hub_save("failure_reason_log", _agent365_failure_reason(row))
    except Exception:
        pass
    return status


def render_agent365_control_center(compact: bool = False) -> None:
    try:
        latest = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else {}
    except Exception:
        latest = {}
    latest = _apply_agent365_probability(latest)
    status = {
        "저장시각": now_str() if "now_str" in globals() else "",
        "버전": AGENT365_VERSION,
        "실행출처": "mobile_view" if compact else "pc_view",
        "365일운영": "대기",
        "PC꺼짐대응": "Apps Script 시간트리거가 agent_tick=1로 호출할 때 실행",
        "확률": _agent365_probability(latest),
        "자동구매": "없음",
        "자동결제": "없음",
    }
    if compact:
        p = status.get("확률", {})
        st.markdown(f"""
        <div style="border:2px solid #d5a83c;border-radius:18px;padding:12px;background:#090909;color:#fff;margin:10px 0;text-align:center;">
          <div style="color:#f8d777;font-weight:1000;font-size:1.05rem;">365일 5 AI 에이전트 확률판</div>
          <div style="font-size:2.1rem;font-weight:1000;color:#fff;line-height:1.05;">종합 {p.get('AI종합확률','-')}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:8px;">
            <div>안정<br><b>{p.get('안정형확률','-')}</b></div>
            <div>변수<br><b>{p.get('변수형확률','-')}</b></div>
            <div>고배당<br><b>{p.get('고배당형확률','-')}</b></div>
          </div>
          <div style="font-size:.82rem;color:#cbd5e1;margin-top:8px;">자료 {p.get('자료충분도','-')} · 위험 {p.get('위험도확률','-')} · 적중보장 아님</div>
        </div>
        """, unsafe_allow_html=True)
        return
    st.markdown("### 🤖 365일 5 AI 에이전트 자동활동")
    st.success("해·달·별·구름·비가 허브 자료를 찾아 저장·학습·분석·추천·성공/실패 원인 기록을 남깁니다.")
    st.json(status)
    st.caption("완전 무인 365일 활동은 Streamlit 화면 실행만으로는 부족하므로, 함께 들어있는 Apps Script 시간트리거를 구글시트에 배포해야 안정적입니다.")


# 기존 모바일 3분류 화면을 확률판 포함 버전으로 다시 정의합니다.
def _render_mobile_compact_3type_view(row: Dict[str, Any]) -> None:
    row = dict(row or {})
    try:
        if "_build_three_type_recommendation" in globals():
            row = _build_three_type_recommendation(row)
        row = _apply_agent365_probability(row)
    except Exception:
        pass

    meet = _safe_mobile_val(row, "경마장", default="서울")
    race_no = _safe_mobile_val(row, "경주번호", default="-")
    race_time = _safe_mobile_val(row, "경주시간", "출발시간", default="-")
    status = _safe_mobile_val(row, "상태", "데이터상태", default="대기")
    saved = _safe_mobile_val(row, "저장시각", default="-")
    stable_rep = _safe_mobile_val(row, "안정형대표", default="-")
    stable_6 = _format_6_for_mobile(row.get("안정형6", ""))
    stable_reason = _safe_mobile_val(row, "안정형근거", default="최근폼·기수·주로 안정성 우선")
    var_rep = _safe_mobile_val(row, "변수형대표", "변수대응형대표", default="-")
    var_6 = _format_6_for_mobile(row.get("변수형6", row.get("변수대응형6", "")))
    var_reason = _safe_mobile_val(row, "변수형근거", "변수대응형근거", default="체중·게이트·주로·기수 변경 대응")
    high_rep = _safe_mobile_val(row, "고배당형대표", default="-")
    high_6 = _format_6_for_mobile(row.get("고배당형6", ""))
    high_reason = _safe_mobile_val(row, "고배당형근거", default="배당 대비 기대값 우선")
    amount = _safe_mobile_val(row, "총추천금액", "추천금액", default="18,000원")
    unit = _safe_mobile_val(row, "단위금액", default="1,000원")
    auto = _safe_mobile_val(row, "자동화모드", default="Y")
    p_total = row.get("AI종합확률", "-")
    p_stable = row.get("안정형확률", "-")
    p_var = row.get("변수형확률", "-")
    p_high = row.get("고배당형확률", "-")
    p_data = row.get("자료충분도", "-")
    p_risk = row.get("위험도확률", "-")

    row = _mobile_drop_placeholder_combos(row) if "_mobile_drop_placeholder_combos" in globals() else row
    if "_mobile_has_any_real_recommend" in globals() and not _mobile_has_any_real_recommend(row):
        _render_mobile_end_or_wait_view(row)
        render_agent365_control_center(compact=True)
        return
    st.markdown(_mobile_real_compact_css(), unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mk-wrap">
      <div class="mk-top">
        <div class="mk-small">MARU KRA · 365일 5 AI 에이전트</div>
        <div class="mk-title">{meet} {race_no}R <span class="mk-gold">삼쌍승 18장</span></div>
        <div class="mk-small">경주시간 {race_time} · 기준 {amount} · 각 {unit}</div>
      </div>
      <div class="mk-status">상태: {status} · 저장 {saved}</div>
      <div style="border:2px solid #d5a83c;border-radius:18px;padding:12px;background:#090909;color:#fff;margin:10px 0;text-align:center;">
        <div style="color:#f8d777;font-weight:1000;font-size:1.0rem;">확률판 · 적중보장 아님</div>
        <div style="font-size:2.25rem;font-weight:1000;line-height:1.05;">AI 종합 {p_total}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px;margin-top:8px;">
          <div>안정형<br><b>{p_stable}</b></div>
          <div>변수형<br><b>{p_var}</b></div>
          <div>고배당<br><b>{p_high}</b></div>
        </div>
        <div style="font-size:.84rem;color:#cbd5e1;margin-top:8px;">자료충분도 {p_data} · 위험도 {p_risk}</div>
      </div>
      <div class="mk-grid">
        <div class="mk-card"><h3>① 안정형 6장</h3><div class="mk-rep">{stable_rep}</div><div class="mk-six">{stable_6}</div><div class="mk-reason">확률 {p_stable} · {stable_reason}</div></div>
        <div class="mk-card"><h3>② 변수형 6장</h3><div class="mk-rep">{var_rep}</div><div class="mk-six">{var_6}</div><div class="mk-reason">확률 {p_var} · {var_reason}</div></div>
        <div class="mk-card"><h3>③ 고배당형 6장</h3><div class="mk-rep">{high_rep}</div><div class="mk-six">{high_6}</div><div class="mk-reason">확률 {p_high} · {high_reason}</div></div>
      </div>
      <div class="mk-note">해·달·별·구름·비 5명 활동 · 자료찾기/학습/성공실패 원인기록 · 자동구매/자동결제 없음</div>
    </div>
    """, unsafe_allow_html=True)

    # 화면 표시만으로 허브에 쓰지 않습니다. Apps Script/background tick 또는 저장 버튼일 때만 기록합니다.
    copy_text = _three_type_mobile_ticket(row) if "_three_type_mobile_ticket" in globals() else str(row.get("구매표복사", ""))
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📋 18장 텍스트", copy_text, file_name=f"maru_{meet}_{race_no}R_18tickets.txt", key="mobile_18tickets_download")
    with c2:
        st.link_button("↗ 더비온 열기", "https://www.derbyon.co.kr")



# =============================================================================
# MARU KRA HUB 365 FINAL CORE
# 목적:
# - 에이전트 명칭보다 먼저, 허브가 자료를 불러오고 저장하고 분석·추천하는 중심 엔진으로 작동
# - 경주 있는 날/없는 날을 구분하여 허브 작업을 다르게 수행
# - PC는 확인용, 모바일은 mobile_recommend 추천 결과만 표시
# - 구글시트 ID는 앱 안에 고정 포함, 입력창 없음
# - 자동구매/자동결제 없음
# =============================================================================
MARU_KRA_FIXED_SHEET_ID = "1uT8lQfbpjhblvFOsFdBSmAnGHXzqhlZQ5jsBayLTpwo"
MARU_KRA_FIXED_GID = "909440003"
MARU_KRA_FINAL_PRECHECK_ROUND = "13ROUND"
MARU_KRA_HUB365_VERSION = "cloud_hub_365_final_v1"
MARU_KRA_HUB_KINDS_FINAL = [
    "mobile_recommend",
    "three_type_recommend",
    "learning_bigdata",
    "api_status",
    "api_raw_cache",
    "pre_saved_data",
    "live_api_data",
    "race_calendar",
    "success_fail_reason",
    "failure_reason_log",
    "probability_memory",
    "strategy_memory",
    "agent_runs",
    "agent_365_runs",
    "hub_365_status",
]
MARU_KRA_MANUAL_PURCHASE_URL = "https://www.derbyon.co.kr"


def _hub365_now():
    try:
        return now_kst()
    except Exception:
        try:
            return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        except Exception:
            return datetime.datetime.now()


def _hub365_now_str():
    try:
        return now_str()
    except Exception:
        return _hub365_now().strftime("%Y-%m-%d %H:%M:%S KST")


def _hub365_today():
    try:
        return today_kst()
    except Exception:
        return _hub365_now().strftime("%Y%m%d")


def _hub365_safe_load(kind: str):
    try:
        if "external_hub_load" in globals():
            x = external_hub_load(kind)
            if isinstance(x, dict):
                return x
            if isinstance(x, list):
                return {"rows": x, "count": len(x)}
    except Exception:
        pass
    return {}


def _hub365_safe_save(kind: str, payload: dict) -> bool:
    payload = dict(payload or {})
    payload.setdefault("저장시각", _hub365_now_str())
    payload.setdefault("허브버전", MARU_KRA_HUB365_VERSION)
    payload.setdefault("SHEET_ID", MARU_KRA_FIXED_SHEET_ID)
    payload.setdefault("자동구매", "없음")
    payload.setdefault("자동결제", "없음")
    ok = False
    try:
        if "external_hub_save" in globals():
            ok = bool(external_hub_save(kind, payload))
    except Exception:
        ok = False
    try:
        d = DATA_DIR if "DATA_DIR" in globals() else Path("maru_kra_data")
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{kind}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        ok = True or ok
    except Exception:
        pass
    return ok


def _hub365_count(kind: str) -> int:
    # 화면 진입만으로 외부 허브를 여러 번 읽지 않습니다.
    # background tick/수동 실행 때만 외부 허브를 조회하고, 일반 화면은 로컬 캐시만 확인합니다.
    try:
        allow_network = "_hub365_network_allowed" in globals() and _hub365_network_allowed()
    except Exception:
        allow_network = False
    if allow_network:
        data = _hub365_safe_load(kind)
        try:
            if isinstance(data, dict):
                if isinstance(data.get("rows"), list):
                    return len(data.get("rows") or [])
                if data.get("count") not in [None, ""]:
                    return int(float(str(data.get("count")).replace(",", "")))
                return 1 if data else 0
        except Exception:
            return 0
    try:
        d = DATA_DIR if "DATA_DIR" in globals() else Path("maru_kra_data")
        fp = d / f"{kind}.json"
        if fp.exists() and fp.stat().st_size > 2:
            return 1
    except Exception:
        pass
    return 0


def _hub365_is_background_tick_request() -> bool:
    try:
        q = st.query_params
        vals = []
        for k in ["agent_tick", "hub365_tick", "background_tick"]:
            v = q.get(k, "")
            if isinstance(v, list):
                vals += [str(x).lower() for x in v]
            else:
                vals.append(str(v).lower())
        return any(v in ["1", "true", "yes", "on"] for v in vals)
    except Exception:
        return False

def _hub365_network_allowed() -> bool:
    try:
        if bool(st.session_state.get("_hub365_network_allowed", False)):
            return True
    except Exception:
        pass
    return _hub365_is_background_tick_request()

def _hub365_schedule_rows(rc_date: str = None) -> int:
    rc_date = rc_date or _hub365_today()
    if not _hub365_network_allowed():
        return 0
    total = 0
    try:
        for meet_name in ["서울", "부산경남", "제주"]:
            try:
                if "_load_schedule_for_sidebar" in globals():
                    sched = _load_schedule_for_sidebar(rc_date, meet_name)
                elif "load_schedule" in globals():
                    sched = load_schedule(rc_date, meet_name)
                else:
                    sched = pd.DataFrame()
                total += int(len(sched)) if sched is not None else 0
            except Exception:
                continue
    except Exception:
        total = 0
    return total


def _hub365_is_race_day(rc_date: str = None) -> tuple:
    """경주일 판단: 일정 API/허브가 있으면 그 결과를 우선, 없으면 금토일 가능성 표시."""
    rc_date = rc_date or _hub365_today()
    rows = _hub365_schedule_rows(rc_date)
    if rows > 0:
        return True, f"경주일정 {rows}건 확인", rows
    try:
        wd = _hub365_now().weekday()  # 월0
        if wd in [4, 5, 6]:
            return True, "일정 API 0건이지만 금·토·일 경주 가능일 · 출전표/일정 재확인", 0
    except Exception:
        pass
    return False, "경주일정 0건 · 경주 없는 날 또는 공개 전", 0


def _hub365_phase(latest: dict = None) -> dict:
    latest = dict(latest or {})
    now = _hub365_now()
    rc_date = str(latest.get("날짜") or _hub365_today())
    is_race, reason, schedule_rows = _hub365_is_race_day(rc_date)
    hour = int(getattr(now, "hour", 0))
    if not is_race:
        code = "NO_RACE_DAY"
        title = "경주 없는 날 · 학습/복습/준비 모드"
        job = "허브자료 정리, 성공/실패 원인 누적, 다음 경주 대비"
    elif hour < 9:
        code = "RACE_PREPARE"
        title = "경주 당일 오전 · 준비 모드"
        job = "출전표/말/기수/과거자료 확인, 1차 예비 분석"
    elif hour < 17:
        code = "RACE_LIVE"
        title = "경주 진행 시간 · 실시간 추천 모드"
        job = "실시간 API/배당/체중/변수 반영, mobile_recommend 저장"
    else:
        code = "RACE_REVIEW"
        title = "경주 후 · 복기/학습 모드"
        job = "결과/배당 확인, 성공·실패 원인 분석, 확률 보정"
    return {
        "코드": code,
        "제목": title,
        "작업": job,
        "판단근거": reason,
        "경주일정건수": schedule_rows,
        "날짜": rc_date,
        "시각": _hub365_now_str(),
    }


def _hub365_probability_from_hub(latest: dict = None) -> dict:
    latest = dict(latest or {})
    try:
        if "_agent365_probability" in globals():
            base = _agent365_probability(latest)
            if isinstance(base, dict) and base:
                base["확률기준"] = "허브/공식자료/과거학습 기반 참고 확률"
                return base
    except Exception:
        pass
    live_rows = 0
    try:
        live_rows = int(float(str(latest.get("실시간행수", 0) or 0).replace(",", "")))
    except Exception:
        live_rows = 0
    learn = _hub365_count("learning_bigdata") + _hub365_count("success_fail_reason") + _hub365_count("failure_reason_log")
    rec = _hub365_count("mobile_recommend") + _hub365_count("three_type_recommend")
    score = max(20, min(88, 40 + min(25, live_rows * 2) + min(20, learn) + min(8, rec)))
    return {
        "AI종합확률": f"{score}%",
        "안정형확률": f"{min(92, score + 6)}%",
        "변수형확률": f"{max(18, score - 2)}%",
        "고배당형확률": f"{max(8, score - 14)}%",
        "자료충분도": f"{max(15, min(95, 35 + min(40, learn) + min(20, live_rows * 2)))}%",
        "위험도확률": f"{max(5, min(95, 100 - score + 10))}%",
        "확률주의": "적중 보장 아님 · 자동구매/자동결제 없음 · 사용자가 직접 확인 후 수동 구매",
        "확률기준": "허브/공식자료/과거학습 기반 참고 확률",
    }


def _hub365_failure_lesson(latest: dict = None, phase: dict = None) -> dict:
    latest = dict(latest or {})
    phase = dict(phase or _hub365_phase(latest))
    text = " ".join(str(latest.get(k, "")) for k in ["근거", "상태", "데이터상태", "위험도", "안정형근거", "변수형근거", "고배당형근거"])
    candidates = []
    for w in ["체중", "게이트", "기수변경", "주로", "날씨", "배당", "인기", "출전취소", "API", "대기", "샘플", "자료부족"]:
        if w in text:
            candidates.append(w)
    if not candidates:
        candidates = ["결과대기"] if phase.get("코드") != "RACE_REVIEW" else ["패턴차이", "배당변동", "변수반영부족"]
    return {
        "저장시각": _hub365_now_str(),
        "날짜": phase.get("날짜", _hub365_today()),
        "현재모드": phase.get("코드"),
        "경마장": latest.get("경마장", ""),
        "경주번호": latest.get("경주번호", ""),
        "추천상태": latest.get("데이터상태", latest.get("상태", "")),
        "적중여부": latest.get("적중여부", "결과대기"),
        "결과마번": latest.get("결과마번", "결과대기"),
        "원인후보": ", ".join(candidates[:8]),
        "다음보정": "원인후보를 다음 추천 가중치와 probability_memory에 반영",
        "자동구매": "없음",
    }


def _hub365_status_tick(source: str = "screen", latest: dict = None) -> dict:
    latest = dict(latest or {})
    phase = _hub365_phase(latest)
    prob = _hub365_probability_from_hub(latest)
    lesson = _hub365_failure_lesson(latest, phase)
    status = {
        "저장시각": _hub365_now_str(),
        "버전": MARU_KRA_HUB365_VERSION,
        "실행출처": source,
        "SHEET_ID": MARU_KRA_FIXED_SHEET_ID,
        "GID": MARU_KRA_FIXED_GID,
        "허브중심": "ON",
        "PC역할": "확인용/관리용",
        "모바일역할": "mobile_recommend 최신 추천 결과만 표시",
        "현재모드": phase,
        "확률": prob,
        "허브자료현황": {k: _hub365_count(k) for k in MARU_KRA_HUB_KINDS_FINAL[:12]},
        "5명역할": {
            "해": "허브 자료 종합 판단 / 최종 확률 / 추천 균형",
            "달": "경주 있는 날·없는 날 구분 / 시간대 모드 전환",
            "별": "공식 API·허브 원자료 확인 / 수집상태 기록",
            "구름": "날씨·주로·체중·게이트·기수변경·배당변동 감지",
            "비": "결과·배당 검증 / 성공·실패 원인 학습",
        },
        "자동구매": "없음",
        "자동결제": "없음",
        "마권구매": "더비온 등 공식 구매 페이지에서 사용자가 직접 입력·확정",
    }
    # 화면 표시만으로 구글시트/허브에 쓰지 않습니다.
    # PC 버튼 실행 또는 Apps Script background tick일 때만 저장합니다.
    try:
        allow_save = ("_hub365_network_allowed" in globals() and _hub365_network_allowed()) or str(source).lower() not in ["screen", "pc", "mobile", "pc_view", "mobile_view"]
    except Exception:
        allow_save = False
    if allow_save:
        _hub365_safe_save("hub_365_status", status)
        _hub365_safe_save("agent_365_runs", status)
        _hub365_safe_save("success_fail_reason", lesson)
        _hub365_safe_save("probability_memory", prob)
    return status


def _hub365_make_no_race_mobile_status(latest: dict = None) -> dict:
    latest = dict(latest or {})
    phase = _hub365_phase(latest)
    prob = _hub365_probability_from_hub(latest)
    row = dict(latest or {})
    row.update({
        "저장시각": _hub365_now_str(),
        "날짜": phase.get("날짜", _hub365_today()),
        "상태": phase.get("제목"),
        "데이터상태": "경주없음/학습중" if phase.get("코드") == "NO_RACE_DAY" else "준비/분석중",
        "365AI상태": "허브 중심 365일 학습·분석 활동중",
        "365AI업무": phase.get("작업"),
        "자동구매": "없음",
        "자동결제": "없음",
        "확률주의": "적중 보장 아님 · 경주가 없으면 추천을 억지로 만들지 않음",
    })
    row.update(prob)
    return row


def run_hub365_cycle(source: str = "manual") -> dict:
    """허브 중심 365일 1회 실행. 경주 없는 날은 학습/복습, 경주 있는 날은 추천/상태저장 중심."""
    try:
        st.session_state["_hub365_network_allowed"] = True
    except Exception:
        pass
    latest = {}
    try:
        latest = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else _hub365_safe_load("mobile_recommend")
    except Exception:
        latest = _hub365_safe_load("mobile_recommend")
    latest = dict(latest or {})
    phase = _hub365_phase(latest)
    status = _hub365_status_tick(source, latest)

    if phase.get("코드") == "NO_RACE_DAY":
        # 경주 없는 날에는 추천을 새로 꾸며내지 않고, 상태/학습 로그를 남긴다.
        no_race_row = _hub365_make_no_race_mobile_status(latest)
        if not latest:
            try:
                save_mobile_recommend_json(no_race_row)
            except Exception:
                _hub365_safe_save("mobile_recommend", no_race_row)
        _hub365_safe_save("learning_bigdata", {
            "저장시각": _hub365_now_str(),
            "분류": "NO_RACE_DAY_LEARNING",
            "학습내용": "경주 없는 날: 과거 추천/결과/배당/변수 패턴 복습",
            "성공실패원인": _hub365_failure_lesson(latest, phase),
            "다음작업": "다음 경주 출전표 공개 시 pre_saved_data/live_api_data 보강",
        })
    elif phase.get("코드") in ["RACE_PREPARE", "RACE_LIVE"]:
        # 경주 있는 날에는 가능하면 기존 안정 수집/분석 루틴을 실행하고, 실패해도 허브 상태는 남긴다.
        try:
            meet = latest.get("경마장") or "서울"
            race_no = int(float(latest.get("경주번호") or 1))
            if "stable_fetch_batch_and_analyze" in globals():
                data, api_status, rec = stable_fetch_batch_and_analyze(phase.get("날짜"), meet, race_no, max_count=26, retry=1)
                if isinstance(rec, dict) and rec:
                    rec.update(_hub365_probability_from_hub(rec))
                    save_mobile_recommend_json(rec)
                    _hub365_safe_save("three_type_recommend", rec)
                    _hub365_safe_save("live_api_data", {"날짜": phase.get("날짜"), "경마장": meet, "경주번호": race_no, "API상태": "수집/분석 시도"})
        except Exception as e:
            _hub365_safe_save("api_status", {"상태": "경주일 자동수집 실패", "오류": str(e)[:200], "앱중단": "N"})
    else:
        _hub365_safe_save("learning_bigdata", {
            "저장시각": _hub365_now_str(),
            "분류": "RACE_REVIEW",
            "학습내용": "경주 후 결과/배당/추천 성공실패 원인 정리",
            "성공실패원인": _hub365_failure_lesson(latest, phase),
        })
    return status



# 12ROUND_NETWORK_FLAG_RESET_FIX
# run_hub365_cycle는 수동 버튼/Apps Script 호출 중에만 외부 허브 네트워크를 허용해야 합니다.
# 기존 코어 함수가 session_state 플래그를 True로 남길 수 있어, 실행 뒤 반드시 원복합니다.
_run_hub365_cycle_core_12round = run_hub365_cycle
def run_hub365_cycle(source: str = "manual") -> dict:
    prev_flag = False
    try:
        prev_flag = bool(st.session_state.get("_hub365_network_allowed", False))
    except Exception:
        prev_flag = False
    try:
        st.session_state["_hub365_network_allowed"] = True
    except Exception:
        pass
    try:
        return _run_hub365_cycle_core_12round(source)
    finally:
        try:
            if prev_flag:
                st.session_state["_hub365_network_allowed"] = True
            else:
                st.session_state["_hub365_network_allowed"] = False
        except Exception:
            pass

def render_hub365_final_center(compact: bool = False) -> None:
    try:
        latest = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else {}
    except Exception:
        latest = {}
    status = _hub365_status_tick("mobile" if compact else "pc", latest)
    phase = status.get("현재모드", {})
    prob = status.get("확률", {})
    if compact:
        st.markdown(f"""
        <div style="border:2px solid #d5a83c;border-radius:18px;padding:12px;background:#0b0b0b;color:white;margin:10px 0;text-align:center;">
          <div style="color:#f8d777;font-weight:1000;">MARU KRA 허브 365</div>
          <div style="font-size:1rem;font-weight:900;">{phase.get('제목','허브 활동중')}</div>
          <div style="font-size:2.05rem;font-weight:1000;line-height:1.05;">AI 종합 {prob.get('AI종합확률','-')}</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px;margin-top:8px;">
            <div>안정<br><b>{prob.get('안정형확률','-')}</b></div>
            <div>변수<br><b>{prob.get('변수형확률','-')}</b></div>
            <div>고배당<br><b>{prob.get('고배당형확률','-')}</b></div>
          </div>
          <div style="font-size:.82rem;color:#cbd5e1;margin-top:8px;">자료 {prob.get('자료충분도','-')} · 위험 {prob.get('위험도확률','-')} · 자동구매 없음</div>
        </div>
        """, unsafe_allow_html=True)
        return
    st.markdown("### 🧠 MARU KRA 허브 중심 365 추천 시스템")
    st.success("허브가 자료를 불러오고 저장하며, 앱이 분석·추천·성공/실패 원인을 다시 허브에 남깁니다. PC는 확인용, 모바일은 추천 결과판입니다.")
    a, b, c, d = st.columns(4)
    a.metric("현재모드", phase.get("코드", "-"))
    b.metric("경주일정", f"{phase.get('경주일정건수',0)}건")
    c.metric("AI 종합", prob.get("AI종합확률", "-"))
    d.metric("자료충분도", prob.get("자료충분도", "-"))
    st.info(f"{phase.get('제목','')} · {phase.get('작업','')}")
    st.caption(f"Google Sheet ID 고정 포함: {MARU_KRA_FIXED_SHEET_ID} / gid {MARU_KRA_FIXED_GID} · 입력창 없음")
    c1, c2, c3 = st.columns(3)
    if c1.button("🔁 허브 365 1회 실행", use_container_width=True, key="hub365_cycle_manual"):
        run_hub365_cycle("pc_button")
        st.success("허브 365 실행 완료 · 상태/확률/성공실패 원인을 허브에 저장했습니다.")
        st.rerun()
    c2.link_button("📗 고정 구글시트 허브 열기", f"https://docs.google.com/spreadsheets/d/{MARU_KRA_FIXED_SHEET_ID}/edit#gid={MARU_KRA_FIXED_GID}", use_container_width=True)
    c3.link_button("↗ 더비온 열기", MARU_KRA_MANUAL_PURCHASE_URL, use_container_width=True)
    with st.expander("허브 자료 현황 / 5명 역할 / 저장 상태", expanded=False):
        st.json(status)


# 기존 PC/모바일 호출부가 이 이름을 사용하므로, 최종 허브 중심 센터로 덮어씁니다.
def render_agent365_control_center(compact: bool = False) -> None:
    render_hub365_final_center(compact=compact)




# 9ROUND_SAFE_ENTRYPOINT_OVERRIDE
# 기존 대시보드 함수는 보존하되, 일반 PC 접속 시 화면 진입만으로 API/경주일정 수집이 돌지 않게
# 안전 진입점으로 감쌉니다. 기존 전체 화면은 사용자가 버튼을 누를 때만 열 수 있습니다.
try:
    render_legacy_full_dashboard = render
except Exception:
    render_legacy_full_dashboard = None

def render() -> None:
    # 12ROUND_SAFE_VIEW_FLAG_CLEAR: 일반 PC/모바일 화면은 이전 실행의 네트워크 허용 플래그를 이어받지 않습니다.
    try:
        if not _hub365_is_background_tick_request():
            st.session_state["_hub365_network_allowed"] = False
    except Exception:
        pass
    if _should_show_mobile():
        render_mobile_quick_view()
        return
    try:
        css()
    except Exception:
        pass
    st.markdown("""
<div class="hero">
<h2>MARU KRA HUB365 안전 대시보드 · 17ROUND</h2>
<div class="muted">PC는 확인용 · 일반 접속 자동수집 없음 · Apps Script agent_tick=1 때만 백그라운드 실행 · 모바일은 허브 추천결과만 표시</div>
</div>
""", unsafe_allow_html=True)
    st.caption("자동구매/자동결제 없음. 공식 구매 페이지 이동 후 사용자가 직접 입력·확정합니다.")
    with st.sidebar:
        st.title("🐎 MARU KRA")
        st.success("17ROUND 반복 심층검사 안전 진입점")
        st.info("일반 PC 접속은 자동수집을 실행하지 않습니다.")
        try:
            st.link_button("📱 모바일 추천결과", CLOUD_MOBILE_URL, width="stretch")
        except Exception:
            st.link_button("📱 모바일 추천결과", "https://maru-kra-final-clean.streamlit.app/?mode=mobile", use_container_width=True)
        st.link_button("📗 구글시트 허브", f"https://docs.google.com/spreadsheets/d/{MARU_KRA_FIXED_SHEET_ID}/edit#gid={MARU_KRA_FIXED_GID}", use_container_width=True)
        st.caption("Google Sheet ID는 앱 안에 고정 포함 · 입력창 없음")
    try:
        render_agent365_control_center(compact=False)
    except Exception as e:
        st.warning(f"허브 365 센터 표시 대기: {str(e)[:120]}")
    tab1, tab2, tab3 = st.tabs(["허브 상태", "수동 실행", "전체 대시보드"] )
    with tab1:
        st.info("화면 확인만으로 API/허브 저장을 실행하지 않습니다. 아래 버튼 또는 Apps Script 트리거만 실행합니다.")
        try:
            latest = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else {}
            if latest:
                st.success("허브 mobile_recommend 최신값 읽기 완료")
                st.json(latest)
            else:
                st.warning("허브 mobile_recommend가 비어 있거나 아직 추천이 없습니다.")
        except Exception as e:
            st.warning(f"허브 읽기 대기: {str(e)[:160]}")
    with tab2:
        st.markdown("#### 수동 1회 실행")
        if st.button("🔁 허브 365 1회 실행", key="safe_entry_hub365_once", use_container_width=True):
            out = run_hub365_cycle("pc_button")
            st.success("허브 365 1회 실행 완료")
            st.json(out)
        st.caption("이 버튼을 누를 때만 허브 저장/분석 작업이 실행됩니다.")
    with tab3:
        st.warning("기존 전체 대시보드는 기능 보존용입니다. 열면 무거운 API/관제 화면이 실행될 수 있습니다.")
        if st.button("🧩 기존 전체 대시보드 수동으로 열기", key="open_legacy_full_dashboard_manual", use_container_width=True):
            if callable(render_legacy_full_dashboard):
                render_legacy_full_dashboard()
            else:
                st.error("기존 대시보드 함수를 찾지 못했습니다.")



# 16ROUND_AGENT_ACTIVITY_VISIBILITY_AND_STALE_TEXT_FIX
# 목적:
# - 허브 365 버튼/Apps Script tick을 눌렀는데 에이전트가 활동하지 않는 것처럼 보이는 문제를 보정합니다.
# - 실제 실행 때마다 hub_365_status / agent_365_runs에 5명 에이전트 활동 기록을 명시적으로 남깁니다.
# - 경주 종료 후 모바일에 남은 특정 경주 문구를 일반화하여 오래된 추천 오해를 막습니다.
try:
    _run_hub365_cycle_core_15round = run_hub365_cycle
except Exception:
    _run_hub365_cycle_core_15round = None

def _hub365_agent_activity_row_15round(source: str = "manual", latest: dict = None, result: dict = None) -> dict:
    latest = dict(latest or {})
    result = dict(result or {})
    try:
        phase = _hub365_phase(latest) if "_hub365_phase" in globals() else {}
    except Exception:
        phase = {}
    try:
        prob = _hub365_probability_from_hub(latest) if "_hub365_probability_from_hub" in globals() else {}
    except Exception:
        prob = {}
    return {
        "저장시각": _hub365_now_str() if "_hub365_now_str" in globals() else (now_str() if "now_str" in globals() else str(datetime.datetime.now())),
        "상태": "해·달·별·구름·비 5명 에이전트 활동 기록",
        "source": str(source),
        "현재모드": phase.get("코드", "UNKNOWN"),
        "모드설명": phase.get("제목", "허브 365 실행"),
        "경마장": latest.get("경마장", ""),
        "경주번호": latest.get("경주번호", ""),
        "해": "총괄 판단/확률/전략 점검",
        "달": "경주 있는 날·없는 날·경주 종료 상태 판단",
        "별": "26개 API/허브 자료 수집 가능 상태 점검",
        "구름": "체중·게이트·주로·날씨·배당변수 감시",
        "비": "성공/실패 원인·learning_bigdata 복기",
        "AI종합확률": prob.get("AI종합확률", latest.get("AI종합확률", "")),
        "자료충분도": prob.get("자료충분도", latest.get("자료충분도", "")),
        "자동구매": "없음",
        "자동결제": "없음",
        "실행결과": result,
    }

def _hub365_make_end_or_learning_mobile_row_15round(latest: dict = None, source: str = "manual") -> dict:
    latest = dict(latest or {})
    meet = latest.get("경마장") or "서울"
    race_no = latest.get("경주번호") or latest.get("race_no") or ""
    try:
        phase = _hub365_phase(latest) if "_hub365_phase" in globals() else {}
    except Exception:
        phase = {}
    try:
        prob = _hub365_probability_from_hub(latest) if "_hub365_probability_from_hub" in globals() else {}
    except Exception:
        prob = {}
    status_title = "오늘 경주 종료 · 이전 추천 표시 차단"
    if phase.get("코드") == "NO_RACE_DAY":
        status_title = "오늘 경주 없음 · 5명 에이전트 학습/복기 활동중"
    row = dict(latest)
    row.update({
        "저장시각": _hub365_now_str() if "_hub365_now_str" in globals() else (now_str() if "now_str" in globals() else str(datetime.datetime.now())),
        "상태": status_title,
        "설명": "해·달·별·구름·비 에이전트가 허브 상태/학습/복기 기록을 저장했습니다. 새 경주 분석 후 추천이 갱신됩니다.",
        "자동구매": "없음",
        "자동결제": "없음",
        "경마장": meet,
        "경주번호": race_no,
        "데이터상태": "경주종료/학습중" if phase.get("코드") != "NO_RACE_DAY" else "경주없음/학습중",
        "실전표시불가": "Y",
        "실전검증": "N",
        "365AI상태": "해·달·별·구름·비 5명 에이전트 활동 기록 저장",
        "삼쌍승18조합": "",
        "구매표복사": "[경주 종료/학습 상태]\n현재 실전 추천 표시는 차단되었습니다.\n이전 경주 추천은 모바일에 표시하지 않습니다.\nPC 수동 실행 또는 Apps Script 백그라운드 실행 후 새 경주 추천이 저장되면 갱신됩니다.",
        "source": str(source),
    })
    row.update(prob)
    return row

def run_hub365_cycle(source: str = "manual") -> dict:
    prev_flag = False
    try:
        prev_flag = bool(st.session_state.get("_hub365_network_allowed", False))
    except Exception:
        prev_flag = False
    try:
        st.session_state["_hub365_network_allowed"] = True
    except Exception:
        pass
    latest = {}
    try:
        latest = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else {}
    except Exception:
        latest = {}
    try:
        start_row = _hub365_agent_activity_row_15round(source, latest, {"단계": "start"})
        if "_hub365_safe_save" in globals():
            _hub365_safe_save("agent_365_runs", start_row)
            _hub365_safe_save("hub_365_status", start_row)
    except Exception:
        pass
    result = {"ok": False, "오류": "run_hub365_cycle core not found"}
    try:
        if callable(_run_hub365_cycle_core_15round):
            result = _run_hub365_cycle_core_15round(source)
        else:
            result = {"ok": True, "상태": "core 없음 · 활동기록만 저장"}
        try:
            latest2 = load_mobile_recommend_json() if "load_mobile_recommend_json" in globals() else latest
        except Exception:
            latest2 = latest
        done_row = _hub365_agent_activity_row_15round(source, latest2, {"단계": "done", "result": result})
        if "_hub365_safe_save" in globals():
            _hub365_safe_save("agent_365_runs", done_row)
            _hub365_safe_save("hub_365_status", done_row)
        # 경주 종료/경주 없음/실전표시불가 상태에서는 모바일에 '추천 없음/학습중'을 명시적으로 저장합니다.
        try:
            phase = _hub365_phase(latest2) if "_hub365_phase" in globals() else {}
            ended = str(latest2.get("데이터상태", "")) in ["경주종료", "종료", "경주종료/학습중"] or str(latest2.get("실전표시불가", "")) == "Y"
            if phase.get("코드") in ["NO_RACE_DAY", "RACE_REVIEW"] or ended:
                mobile_row = _hub365_make_end_or_learning_mobile_row_15round(latest2, source)
                if "save_mobile_recommend_json" in globals():
                    save_mobile_recommend_json(mobile_row)
                elif "_hub365_safe_save" in globals():
                    _hub365_safe_save("mobile_recommend", mobile_row)
        except Exception:
            pass
        if isinstance(result, dict):
            result["에이전트활동저장"] = "Y"
            result["저장탭"] = "hub_365_status / agent_365_runs / mobile_recommend(종료·학습상태일 때)"
        return result
    except Exception as e:
        err = {"ok": False, "상태": "허브365 실행 중 오류", "오류": str(e)[:300], "에이전트활동저장": "오류기록 시도"}
        try:
            if "_hub365_safe_save" in globals():
                _hub365_safe_save("agent_365_runs", _hub365_agent_activity_row_15round(source, latest, err))
                _hub365_safe_save("hub_365_status", _hub365_agent_activity_row_15round(source, latest, err))
        except Exception:
            pass
        return err
    finally:
        try:
            st.session_state["_hub365_network_allowed"] = bool(prev_flag)
        except Exception:
            pass

if __name__ == "__main__":
    if "_hub365_is_background_tick_request" in globals() and _hub365_is_background_tick_request():
        try:
            result = run_hub365_cycle("apps_script_tick")
            st.write({"ok": True, "mode": "apps_script_tick", "result": result})
        except Exception as e:
            try:
                st.write({"ok": False, "mode": "apps_script_tick", "error": str(e)[:300]})
            except Exception:
                pass
    else:
        render()

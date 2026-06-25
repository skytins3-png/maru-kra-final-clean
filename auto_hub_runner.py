"""
MARU KRA auto_hub_runner.py

주의:
- 자동구매/자동결제/자동배포 없음.
- 월화수목 허브 운영 보조용 파일.
- Streamlit Cloud에서는 주기 실행을 보장하지 않으므로, 실제 운영은 app.py 내부의 주간 에이전트 틱과 Google Sheet 허브를 기준으로 합니다.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

DATA_DIR = Path("maru_kra_data")
DATA_DIR.mkdir(exist_ok=True)


def now_kst() -> datetime.datetime:
    return datetime.datetime.utcnow() + datetime.timedelta(hours=9)


def write_runner_heartbeat() -> None:
    payload = {
        "saved_at_kst": now_kst().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "hub_runner_heartbeat",
        "message": "월화수목 허브 운영 보조. 실제 분석/저장은 app.py와 Google Sheet 허브가 담당합니다.",
        "auto_purchase": False,
        "auto_payment": False,
        "auto_deploy": False,
    }
    (DATA_DIR / "auto_hub_runner_status.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    write_runner_heartbeat()
    print("MARU KRA auto_hub_runner heartbeat saved.")


import streamlit as st
import zipfile, json, shutil, io, re, ast, subprocess, sys, base64, time
from pathlib import Path
from datetime import datetime
import requests

ROOT = Path(__file__).parent
MEM = ROOT / "ai_memory.json"
STORE = ROOT / "project_storage"
VERS = ROOT / "version_outputs"
GENERATED = ROOT / "generated_projects"
IMAGE_STORE = ROOT / "image_uploads"
STORE.mkdir(exist_ok=True)
VERS.mkdir(exist_ok=True)
GENERATED.mkdir(exist_ok=True)
IMAGE_STORE.mkdir(exist_ok=True)

DEFAULT = {
    "version": "13.0-all-in-one-final",
    "projects": {},
    "patch_records": [],
    "github_deploys": [],
    "test_records": [],
    "file_checks": [],
    "generated_projects": [],
    "hub_uploads": [],
    "log_analyses": [],
    "image_analyses": [],
    "command_records": [],
    "google_sheets": {"enabled": False, "sheet_id": "", "service_account_json": ""},
    "lessons": [],
}

PATCHES = {
    "mobile_ui": "모바일 큰 글씨/큰 버튼",
    "error_logger": "오류 로그 저장",
    "api_timeout": "API timeout/통신두절 방어",
    "debug_panel": "디버그 패널",
    "api_key_guard": "API KEY 보안 안내",
    "zip_export": "현재 앱 ZIP 다운로드",
    "kra_helper": "경마 API 점검 도구 파일 추가",
    "toto_helper": "토토/스포츠 API 점검 도구 파일 추가",
    "html_render_fix": "HTML 카드 코드노출 수정",
    "race_schedule_fallback": "경마시간 추천없음 표시 보정",
}

FEATURES = [
    "음성지시 제거", "OpenAI API 키 제거", "요금 발생 요소 제거",
    "ZIP 업로드 자동 압축해제", "프로젝트 보관함", "파일 목록 검사",
    "오류 파일 검사", "문법 검사", "기존 기능 분석", "자동테스트",
    "반복 자동테스트", "개선안 추천", "승인/미승인/추가지시",
    "승인한 항목 실제 패치", "app.py 실제 수정", "helper 파일 실제 추가",
    "새 버전 ZIP 생성", "GitHub 대상 저장소 자동 업로드/커밋",
    "Streamlit Cloud 자동 재배포 유도", "구글시트 저장 구조", 
    "GitHub Actions 예약 테스트 파일 생성", "진화형 AI 코드 생성", "생성 앱 GitHub 허브 자동 업로드", "구글시트 허브 저장", "로그파일 붙여넣기/업로드 분석", "사진 첨부/명령 입력 분석", "HTML 카드 코드노출 수정", "경마시간 추천없음 표시 보정", "자동구매/자동결제 차단"
]

def load():
    if MEM.exists():
        try:
            m = json.loads(MEM.read_text(encoding="utf-8"))
            for k, v in DEFAULT.items():
                m.setdefault(k, v)
            return m
        except Exception:
            pass
    save(DEFAULT.copy())
    return DEFAULT.copy()

def save(m):
    m["updated_at"] = datetime.now().isoformat(timespec="seconds")
    MEM.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

def sname(x):
    return re.sub(r"[^a-zA-Z0-9가-힣_.-]+", "_", str(x))[:80] or "project"


def infer_project_name(name, app_url="", uploaded=None):
    raw = (name or "").strip()
    if raw:
        return raw
    if app_url:
        m = re.search(r"https?://([^./]+)", app_url)
        if m:
            return m.group(1).strip()
    if uploaded is not None:
        base = Path(uploaded.name).stem
        base = re.sub(r"\s*\(\d+\)$", "", base)
        base = base.replace("_UPLOAD", "").replace("_upload", "")
        if base:
            return sname(base)
    return "maru-kra-final-clean"


def read(p):
    for enc in ("utf-8", "cp949", "euc-kr"):
        try:
            return Path(p).read_text(encoding=enc)
        except Exception:
            pass
    return ""

def write(p, txt):
    Path(p).write_text(txt, encoding="utf-8")

def unzip_upload(up, name):
    pdir = STORE / sname(name)
    if pdir.exists():
        shutil.rmtree(pdir)
    pdir.mkdir(parents=True)
    raw = pdir / up.name
    raw.write_bytes(up.getvalue())
    src = pdir / "src"
    src.mkdir()
    if up.name.lower().endswith(".zip"):
        with zipfile.ZipFile(raw) as z:
            z.extractall(src)
    else:
        shutil.copy2(raw, src / up.name)
    kids = list(src.iterdir())
    if len(kids) == 1 and kids[0].is_dir():
        inner = kids[0]
        if (inner/"app.py").exists() or list(inner.glob("*.py")):
            tmp = pdir/"src_inner"
            shutil.move(str(inner), str(tmp))
            shutil.rmtree(src)
            tmp.rename(src)
    return src

def find_app(src):
    src = Path(src)
    for n in ["app.py", "streamlit_app.py", "main.py"]:
        p = src / n
        if p.exists():
            return p
    py = list(src.rglob("*.py"))
    return py[0] if py else None

def scan(src):
    src = Path(src)
    files, errors, suspicious = [], [], []
    for p in src.rglob("*"):
        if "__pycache__" in p.parts or ".git" in p.parts or not p.is_file():
            continue
        rel = str(p.relative_to(src))
        files.append({"path": rel, "size": p.stat().st_size})
        low = p.name.lower()
        if any(x in low for x in ["error", "log", "traceback", "debug"]):
            errors.append(rel)
        if p.suffix.lower() in [".env", ".pem", ".key"] or p.name == "secrets.toml":
            suspicious.append(rel)
    return {
        "file_count": len(files),
        "has_app_py": any(f["path"].endswith("app.py") for f in files),
        "has_requirements": any(f["path"].endswith("requirements.txt") for f in files),
        "error_files": errors,
        "suspicious_files": suspicious,
        "files": files[:500]
    }

def syntax_all(src):
    rows = []
    for p in Path(src).rglob("*.py"):
        if "__pycache__" in p.parts or ".git" in p.parts:
            continue
        r = subprocess.run([sys.executable, "-m", "py_compile", str(p)], capture_output=True, text=True)
        rows.append({"file": str(p.relative_to(src)), "ok": r.returncode == 0, "message": "OK" if r.returncode == 0 else r.stderr[-2000:]})
    return rows

def analyze_app(app_path):
    txt = read(app_path) if app_path and Path(app_path).exists() else ""
    if not txt:
        return {"features": ["app.py 없음"], "risks": ["app.py를 찾지 못함"]}
    features = []
    if "streamlit" in txt or "st." in txt: features.append("Streamlit UI")
    if "requests" in txt or ".get(" in txt: features.append("API 호출")
    if "timeout=" in txt: features.append("timeout 설정")
    if "try:" in txt and "except" in txt: features.append("오류 처리")
    if "download_button" in txt or "zipfile" in txt: features.append("다운로드/ZIP")
    if "file_uploader" in txt: features.append("파일 업로드")
    if "경마" in txt or "KRA" in txt or "horse" in txt: features.append("경마 관련")
    if "토토" in txt or "sports" in txt or "odds" in txt: features.append("토토/스포츠 관련")
    risks = []
    if re.search(r"(api[_-]?key|serviceKey|token)\s*=\s*['\"][A-Za-z0-9_\-]{16,}", txt, re.I):
        risks.append("API 키가 코드에 직접 들어갔을 가능성")
    if ".get(" in txt and "timeout=" not in txt:
        risks.append("API timeout 부족 가능성")
    if "자동구매" in txt or "자동결제" in txt:
        risks.append("자동구매/자동결제 문구 있음 - 차단 권장")
    if "openai" in txt.lower() or "audio_input" in txt.lower():
        risks.append("음성/OpenAI 코드가 남아 있음 - 제거 권장")
    try:
        ast.parse(txt)
    except Exception as e:
        risks.append("문법 오류: " + str(e))
    return {"features": features or ["기능 추출 부족"], "risks": risks or ["큰 위험 없음"], "lines": len(txt.splitlines())}

def parse_log(txt):
    t = (txt or "").lower()
    rec, patches = [], set()
    rules = [
        ("agent-card", ["html_render_fix", "mobile_ui"], "HTML 카드 코드 노출"),
        ("<div", ["html_render_fix", "mobile_ui"], "HTML 코드가 화면에 보임"),
        ("추천 없음", ["race_schedule_fallback", "debug_panel", "kra_helper"], "경마시간 추천없음 표시 보정"),
        ("todayrace", ["race_schedule_fallback", "debug_panel", "kra_helper"], "공식 경주 일정과 앱 표시 불일치"),
        ("제주", ["race_schedule_fallback", "debug_panel", "kra_helper"], "경마장 자동 감지 보정"),
        ("nameerror", ["error_logger", "debug_panel"], "정의되지 않은 변수"),
        ("keyerror", ["error_logger", "debug_panel"], "키 누락"),
        ("http 500", ["api_timeout", "debug_panel"], "서버/API 오류"),
        ("http 403", ["api_key_guard", "debug_panel"], "권한 문제"),
        ("http 401", ["api_key_guard", "debug_panel"], "키 인증 문제"),
        ("http 404", ["api_timeout", "debug_panel"], "URL 오류"),
        ("timeout", ["api_timeout", "debug_panel"], "타임아웃"),
        ("connectionerror", ["api_timeout", "debug_panel"], "통신두절"),
        ("modulenotfounderror", ["debug_panel"], "requirements 누락"),
        ("data[]", ["debug_panel"], "데이터 0건"),
        ("no result", ["debug_panel"], "데이터 없음"),
        ("통신두절", ["api_timeout", "debug_panel"], "통신두절"),
        ("오류", ["error_logger", "debug_panel"], "오류 기록 필요"),
    ]
    for key, ps, reason in rules:
        if key in t:
            rec.append({"keyword": key, "reason": reason, "patches": ps})
            patches.update(ps)
    return {"findings": rec or [{"keyword":"없음","reason":"명확한 오류 패턴 없음","patches":[]}], "recommended_patches": sorted(patches)}

def inspect_error_files(src):
    rows = []
    for p in Path(src).rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and any(x in p.name.lower() for x in ["error", "log", "traceback", "debug"]):
            txt = read(p)
            rows.append({"file": str(p.relative_to(src)), "preview": txt[:1200], "analysis": parse_log(txt)})
    return rows



def save_uploaded_images(project_name, uploads):
    saved = []
    folder = IMAGE_STORE / sname(project_name)
    folder.mkdir(parents=True, exist_ok=True)
    for up in uploads or []:
        suffix = Path(up.name).suffix.lower() or ".png"
        fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{sname(Path(up.name).stem)}{suffix}"
        p = folder / fname
        data = up.getvalue()
        p.write_bytes(data)
        saved.append({
            "name": up.name,
            "saved_path": str(p),
            "size": len(data),
            "suffix": suffix,
        })
    return saved

def analyze_image_command(command_text, saved_images):
    cmd = (command_text or "").lower()
    patches = set()
    findings = []
    if any(k in cmd for k in ["모바일", "폰", "화면", "작", "안보", "글씨", "버튼"]):
        patches.update(["mobile_ui", "debug_panel"])
        findings.append({"reason": "모바일 화면/버튼/글씨 개선 명령", "patches": ["mobile_ui", "debug_panel"]})
    if any(k in cmd for k in ["오류", "에러", "traceback", "빨간", "멈춤", "안됨", "안되"]):
        patches.update(["error_logger", "debug_panel"])
        findings.append({"reason": "화면 오류/정지/에러 명령", "patches": ["error_logger", "debug_panel"]})
    if any(k in cmd for k in ["html", "div", "agent-card", "카드", "코드", "그대로"]):
        patches.update(["html_render_fix", "mobile_ui"])
        findings.append({"reason": "HTML 카드 코드 노출 명령", "patches": ["html_render_fix", "mobile_ui"]})
    if any(k in cmd for k in ["경마시간", "추천 없음", "추천없음", "제주", "서울", "부산", "경주", "todayrace"]):
        patches.update(["race_schedule_fallback", "debug_panel", "kra_helper"])
        findings.append({"reason": "경마시간/추천없음/경주표시 명령", "patches": ["race_schedule_fallback", "debug_panel", "kra_helper"]})
    if any(k in cmd for k in ["api", "통신", "500", "403", "404", "401", "timeout", "데이터", "실시간"]):
        patches.update(["api_timeout", "debug_panel", "api_key_guard"])
        findings.append({"reason": "API/통신/실시간 관련 명령", "patches": ["api_timeout", "debug_panel", "api_key_guard"]})
    if any(k in cmd for k in ["다운로드", "zip", "압축", "파일"]):
        patches.update(["zip_export", "debug_panel"])
        findings.append({"reason": "파일/ZIP/다운로드 관련 명령", "patches": ["zip_export", "debug_panel"]})
    if any(k in cmd for k in ["경마", "kra", "마사회"]):
        patches.update(["kra_helper", "debug_panel"])
        findings.append({"reason": "경마/KRA 관련 명령", "patches": ["kra_helper", "debug_panel"]})
    if any(k in cmd for k in ["토토", "스포츠", "축구", "배당", "odds"]):
        patches.update(["toto_helper", "debug_panel"])
        findings.append({"reason": "토토/스포츠 관련 명령", "patches": ["toto_helper", "debug_panel"]})
    if not findings:
        patches.update(["debug_panel", "error_logger"])
        findings.append({"reason": "일반 사진/명령 분석: 디버그와 오류기록 우선 추천", "patches": ["debug_panel", "error_logger"]})
    return {
        "image_count": len(saved_images or []),
        "images": saved_images,
        "command": command_text,
        "findings": findings,
        "recommended_patches": sorted(patches),
    }


def decode_uploaded_log(uploaded_file):
    if uploaded_file is None:
        return ""
    raw = uploaded_file.getvalue()
    for enc in ("utf-8", "cp949", "euc-kr"):
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode("utf-8", errors="ignore")


def test_url(label, url, key=""):
    today = datetime.now().strftime("%Y%m%d")
    dash = datetime.now().strftime("%Y-%m-%d")
    final = url.replace("{api_key}", key or "").replace("{serviceKey}", key or "").replace("{token}", key or "").replace("{today}", today).replace("{today_dash}", dash)
    out = {"label": label, "ok": False, "status_code": None, "error": "", "data_count": None, "preview": ""}
    try:
        r = requests.get(final, timeout=15)
        out["ok"] = r.ok; out["status_code"] = r.status_code
        try:
            data = r.json()
            if isinstance(data, dict) and isinstance(data.get("data"), list):
                out["data_count"] = len(data["data"])
            out["preview"] = json.dumps(data, ensure_ascii=False)[:1200]
        except Exception:
            out["preview"] = r.text[:1200]
    except Exception as e:
        out["error"] = str(e)
    return out

def analyze_tests(rows):
    patches, findings = set(), []
    for r in rows:
        stc = r.get("status_code")
        if r.get("error"):
            patches.update(["api_timeout", "debug_panel", "error_logger"])
            findings.append({"target": r["label"], "problem": "통신두절", "patches": ["api_timeout", "debug_panel"]})
        elif stc in [401,403]:
            patches.update(["api_key_guard", "debug_panel"])
            findings.append({"target": r["label"], "problem": f"HTTP {stc}", "patches": ["api_key_guard", "debug_panel"]})
        elif stc == 404 or (stc and stc >= 500):
            patches.update(["api_timeout", "debug_panel"])
            findings.append({"target": r["label"], "problem": f"HTTP {stc}", "patches": ["api_timeout", "debug_panel"]})
        elif r.get("ok") and r.get("data_count") == 0:
            patches.add("debug_panel")
            findings.append({"target": r["label"], "problem": "데이터 0건", "patches": ["debug_panel"]})
    return {"findings": findings or [{"problem": "큰 문제 없음"}], "recommended_patches": sorted(patches)}

def ensure_req(src):
    p = Path(src)/"requirements.txt"
    cur = [x.strip() for x in read(p).splitlines() if x.strip()] if p.exists() else []
    for pkg in ["streamlit", "pandas", "numpy", "requests"]:
        if pkg.lower() not in {x.lower() for x in cur}:
            cur.append(pkg)
    write(p, "\n".join(cur)+"\n")

def apply_patch(app_path, approved):
    app_path = Path(app_path)
    txt = read(app_path)
    write(app_path.with_suffix(".before_upgrade.py"), txt)
    top, bottom = [], []
    if "html_render_fix" in approved:
        for a,b in [("st.code(agent_html)", "st.markdown(agent_html, unsafe_allow_html=True)"), ("st.text(agent_html)", "st.markdown(agent_html, unsafe_allow_html=True)"), ("st.write(agent_html)", "st.markdown(agent_html, unsafe_allow_html=True)"), ("st.code(card_html)", "st.markdown(card_html, unsafe_allow_html=True)"), ("st.text(card_html)", "st.markdown(card_html, unsafe_allow_html=True)"), ("st.write(card_html)", "st.markdown(card_html, unsafe_allow_html=True)"), ("st.code(html)", "st.markdown(html, unsafe_allow_html=True)"), ("st.text(html)", "st.markdown(html, unsafe_allow_html=True)")]:
            txt = txt.replace(a,b)
    if "mobile_ui" in approved and "MARU_MOBILE_UI" not in txt:
        if "st.set_page_config" not in txt:
            top.append("st.set_page_config(page_title='업그레이드 앱', layout='wide')\n")
        top.append("st.markdown('<style>/* MARU_MOBILE_UI */ .block-container{padding-top:1rem;max-width:1200px}.stButton>button{height:3rem;font-weight:800} textarea,input{font-size:1.02rem!important}</style>', unsafe_allow_html=True)\n")
    if any(x in approved for x in ["error_logger","debug_panel","api_timeout","zip_export"]) and "MARU_COMMON_IMPORTS" not in txt:
        top.append("from pathlib import Path as _maru_Path\nfrom datetime import datetime as _maru_datetime\nimport json as _maru_json\n")
    if "error_logger" in approved and "MARU_ERROR_LOGGER" not in txt:
        top.append("""
# MARU_ERROR_LOGGER
_MARU_ERROR_LOG = _maru_Path(__file__).parent / 'error_log.json'
def maru_log_error(where, err):
    rec={'time':_maru_datetime.now().isoformat(timespec='seconds'),'where':str(where),'error':str(err)}
    try:
        old=_maru_json.loads(_MARU_ERROR_LOG.read_text(encoding='utf-8')) if _MARU_ERROR_LOG.exists() else []
        old.append(rec); _MARU_ERROR_LOG.write_text(_maru_json.dumps(old[-500:],ensure_ascii=False,indent=2),encoding='utf-8')
    except Exception: pass
    return rec
""")
    if "api_timeout" in approved and "MARU_SAFE_GET" not in txt:
        top.append("""
# MARU_SAFE_GET
def maru_safe_get(url, params=None, headers=None, timeout=15):
    import requests as _r
    try:
        res=_r.get(url, params=params, headers=headers, timeout=timeout)
        info={'ok':res.ok,'status_code':res.status_code,'url':str(res.url)[:300]}
        try: return info, res.json()
        except Exception: return info, {'text_preview':res.text[:3000]}
    except Exception as e:
        if 'maru_log_error' in globals(): maru_log_error('maru_safe_get', e)
        return {'ok':False,'status_code':'CONNECTION_ERROR','error':str(e)}, None
""")
    if "api_key_guard" in approved and "MARU_API_KEY_GUARD" not in txt:
        bottom.append("with st.expander('🔐 API KEY 보안 안내'):\n    st.warning('API KEY는 app.py에 직접 넣지 마세요. Streamlit Secrets 또는 입력창을 사용하세요.')\n")
    if "debug_panel" in approved and "MARU_DEBUG_PANEL" not in txt:
        bottom.append("""
with st.expander('🧯 MARU 디버그 패널'):
    try:
        _log=_maru_Path(__file__).parent/'error_log.json'
        st.json(_maru_json.loads(_log.read_text(encoding='utf-8'))[-30:] if _log.exists() else [])
    except Exception as e: st.warning(e)
""")
    if "zip_export" in approved and "MARU_ZIP_EXPORT" not in txt:
        bottom.append("""
with st.expander('📦 현재 앱 ZIP 다운로드'):
    try:
        import zipfile as _z, io as _io
        root=_maru_Path(__file__).parent; buf=_io.BytesIO()
        with _z.ZipFile(buf,'w',_z.ZIP_DEFLATED) as zz:
            for p in root.rglob('*'):
                if '__pycache__' not in p.parts and '.git' not in p.parts and p.is_file(): zz.write(p,p.relative_to(root))
        st.download_button('현재 앱 ZIP 다운로드', buf.getvalue(), 'current_app_export.zip', 'application/zip', use_container_width=True)
    except Exception as e: st.warning(e)
""")
    if "race_schedule_fallback" in approved and "MARU_RACE_FALLBACK_NOTE" not in txt:
        bottom.append("with st.expander('🐎 경마 추천 없음 보정 안내'):\n    st.info('추천 파일이 비어 있어도 공식 경주 일정이 있으면 경주 있음 / 추천 생성 대기 / 수집 필요로 표시되도록 보정 파일을 추가했습니다.')\n")
    if top:
        txt = txt.replace("import streamlit as st", "import streamlit as st\n" + "\n".join(top), 1) if "import streamlit as st" in txt else "import streamlit as st\n" + "\n".join(top) + "\n" + txt
    if bottom:
        txt += "\n\n# ===== MARU V13 PATCH ADDONS =====\n" + "\n".join(bottom)
    write(app_path, txt)

def add_helpers(src, approved):
    src = Path(src)
    if "kra_helper" in approved:
        write(src/"kra_api_debug_helper.py", "import streamlit as st, requests\nst.title('🐎 경마 API 점검')\nurl=st.text_area('URL')\nkey=st.text_input('KEY',type='password')\nif st.button('점검'):\n    try:\n        r=requests.get(url.replace('{serviceKey}',key).replace('{api_key}',key),timeout=15); st.metric('HTTP',r.status_code); st.text(r.text[:5000])\n    except Exception as e: st.error(e)\n")
    if "toto_helper" in approved:
        write(src/"toto_api_debug_helper.py", "import streamlit as st, requests\nst.title('⚽ 토토/스포츠 API 점검')\nurl=st.text_area('URL')\ntoken=st.text_input('TOKEN',type='password')\nif st.button('점검'):\n    try:\n        r=requests.get(url.replace('{token}',token).replace('{api_key}',token),timeout=15); st.metric('HTTP',r.status_code); st.text(r.text[:5000])\n    except Exception as e: st.error(e)\n")
    if "race_schedule_fallback" in approved:
        write(src/"maru_race_schedule_fallback.py", "from datetime import datetime\n\ndef maru_race_status_fallback(recommend_data=None, race_hint=None):\n    if recommend_data:\n        return {'status':'추천 있음','message':'저장된 추천 표시','data':recommend_data}\n    if race_hint:\n        return {'status':'경주 있음 / 추천 생성 대기','message':f'{race_hint} 경주 일정 감지. 수집/분석 후 추천 표시','data':None}\n    return {'status':'추천 대기','message':'경주 일정 수집 또는 추천 생성 필요','data':None}\n")



def get_gsheet_config(mem):
    return mem.setdefault("google_sheets", {"enabled": False, "sheet_id": "", "service_account_json": ""})

def gsheet_append(mem, tab_name, row):
    cfg = get_gsheet_config(mem)
    if not cfg.get("enabled"):
        return False, "구글시트 꺼짐"
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        info = json.loads(cfg.get("service_account_json", ""))
        creds = Credentials.from_service_account_info(
            info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        ss = gspread.authorize(creds).open_by_key(cfg.get("sheet_id", ""))
        try:
            ws = ss.worksheet(tab_name)
        except Exception:
            ws = ss.add_worksheet(title=tab_name, rows=1000, cols=10)
            ws.append_row(["time", "type", "project", "version", "status", "summary", "data_json"])
        ws.append_row(
            [
                row.get("time", datetime.now().isoformat(timespec="seconds")),
                row.get("type", tab_name),
                row.get("project", ""),
                str(row.get("version", "")),
                row.get("status", ""),
                row.get("summary", ""),
                json.dumps(row, ensure_ascii=False)[:45000],
            ],
            value_input_option="USER_ENTERED",
        )
        return True, "구글시트 저장 완료"
    except Exception as e:
        return False, str(e)

def save_event(mem, tab, row):
    ok, msg = gsheet_append(mem, tab, row)
    mem.setdefault("lessons", []).append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "lesson": f"{tab}: {msg}",
    })
    return ok, msg


def generate_streamlit_project(project_name, goal, app_kind="기본앱"):
    """외부 유료 AI API 없이 템플릿 기반 Streamlit 앱을 생성합니다."""
    pname = sname(project_name or "generated-app")
    out = GENERATED / pname
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    safe_goal = (goal or "사용자 목표 앱").strip()
    title = project_name or "MARU Generated App"

    app_code = f"""import streamlit as st
import pandas as pd
import numpy as np
import requests
from pathlib import Path
from datetime import datetime
import json

st.set_page_config(page_title={title!r}, page_icon="🧠", layout="wide")

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
MEMORY_FILE = DATA_DIR / "memory.json"

def load_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {{"records": [], "created_at": datetime.now().isoformat(timespec="seconds")}}

def save_memory(m):
    m["updated_at"] = datetime.now().isoformat(timespec="seconds")
    MEMORY_FILE.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

def safe_get(url, timeout=15):
    try:
        r = requests.get(url, timeout=timeout)
        info = {{"ok": r.ok, "status_code": r.status_code, "url": str(r.url)[:300]}}
        try:
            return info, r.json()
        except Exception:
            return info, {{"text_preview": r.text[:3000]}}
    except Exception as e:
        return {{"ok": False, "error": str(e)}}, None

st.title("🧠 " + {title!r})
st.caption("MARU 자동 생성 앱 / 기존 기능 삭제 금지 / 수동 확인 중심")
st.info({safe_goal!r})

tab1, tab2, tab3, tab4 = st.tabs(["🏠 대시보드", "🔌 API 점검", "📝 기록", "📦 내보내기"])

with tab1:
    st.subheader("핵심 목표")
    st.write({safe_goal!r})
    st.metric("앱 종류", {app_kind!r})
    st.metric("생성 시각", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

with tab2:
    st.subheader("API 통신 점검")
    url = st.text_area("API URL", height=120)
    token = st.text_input("API KEY/TOKEN 선택", type="password")
    if st.button("통신 점검", type="primary", use_container_width=True):
        final_url = url.replace("{{api_key}}", token).replace("{{serviceKey}}", token).replace("{{token}}", token)
        info, data = safe_get(final_url)
        st.json(info)
        if data is not None:
            st.json(data)

with tab3:
    st.subheader("기록")
    mem = load_memory()
    memo = st.text_area("메모/테스트 결과")
    if st.button("기록 저장", use_container_width=True):
        mem.setdefault("records", []).append({{"time": datetime.now().isoformat(timespec="seconds"), "memo": memo}})
        save_memory(mem)
        st.success("저장 완료")
    st.json(mem)

with tab4:
    st.subheader("내보내기")
    st.write("GitHub/Streamlit 배포용 기본 파일이 포함된 앱입니다.")
"""
    req = "streamlit\npandas\nnumpy\nrequests\n"
    readme = f"""# {title}

MARU 진화형 AI 코드 생성기가 만든 Streamlit 앱입니다.

## 목표

{safe_goal}

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud:

```text
Main file path: app.py
```
"""
    memdata = {"project": title, "goal": safe_goal, "created_at": datetime.now().isoformat(timespec="seconds"), "records": []}
    (out / "app.py").write_text(app_code, encoding="utf-8")
    (out / "requirements.txt").write_text(req, encoding="utf-8")
    (out / "README.md").write_text(readme, encoding="utf-8")
    (out / "data").mkdir(exist_ok=True)
    (out / "data" / "memory.json").write_text(json.dumps(memdata, ensure_ascii=False, indent=2), encoding="utf-8")
    return out

def register_generated_project(mem, project_name, src, app_url="", github_repo=""):
    pname = sname(project_name)
    app_path = find_app(src)
    info = {
        "name": pname,
        "src": str(src),
        "app_file": str(app_path) if app_path else "",
        "app_url": app_url,
        "api_key": "",
        "api_urls": [],
        "version": 0,
        "github": {"owner": "skytins3-png", "repo": github_repo or pname, "branch": "main", "prefix": ""},
        "scan": scan(src),
        "syntax": syntax_all(src),
        "errors": inspect_error_files(src),
        "analysis": analyze_app(app_path)
    }
    mem.setdefault("projects", {})[pname] = info
    mem.setdefault("generated_projects", []).append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "project": pname,
        "src": str(src),
        "scan": info["scan"],
        "analysis": info["analysis"]
    })
    save(mem)
    return info


def make_zip(src, name, ver):
    out = VERS / f"{sname(name)}_v{ver:03d}_PATCHED.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in Path(src).rglob("*"):
            if "__pycache__" not in p.parts and ".git" not in p.parts and p.is_file():
                z.write(p, p.relative_to(src))
    return out


def zip_bytes(src):
    buf = io.BytesIO()
    src = Path(src)
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src.rglob("*"):
            if "__pycache__" in p.parts or ".git" in p.parts or not p.is_file():
                continue
            z.write(p, p.relative_to(src))
    return buf.getvalue()

def gh_headers(token):
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}

def gh_repo(owner, repo, token):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=gh_headers(token), timeout=20)
    try: data = r.json()
    except Exception: data = {"text": r.text[:1000]}
    return r.status_code, data

def gh_sha(owner, repo, branch, path, token):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=gh_headers(token), params={"ref": branch}, timeout=20)
    return r.json().get("sha") if r.status_code == 200 else None

def gh_put(owner, repo, branch, path, b, msg, token):
    payload = {"message": msg, "content": base64.b64encode(b).decode(), "branch": branch}
    sha = gh_sha(owner, repo, branch, path, token)
    if sha: payload["sha"] = sha
    r = requests.put(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=gh_headers(token), json=payload, timeout=30)
    try: data = r.json()
    except Exception: data = {"text": r.text[:1000]}
    return r.status_code in [200,201], r.status_code, data

def gh_upload_folder(src, owner, repo, branch, token, msg, prefix=""):
    rows = []
    for p in Path(src).rglob("*"):
        if "__pycache__" in p.parts or ".git" in p.parts or not p.is_file(): continue
        if ".github" in p.parts and "workflows" in p.parts:
            rows.append({"file": str(p.relative_to(src)).replace("\\","/"), "ok": True, "status": "SKIPPED", "message": "GitHub workflows 폴더는 보안권한 문제 방지를 위해 자동 제외"})
            continue
        if p.name in [".env", "secrets.toml"] or p.suffix.lower() in [".pem", ".key"]: continue
        rel = str(p.relative_to(src)).replace("\\","/")
        target = f"{prefix.strip('/')}/{rel}" if prefix.strip("/") else rel
        ok, status, data = gh_put(owner, repo, branch, target, p.read_bytes(), msg, token)
        rows.append({"file": target, "ok": ok, "status": status, "message": data.get("message","") if isinstance(data, dict) else ""})
        time.sleep(0.05)
    return rows

def workflow(app_url, api_urls):
    return f"""name: MARU Auto Test
on:
  workflow_dispatch:
  schedule:
    - cron: '*/30 * * * *'
jobs:
  auto-test:
    runs-on: ubuntu-latest
    steps:
      - run: |
          python - <<'PY'
          import requests, json
          targets=[]
          app={app_url!r}
          if app: targets.append(("APP_URL", app))
          for i,u in enumerate({api_urls!r},1): targets.append((f"API_{{i}}", u))
          rows=[]
          for label,url in targets:
              try:
                  r=requests.get(url, timeout=15); rows.append({{"label":label,"ok":r.ok,"status":r.status_code,"preview":r.text[:500]}})
              except Exception as e:
                  rows.append({{"label":label,"ok":False,"error":str(e)}})
          print(json.dumps(rows,ensure_ascii=False,indent=2))
          if any(not x.get("ok") for x in rows): raise SystemExit(1)
          PY
"""

m = load()
st.set_page_config(page_title="MARU V13 통합 자동화 AI", page_icon="🧠", layout="wide")
st.markdown("<style>.block-container{max-width:1280px;padding-top:1rem}.stButton>button{height:3rem;font-weight:800}</style>", unsafe_allow_html=True)
st.title("🧠 MARU V13 통합 자동화 AI")
st.caption("코드생성 + 패치 + GitHub 허브 자동 업로드 → Streamlit Cloud 자동 재배포")
st.info("핵심: 이제 ZIP 다운로드 후 사람이 다시 올리는 단계 없이, 승인 후 대상 GitHub 저장소까지 자동 반영합니다.")

tabs = st.tabs(["📋 기능", "🤖 코드생성", "📁 등록", "📡 테스트", "🧯 로그분석", "🖼️ 사진분석/명령", "✅ 패치", "🔍 검사", "📦 버전", "🚀 GitHub 자동반영", "☁️ 구글시트", "📚 기록"])

with tabs[0]:
    st.write(FEATURES)
    st.warning("GitHub 자동반영은 GitHub 토큰이 필요합니다. 토큰은 공개 저장소에 절대 올리지 마세요.")

with tabs[1]:
    st.subheader("진화형 AI 코드 생성기 + 자동 허브 업로드")
    st.caption("목표를 입력하면 Streamlit 앱을 생성하고, 검사 후 GitHub 허브 저장소로 자동 업로드할 수 있습니다.")
    gen_name = st.text_input("생성 프로젝트 이름", placeholder="maru-new-app")
    gen_kind = st.selectbox("앱 종류", ["기본앱", "경마 분석앱 뼈대", "토토/스포츠 분석앱 뼈대", "API 대시보드", "기록/허브앱"])
    gen_goal = st.text_area("앱 목표 / 필요한 기능", height=150, placeholder="예: 경마 API를 점검하고 오류 로그를 저장하는 모바일용 대시보드")
    gen_repo = st.text_input("생성 결과를 올릴 GitHub repo 이름", placeholder="maru-new-app")
    if st.button("코드 생성 + 자동검사", type="primary", use_container_width=True):
        pname = infer_project_name(gen_name, "", None)
        src = generate_streamlit_project(pname, gen_goal, gen_kind)
        info = register_generated_project(m, pname, src, github_repo=(gen_repo.strip() or pname))
        st.success(f"생성/검사 완료: {pname}")
        st.json(info["scan"])
        st.json(info["analysis"])
        st.download_button("생성 앱 ZIP 다운로드", zip_bytes(src), f"{sname(pname)}_GENERATED.zip", "application/zip", use_container_width=True)

    st.divider()
    st.subheader("생성 앱 바로 GitHub 허브 업로드")
    ps_gen = list(m.get("projects", {}).keys())
    if not ps_gen:
        st.info("먼저 위에서 코드를 생성하세요.")
    else:
        hub_project = st.selectbox("업로드할 생성/등록 프로젝트", ps_gen, key="hub_codegen_project")
        gh = m["projects"][hub_project].get("github", {})
        c1, c2 = st.columns(2)
        with c1:
            hub_owner = st.text_input("허브 GitHub owner", value=gh.get("owner", "skytins3-png"), key="hub_owner_codegen")
            hub_repo = st.text_input("허브 대상 repo", value=gh.get("repo", hub_project), key="hub_repo_codegen")
            hub_branch = st.text_input("branch", value=gh.get("branch", "main"), key="hub_branch_codegen")
        with c2:
            hub_token = st.text_input("GitHub 토큰", type="password", key="hub_token_codegen")
            hub_msg = st.text_input("커밋 메시지", value=f"MARU generated code hub upload {datetime.now().strftime('%Y-%m-%d %H:%M')}", key="hub_msg_codegen")
            st.warning("토큰은 저장하지 않습니다. 채팅창/README/GitHub 파일에 붙이지 마세요.")
        if st.button("생성 앱 GitHub 허브에 자동 업로드/커밋", type="primary", use_container_width=True):
            if not hub_token:
                st.error("GitHub 토큰 필요")
            else:
                src = Path(m["projects"][hub_project]["src"])
                rows = gh_upload_folder(src, hub_owner, hub_repo, hub_branch, hub_token, hub_msg, "")
                ok = sum(1 for r in rows if r["ok"])
                fail = len(rows) - ok
                rec = {
                    "time": datetime.now().isoformat(timespec="seconds"),
                    "project": hub_project,
                    "repo": f"{hub_owner}/{hub_repo}",
                    "branch": hub_branch,
                    "ok": ok,
                    "fail": fail,
                    "rows": rows,
                    "type": "codegen_hub_upload"
                }
                m.setdefault("hub_uploads", []).append(rec)
                m.setdefault("github_deploys", []).append(rec)
                save_event(m, "hub_uploads", {"type":"codegen_hub_upload","project":hub_project,"status":"SUCCESS" if fail==0 else "PARTIAL","summary":f"성공 {ok}, 실패 {fail}"})
                m["projects"][hub_project]["github"] = {"owner": hub_owner, "repo": hub_repo, "branch": hub_branch, "prefix": ""}
                save(m)
                if fail == 0:
                    st.success("생성 앱 GitHub 허브 자동 업로드 완료")
                else:
                    st.warning(f"일부 제외/실패: 성공 {ok}, 실패 {fail}")
                st.json(rows[:100])

with tabs[2]:
    name = st.text_input("프로젝트 이름", placeholder="maru-kra-final-clean", key="maru_project_name")
    app_url = st.text_input("배포 앱 주소", placeholder="https://maru-kra-final-clean.streamlit.app", key="maru_app_url")
    api_key = st.text_input("API KEY/TOKEN 선택", type="password")
    api_urls = st.text_area("API URL 목록 - 한 줄에 하나")
    up = st.file_uploader("ZIP 또는 app.py", type=["zip","py"])
    if st.button("저장 + 자동검사", type="primary", use_container_width=True):
        pname = infer_project_name(name, app_url, up)
        if not up and pname not in m["projects"]:
            st.warning("처음 등록은 ZIP 또는 app.py 필요")
        else:
            old = m["projects"].get(pname, {})
            src = unzip_upload(up, pname) if up else Path(old["src"])
            app_path = find_app(src)
            info = {
                "name": pname, "src": str(src), "app_file": str(app_path) if app_path else "",
                "app_url": app_url.strip() or old.get("app_url",""),
                "api_key": api_key or old.get("api_key",""),
                "api_urls": [x.strip() for x in api_urls.splitlines() if x.strip()] or old.get("api_urls", []),
                "version": old.get("version", 0),
                "github": old.get("github", {}),
                "scan": scan(src), "syntax": syntax_all(src), "errors": inspect_error_files(src), "analysis": analyze_app(app_path)
            }
            m["projects"][pname] = info
            m["file_checks"].append({"time": datetime.now().isoformat(timespec="seconds"), "project": pname, "scan": info["scan"]})
            save_event(m, "projects", {"type":"project_register","project":pname,"status":"SAVED","summary":"프로젝트 등록/검사"})
            save(m)
            st.success(f"등록/검사 완료: {pname}")
            st.json(info["scan"]); st.json(info["analysis"])

with tabs[7]:
    ps = list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel = st.selectbox("프로젝트", ps, key="scan")
        info = m["projects"][sel]; src = Path(info["src"])
        if st.button("다시 검사", type="primary", use_container_width=True):
            app_path = find_app(src)
            info.update({"scan": scan(src), "syntax": syntax_all(src), "errors": inspect_error_files(src), "analysis": analyze_app(app_path)})
            save(m); st.success("검사 완료")
        st.subheader("파일 목록"); st.json(info.get("scan", {}))
        st.subheader("문법 검사"); st.json(info.get("syntax", []))
        st.subheader("오류 파일"); st.json(info.get("errors", []))
        st.subheader("기능 분석"); st.json(info.get("analysis", {}))

with tabs[3]:
    ps = list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel = st.selectbox("프로젝트", ps, key="test")
        cnt = st.number_input("반복 횟수", 1, 20, 1)
        if st.button("자동/반복 테스트", type="primary", use_container_width=True):
            info = m["projects"][sel]
            results = []
            for i in range(int(cnt)):
                rows=[]
                if info.get("app_url"): rows.append(test_url("APP_URL", info["app_url"]))
                for j,u in enumerate(info.get("api_urls",[]),1): rows.append(test_url(f"API_{j}", u, info.get("api_key","")))
                rec={"time":datetime.now().isoformat(timespec="seconds"),"project":sel,"round":i+1,"rows":rows,"analysis":analyze_tests(rows)}
                results.append(rec); m["test_records"].append(rec); save_event(m, "test_records", {"type":"test","project":sel,"status":"DONE","summary":"자동/반복 테스트"}); info["last_test"]=rec
            save(m); st.success("테스트 완료"); st.json(results)
        info = m["projects"][sel]
        st.download_button("PC 꺼져도 테스트용 maru_auto_test.yml", workflow(info.get("app_url",""), info.get("api_urls",[])).encode(), "maru_auto_test.yml", "text/yaml", use_container_width=True)

with tabs[4]:
    st.subheader("로그파일 / 오류 로그 분석")
    st.caption("Streamlit Cloud 로그를 복사해 붙여넣거나 log/txt/json 파일을 업로드하면 오류 패턴을 분석하고 필요한 패치를 추천합니다.")
    ps = list(m["projects"].keys())
    if not ps:
        st.info("먼저 프로젝트를 등록하세요.")
    else:
        sel = st.selectbox("로그 분석 대상 프로젝트", ps, key="log_project")
        pasted_log = st.text_area("로그 붙여넣기", height=220, placeholder="Streamlit Cloud 로그, Traceback, HTTP 오류, NameError 등을 여기에 붙여넣으세요.")
        log_file = st.file_uploader("로그파일 업로드", type=["txt", "log", "json", "csv"], key="manual_log_upload")
        if st.button("로그 분석 + 패치 추천 저장", type="primary", use_container_width=True):
            file_text = decode_uploaded_log(log_file)
            combined = (pasted_log or "") + "\n\n" + (file_text or "")
            if not combined.strip():
                st.warning("붙여넣은 로그 또는 업로드한 로그파일이 필요합니다.")
            else:
                analysis = parse_log(combined)
                rec = {
                    "time": datetime.now().isoformat(timespec="seconds"),
                    "project": sel,
                    "summary": analysis,
                    "recommended_patches": analysis.get("recommended_patches", []),
                    "preview": combined[:3000],
                }
                m.setdefault("log_analyses", []).append(rec)
                m["projects"][sel]["last_log_analysis"] = rec
                save_event(m, "log_analyses", {
                    "type": "log_analysis",
                    "project": sel,
                    "status": "DONE",
                    "summary": "수동 로그 분석",
                    "data": rec,
                })
                save(m)
                st.success("로그 분석 완료. 추천 패치를 ✅ 패치 탭에서 승인할 수 있습니다.")
                st.json(analysis)
        last = m.get("projects", {}).get(sel, {}).get("last_log_analysis")
        if last:
            st.markdown("### 최근 로그 분석 결과")
            st.json(last)

with tabs[5]:
    st.subheader("사진 첨부 분석 + 명령 입력")
    st.caption("앱 화면 캡처/오류 사진을 올리고 명령을 입력하면 패치 추천으로 저장합니다.")
    ps = list(m["projects"].keys())
    if not ps:
        st.info("먼저 프로젝트를 등록하세요.")
    else:
        sel = st.selectbox("사진 분석 대상 프로젝트", ps, key="image_command_project")
        imgs = st.file_uploader(
            "사진 첨부",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key="image_command_uploads",
        )
        cmd = st.text_area(
            "명령 입력",
            height=140,
            placeholder="예: 이 화면에서 버튼이 너무 작아. 모바일에서 크게 보이게 패치 추천해줘. / 이 오류 화면 보고 원인 찾아줘.",
            key="image_command_text",
        )
        st.info("사진은 근거 파일로 저장하고, 입력한 명령을 분석해서 패치 추천으로 연결합니다.")
        if st.button("사진 저장 + 명령 분석 + 패치 추천 저장", type="primary", use_container_width=True):
            if not imgs and not cmd.strip():
                st.warning("사진 또는 명령 입력이 필요합니다.")
            else:
                saved = save_uploaded_images(sel, imgs)
                analysis = analyze_image_command(cmd, saved)
                rec = {
                    "time": datetime.now().isoformat(timespec="seconds"),
                    "project": sel,
                    "summary": analysis,
                    "recommended_patches": analysis.get("recommended_patches", []),
                    "command": cmd,
                    "images": saved,
                }
                m.setdefault("image_analyses", []).append(rec)
                m.setdefault("command_records", []).append(rec)
                m["projects"][sel]["last_image_analysis"] = rec
                save_event(m, "image_analyses", {
                    "type": "image_command_analysis",
                    "project": sel,
                    "status": "DONE",
                    "summary": "사진 첨부/명령 분석",
                    "data": rec,
                })
                save(m)
                st.success("사진/명령 분석 완료. 추천 패치를 ✅ 패치 탭에서 승인할 수 있습니다.")
                st.json(analysis)
        last_img = m.get("projects", {}).get(sel, {}).get("last_image_analysis")
        if last_img:
            st.markdown("### 최근 사진/명령 분석 결과")
            st.json(last_img)

with tabs[6]:
    ps = list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel = st.selectbox("프로젝트", ps, key="patch")
        info = m["projects"][sel]; src=Path(info["src"]); app_path=Path(info.get("app_file","")) if info.get("app_file") else find_app(src)
        recset=set()
        if info.get("last_test"): recset.update(info["last_test"]["analysis"].get("recommended_patches",[]))
        if info.get("last_log_analysis"): recset.update(info["last_log_analysis"].get("recommended_patches", []))
        if info.get("last_image_analysis"): recset.update(info["last_image_analysis"].get("recommended_patches", []))
        for e in info.get("errors",[]): recset.update(e.get("analysis",{}).get("recommended_patches",[]))
        st.json(analyze_app(app_path))
        approved=[]
        for k,v in PATCHES.items():
            default = k in recset
            if st.checkbox(v, value=default, key=f"{sel}_{k}"): approved.append(k)
        st.error("자동구매/자동결제는 이 앱에서 지원하지 않고 차단합니다.")
        if st.button("승인 항목 실제 패치 → 새 ZIP 생성", type="primary", use_container_width=True):
            before=analyze_app(app_path)
            apply_patch(app_path, approved)
            add_helpers(src, approved)
            ensure_req(src)
            after=analyze_app(app_path)
            syn=syntax_all(src)
            ver=int(info.get("version",0))+1; info["version"]=ver; info["analysis"]=after
            write(src/f"feature_snapshot_v{ver:03d}.json", json.dumps({"before":before,"after":after,"approved":approved}, ensure_ascii=False, indent=2))
            zp=make_zip(src, sel, ver)
            ok=all(x["ok"] for x in syn)
            row={"time":datetime.now().isoformat(timespec="seconds"),"project":sel,"version":ver,"approved":approved,"syntax_ok":ok,"zip":str(zp)}
            m["patch_records"].append(row); save_event(m, "patch_records", {"type":"patch","project":sel,"version":ver,"status":"SUCCESS" if ok else "CHECK","summary":"승인 패치"}); save(m)
            st.success(f"패치 완료 v{ver:03d}" if ok else "패치됐지만 문법 오류 확인 필요")
            st.json({"before":before,"after":after,"syntax":syn})
            with open(zp,"rb") as f: st.download_button("패치 ZIP 다운로드", f, file_name=zp.name, mime="application/zip", use_container_width=True)

with tabs[9]:
    ps=list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트", ps, key="gh")
        info=m["projects"][sel]; old=info.get("github",{})
        c1,c2=st.columns(2)
        with c1:
            owner=st.text_input("GitHub owner", old.get("owner","skytins3-png"))
            repo=st.text_input("대상 repo", old.get("repo","maru-kra-final-clean"))
            branch=st.text_input("branch", old.get("branch","main"))
            prefix=st.text_input("업로드 폴더 prefix", old.get("prefix",""), placeholder="비우면 루트")
        with c2:
            token=st.text_input("GitHub 토큰", type="password")
            msg=st.text_input("커밋 메시지", f"MARU auto patch deploy {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            savecfg=st.checkbox("토큰 제외 설정 저장", value=True)
            st.warning("토큰은 저장하지 않습니다. 매번 입력하거나 Streamlit Secrets를 쓰는 게 안전합니다.")
            st.info(".github/workflows 폴더는 GitHub 보안권한 문제 방지를 위해 자동 업로드에서 제외합니다.")
        if st.button("연결 확인", use_container_width=True):
            if not token: st.error("토큰 필요")
            else:
                code,data=gh_repo(owner,repo,token)
                st.success("연결 성공") if code==200 else st.error(f"실패 HTTP {code}")
                st.json(data)
        if st.button("대상 GitHub 저장소에 자동 업로드/커밋", type="primary", use_container_width=True):
            if not token: st.error("토큰 필요")
            else:
                if savecfg:
                    info["github"]={"owner":owner,"repo":repo,"branch":branch,"prefix":prefix}; save(m)
                rows=gh_upload_folder(Path(info["src"]), owner, repo, branch, token, msg, prefix)
                ok=sum(1 for r in rows if r["ok"]); fail=len(rows)-ok
                deploy={"time":datetime.now().isoformat(timespec="seconds"),"project":sel,"repo":f"{owner}/{repo}","branch":branch,"ok":ok,"fail":fail,"rows":rows}
                m["github_deploys"].append(deploy); save_event(m, "github_deploys", {"type":"github_deploy","project":sel,"status":"SUCCESS" if fail==0 else "PARTIAL","summary":f"성공 {ok}, 실패 {fail}"}); save(m)
                st.success("GitHub 자동반영 완료. Streamlit Cloud가 곧 재배포합니다." if fail==0 else f"일부 실패: 성공 {ok}, 실패 {fail}")
                st.json(rows[:100])

with tabs[8]:
    ps=list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트", ps, key="ver")
        info=m["projects"][sel]; src=Path(info["src"])
        st.metric("현재 버전", info.get("version",0))
        st.download_button("현재 보관본 ZIP", zip_bytes(src), f"{sname(sel)}_CURRENT.zip", "application/zip", use_container_width=True)
        app_path=Path(info.get("app_file","")) if info.get("app_file") else find_app(src)
        if app_path and app_path.exists():
            st.download_button("단일 app.py", read(app_path).encode(), f"{sname(sel)}_app.py", "text/x-python", use_container_width=True)


with tabs[10]:
    st.subheader("구글시트 허브 저장")
    st.caption("프로젝트, 테스트, 패치, GitHub 자동반영, 코드생성 허브 업로드 기록을 Google Sheets에 저장합니다.")
    cfg = get_gsheet_config(m)
    enabled = st.checkbox("구글시트 저장 사용", value=bool(cfg.get("enabled")))
    sheet_id = st.text_input("Google Sheet ID", value=cfg.get("sheet_id", ""))
    service_json = st.text_area("서비스계정 JSON", value=cfg.get("service_account_json", ""), height=180)
    st.info("서비스계정 JSON 안의 client_email을 Google Sheet 편집자로 공유해야 연결됩니다.")
    if st.button("구글시트 설정 저장", type="primary", use_container_width=True):
        cfg.update({"enabled": enabled, "sheet_id": sheet_id.strip(), "service_account_json": service_json.strip()})
        m["google_sheets"] = cfg
        save(m)
        st.success("구글시트 설정 저장 완료")
    if st.button("연결 테스트", use_container_width=True):
        cfg.update({"enabled": enabled, "sheet_id": sheet_id.strip(), "service_account_json": service_json.strip()})
        m["google_sheets"] = cfg
        ok, msg = gsheet_append(m, "connection_test", {
            "type": "connection_test",
            "project": "MARU",
            "status": "TEST",
            "summary": "구글시트 연결 테스트",
        })
        save(m)
        if ok:
            st.success(msg)
        else:
            st.error(msg)
    st.markdown("### 저장되는 탭")
    st.write(["connection_test", "projects", "test_records", "patch_records", "github_deploys", "hub_uploads", "log_analyses", "image_analyses", "generated_projects", "lessons"])

with tabs[11]:
    st.subheader("GitHub 자동반영 기록"); st.json(m.get("github_deploys", [])[-20:])
    st.subheader("코드생성 허브 업로드 기록"); st.json(m.get("hub_uploads", [])[-20:])
    st.subheader("패치 기록"); st.json(m.get("patch_records", [])[-20:])
    st.subheader("테스트 기록"); st.json(m.get("test_records", [])[-20:])
    st.subheader("로그 분석 기록"); st.json(m.get("log_analyses", [])[-20:])
    st.subheader("사진/명령 분석 기록"); st.json(m.get("image_analyses", [])[-20:])
    st.subheader("학습"); st.json(m.get("lessons", [])[-50:])

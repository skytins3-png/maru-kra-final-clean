
import streamlit as st

# ===== MARU V14 hard block Streamlit help dumps =====
try:
    _MARU_ORIG_HELP = st.help
except Exception:
    _MARU_ORIG_HELP = None

def _maru_block_help(obj=None, *args, **kwargs):
    try:
        s = str(obj)
    except Exception:
        s = ""
    # Streamlit 자체 도움말은 화면에 길게 뿌리지 않음
    if obj is st or "streamlit" in s.lower() or "DeltaGenerator" in s or "BottomContainerProxy" in s:
        return None
    if _MARU_ORIG_HELP:
        return _MARU_ORIG_HELP(obj, *args, **kwargs)
    return None

try:
    st.help = _maru_block_help
except Exception:
    pass

def _maru_strip_streamlit_help_text(s):
    try:
        s = str(s)
    except Exception:
        return s
    markers = [
        "Streamlit 사용법",
        "Take a look at the other commands",
        "dir(streamlit)",
        "streamlit hello",
        "BottomContainerProxy",
        "QueryParamsProxy",
        ">>> import streamlit as st",
        "For more detailed info, see https://docs.streamlit.io",
        "더 자세한 정보는 https://docs.streamlit.io",
    ]
    if any(m in s for m in markers):
        return ""
    return s

# 기존 안전 출력 함수가 있든 없든 한 번 더 강제 차단
try:
    _MARU_ORIG_WRITE2 = st.write
    _MARU_ORIG_MARKDOWN2 = st.markdown
    _MARU_ORIG_TEXT2 = st.text
    _MARU_ORIG_CODE2 = st.code

    def _maru_write2(*args, **kwargs):
        clean = [_maru_strip_streamlit_help_text(a) for a in args]
        clean = [a for a in clean if a not in ("", None)]
        if not clean:
            return None
        return _MARU_ORIG_WRITE2(*clean, **kwargs)

    def _maru_markdown2(body, *args, **kwargs):
        body = _maru_strip_streamlit_help_text(body)
        if not body:
            return None
        return _MARU_ORIG_MARKDOWN2(body, *args, **kwargs)

    def _maru_text2(body="", *args, **kwargs):
        body = _maru_strip_streamlit_help_text(body)
        if not body:
            return None
        return _MARU_ORIG_TEXT2(body, *args, **kwargs)

    def _maru_code2(body="", *args, **kwargs):
        body = _maru_strip_streamlit_help_text(body)
        if not body:
            return None
        return _MARU_ORIG_CODE2(body, *args, **kwargs)

    st.write = _maru_write2
    st.markdown = _maru_markdown2
    st.text = _maru_text2
    st.code = _maru_code2
except Exception:
    pass
# ===== /MARU V14 hard block Streamlit help dumps =====


# ===== MARU V14 display guard: hide accidental Streamlit help/debug dumps =====
_MARU_ORIG_WRITE = st.write
_MARU_ORIG_MARKDOWN = st.markdown
_MARU_ORIG_TEXT = st.text
_MARU_ORIG_CODE = st.code

def _maru_is_streamlit_debug_dump(obj):
    try:
        s = str(obj)
    except Exception:
        return False
    markers = [
        "Streamlit 사용법",
        "Take a look at the other commands",
        "dir(streamlit)",
        "streamlit hello",
        "BottomContainerProxy",
        "QueryParamsProxy",
        "https://docs.streamlit.io",
        ">>> import streamlit as st",
    ]
    return any(m in s for m in markers)

def _maru_safe_write(*args, **kwargs):
    if args and any(_maru_is_streamlit_debug_dump(a) for a in args):
        return None
    return _MARU_ORIG_WRITE(*args, **kwargs)

def _maru_safe_markdown(body, *args, **kwargs):
    if _maru_is_streamlit_debug_dump(body):
        return None
    return _MARU_ORIG_MARKDOWN(body, *args, **kwargs)

def _maru_safe_text(body="", *args, **kwargs):
    if _maru_is_streamlit_debug_dump(body):
        return None
    return _MARU_ORIG_TEXT(body, *args, **kwargs)

def _maru_safe_code(body="", *args, **kwargs):
    if _maru_is_streamlit_debug_dump(body):
        return None
    return _MARU_ORIG_CODE(body, *args, **kwargs)

st.write = _maru_safe_write
st.markdown = _maru_safe_markdown
st.text = _maru_safe_text
st.code = _maru_safe_code
# ===== /MARU V14 display guard =====


# ===== MARU V14 absolute compatibility helpers =====
try:
    st
except NameError:
    import streamlit as st

def maru_secret_first(*names, default=""):
    for _name in names:
        try:
            _val = st.secrets.get(_name, "")
            if _val:
                return _val
        except Exception:
            pass
    return default

def maru_maru_get_default_profile(mem_obj=None):
    _base = {
        "project_name": "maru-kra-final-clean",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-kra-final-clean",
        "github_branch": "main",
    }
    try:
        if mem_obj is not None:
            _prof = mem_obj.setdefault("default_profile", {})
            for _k, _v in _base.items():
                _prof.setdefault(_k, _v)
            return _prof
    except Exception:
        pass
    return _base

def maru_maru_profile_from_choice(choice, mem_obj=None):
    _presets = {
        "경마앱": {"project_name":"maru-kra-final-clean","app_url":"https://maru-kra-final-clean.streamlit.app","api_key":"","api_urls":"","github_owner":"skytins3-png","github_repo":"maru-kra-final-clean","github_branch":"main"},
        "토토앱": {"project_name":"skytoto-ai-hub","app_url":"","api_key":"","api_urls":"","github_owner":"skytins3-png","github_repo":"skytoto-ai-hub","github_branch":"main"},
        "AI 코드 생성기": {"project_name":"maru-ai-code-maker","app_url":"https://maru-ai-code-maker.streamlit.app","api_key":"","api_urls":"","github_owner":"skytins3-png","github_repo":"maru-ai-code-maker","github_branch":"main"},
        "직접입력": {"project_name":"","app_url":"","api_key":"","api_urls":"","github_owner":"skytins3-png","github_repo":"","github_branch":"main"},
    }
    _p = _presets.get(choice, _presets["직접입력"]).copy()
    if choice == "직접입력":
        _p.update(maru_maru_get_default_profile(mem_obj))
    else:
        _cur = maru_maru_get_default_profile(mem_obj)
        if _cur.get("api_key") and not _p.get("api_key"):
            _p["api_key"] = _cur.get("api_key", "")
        if _cur.get("api_urls") and not _p.get("api_urls"):
            _p["api_urls"] = _cur.get("api_urls", "")
    return _p

def maru_api_key_for(choice, mem_obj=None):
    if choice == "경마앱":
        return maru_secret_first("KRA_API_KEY", "PUBLIC_DATA_API_KEY", "MARU_KRA_API_KEY", default=maru_maru_get_default_profile(mem_obj).get("api_key", ""))
    if choice == "토토앱":
        return maru_secret_first("TOTO_API_KEY", "SPORTS_API_KEY", "SPORTMONKS_TOKEN", "MARU_TOTO_API_KEY", default=maru_maru_get_default_profile(mem_obj).get("api_key", ""))
    return maru_maru_get_default_profile(mem_obj).get("api_key", "")

def maru_api_urls_for(choice, mem_obj=None):
    _cur = maru_maru_get_default_profile(mem_obj).get("api_urls", "")
    if _cur:
        return _cur
    if choice == "경마앱":
        return "\n".join([
            "https://apis.data.go.kr/B551015/API310/raceInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json",
            "https://apis.data.go.kr/B551015/API310/entryInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json",
            "https://apis.data.go.kr/B551015/API310/horseInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json",
        ])
    if choice == "토토앱":
        return "\n".join([
            "https://api.sportmonks.com/v3/football/fixtures/date/{today_dash}?api_token={api_key}&include=participants;league",
            "https://api.sportmonks.com/v3/football/fixtures/between/{today_dash}/{today_dash}?api_token={api_key}&include=participants;league",
        ])
    return ""

def maru_github_token():
    return maru_secret_first("GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token", default="")

# Backward-compatible names. If old screen code calls these, they now always exist.
def default_api_key_for(choice, mem_obj=None):
    return maru_api_key_for(choice, mem_obj)

def default_api_urls_for(choice, mem_obj=None):
    return maru_api_urls_for(choice, mem_obj)

def maru_profile_from_choice(choice, mem_obj=None):
    return maru_maru_profile_from_choice(choice, mem_obj)

def maru_get_default_profile(mem_obj=None):
    return maru_maru_get_default_profile(mem_obj)

def maru_github_token():
    return maru_secret_first("GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token", default="")

def maru_github_token():
    return maru_secret_first("GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token", default="")
# ===== /MARU V14 absolute compatibility helpers =====


# ===== MARU V14 missing helper hotfix =====
def _maru_secret_get(name, default=""):
    try:
        value = st.secrets.get(name, default)
        return value if value is not None else default
    except Exception:
        return default

def secret_first(*names, default=""):
    for name in names:
        value = _maru_secret_get(name, "")
        if value:
            return value
    return default

def maru_get_default_profile(mem_obj=None):
    base = {
        "project_name": "maru-kra-final-clean",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-kra-final-clean",
        "github_branch": "main",
    }
    try:
        if mem_obj is not None:
            prof = mem_obj.setdefault("default_profile", {})
            for k, v in base.items():
                prof.setdefault(k, v)
            return prof
    except Exception:
        pass
    return base

PROJECT_PRESETS = {
    "경마앱": {
        "project_name": "maru-kra-final-clean",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-kra-final-clean",
        "github_branch": "main",
    },
    "토토앱": {
        "project_name": "skytoto-ai-hub",
        "app_url": "",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "skytoto-ai-hub",
        "github_branch": "main",
    },
    "AI 코드 생성기": {
        "project_name": "maru-ai-code-maker",
        "app_url": "https://maru-ai-code-maker.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-ai-code-maker",
        "github_branch": "main",
    },
    "직접입력": {
        "project_name": "",
        "app_url": "",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "",
        "github_branch": "main",
    },
}

def maru_profile_from_choice(choice, mem_obj=None):
    prof = PROJECT_PRESETS.get(choice, PROJECT_PRESETS["직접입력"]).copy()
    if choice == "직접입력":
        current = maru_get_default_profile(mem_obj)
        prof.update(current)
        return prof
    try:
        current = maru_get_default_profile(mem_obj)
        if current.get("api_key") and not prof.get("api_key"):
            prof["api_key"] = current.get("api_key", "")
        if current.get("api_urls") and not prof.get("api_urls"):
            prof["api_urls"] = current.get("api_urls", "")
    except Exception:
        pass
    return prof

def maru_api_key_for(choice, mem_obj=None):
    if choice == "경마앱":
        return secret_first(
            "KRA_API_KEY",
            "PUBLIC_DATA_API_KEY",
            "MARU_KRA_API_KEY",
            default=maru_get_default_profile(mem_obj).get("api_key", ""),
        )
    if choice == "토토앱":
        return secret_first(
            "TOTO_API_KEY",
            "SPORTS_API_KEY",
            "SPORTMONKS_TOKEN",
            "MARU_TOTO_API_KEY",
            default=maru_get_default_profile(mem_obj).get("api_key", ""),
        )
    return maru_get_default_profile(mem_obj).get("api_key", "")

def maru_api_urls_for(choice, mem_obj=None):
    current = maru_get_default_profile(mem_obj).get("api_urls", "")
    if current:
        return current
    if choice == "경마앱":
        return "\n".join([
            "https://apis.data.go.kr/B551015/API310/raceInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json",
            "https://apis.data.go.kr/B551015/API310/entryInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json",
            "https://apis.data.go.kr/B551015/API310/horseInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json",
        ])
    if choice == "토토앱":
        return "\n".join([
            "https://api.sportmonks.com/v3/football/fixtures/date/{today_dash}?api_token={api_key}&include=participants;league",
            "https://api.sportmonks.com/v3/football/fixtures/between/{today_dash}/{today_dash}?api_token={api_key}&include=participants;league",
        ])
    return ""

def maru_github_token():
    return secret_first("GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token", default="")

def maru_github_token():
    return maru_secret_first("GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token", default="")
# ===== /MARU V14 missing helper hotfix =====

import zipfile, json, shutil, io, re, ast, subprocess, sys, base64, time
from pathlib import Path
from datetime import datetime, timezone, timedelta


# ===== MARU V14.5 KST final safe time helpers =====
try:
    KST
except NameError:
    KST = timezone(timedelta(hours=9))

def maru_now_kst():
    try:
        return maru_now_kst()
    except Exception:
        return datetime.now(timezone(timedelta(hours=9)))

def maru_now_kst_text():
    return maru_now_kst().strftime("%Y-%m-%d %H:%M:%S KST")
# ===== /MARU V14.5 KST final safe time helpers =====


# 한국시간 고정값
KST = timezone(timedelta(hours=9))

import requests

ROOT = Path(__file__).parent
MEM = ROOT / "ai_memory.json"


# ===== MARU V14.6 save_memory compatibility hotfix =====
def save_memory(mem_obj):
    """기존 앱에 저장 함수명이 없거나 달라도 보관소/루프가 멈추지 않게 하는 호환 저장 함수."""
    try:
        target = globals().get("MEM", None)
        if target is None:
            target = Path(__file__).parent / "ai_memory.json"
        target = Path(target)
        target.write_text(json.dumps(mem_obj, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception as e:
        try:
            st.warning(f"메모리 저장 실패: {e}")
        except Exception:
            pass
        return False

def load_memory_safe(default=None):
    try:
        target = globals().get("MEM", None)
        if target is None:
            target = Path(__file__).parent / "ai_memory.json"
        target = Path(target)
        if target.exists():
            return json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default if default is not None else {}
# ===== /MARU V14.6 save_memory compatibility hotfix =====

STORE = ROOT / "project_storage"
VERS = ROOT / "version_outputs"
GENERATED = ROOT / "generated_projects"
IMAGE_STORE = ROOT / "image_uploads"


# ===== MARU V14 project vault auto apply =====
MARU_PROJECT_VAULT_DIR = ROOT / "project_vault"
MARU_PROJECT_VAULT_DIR.mkdir(parents=True, exist_ok=True)

MARU_PROJECT_PRESETS = {
    "경마앱": {
        "project_name": "maru-kra-final-clean",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "github_owner": "skytins3-png",
        "github_repo": "maru-kra-final-clean",
        "github_branch": "main",
    },
    "토토앱": {
        "project_name": "skytoto-ai-hub",
        "app_url": "",
        "github_owner": "skytins3-png",
        "github_repo": "skytoto-ai-hub",
        "github_branch": "main",
    },
    "AI 코드 생성기": {
        "project_name": "maru-ai-code-maker",
        "app_url": "https://maru-ai-code-maker.streamlit.app",
        "github_owner": "skytins3-png",
        "github_repo": "maru-ai-code-maker",
        "github_branch": "main",
    },
}

def maru_vault_key(label):
    preset = MARU_PROJECT_PRESETS.get(label, dict())
    name = preset.get("project_name", label)
    return str(name).replace("/", "_").replace(" ", "_")

def maru_vault_project_dir(label):
    d = MARU_PROJECT_VAULT_DIR / maru_vault_key(label)
    d.mkdir(parents=True, exist_ok=True)
    return d

def maru_vault_src_dir(label):
    d = maru_vault_project_dir(label) / "latest_src"
    d.mkdir(parents=True, exist_ok=True)
    return d

def maru_vault_meta_path(label):
    return maru_vault_project_dir(label) / "vault_meta.json"

def maru_read_vault_meta(label):
    p = maru_vault_meta_path(label)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return dict()
    return dict()

def maru_write_vault_meta(label, meta):
    meta["updated_at"] = maru_now_kst_text()
    maru_vault_meta_path(label).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

def maru_load_project_from_vault(mem_obj, label):
    preset = MARU_PROJECT_PRESETS.get(label, dict())
    pname = preset.get("project_name", label)
    src = maru_vault_src_dir(label)
    meta = maru_read_vault_meta(label)
    if not (src / "app.py").exists():
        return False, f"{label} 보관소에 app.py가 없습니다. 최초 1회만 ZIP/app.py를 보관소에 저장하세요."
    mem_obj.setdefault("projects", dict())
    mem_obj["projects"][pname] = {
        "name": pname,
        "src": str(src),
        "app_url": preset.get("app_url", meta.get("app_url", "")),
        "api_key": meta.get("api_key", ""),
        "api_urls": meta.get("api_urls", []),
        "github": {
            "owner": preset.get("github_owner", "skytins3-png"),
            "repo": preset.get("github_repo", pname),
            "branch": preset.get("github_branch", "main"),
        },
        "vault_label": label,
        "vault_auto": True,
        "updated_at": maru_now_kst_text(),
    }
    mem_obj["default_project"] = pname
    mem_obj["default_profile"] = {
        "project_name": pname,
        "app_url": preset.get("app_url", ""),
        "api_key": meta.get("api_key", ""),
        "api_urls": "\\n".join(meta.get("api_urls", [])) if isinstance(meta.get("api_urls", []), list) else str(meta.get("api_urls", "")),
        "github_owner": preset.get("github_owner", "skytins3-png"),
        "github_repo": preset.get("github_repo", pname),
        "github_branch": preset.get("github_branch", "main"),
    }
    save_memory(mem_obj)
    return True, f"{label} 최신파일을 보관소에서 불러왔습니다. 이제 등록 없이 패치/검사/GitHub 자동반영 가능합니다."

def maru_save_upload_to_vault(label, uploaded_file, api_key="", api_urls_text=""):
    src = maru_vault_src_dir(label)
    if src.exists():
        shutil.rmtree(src)
    src.mkdir(parents=True, exist_ok=True)
    raw_dir = maru_vault_project_dir(label) / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    filename = uploaded_file.name
    raw_path = raw_dir / filename
    raw_path.write_bytes(uploaded_file.getvalue())
    if filename.lower().endswith(".zip"):
        with zipfile.ZipFile(raw_path, "r") as z:
            z.extractall(src)
        nested_apps = list(src.rglob("app.py"))
        if nested_apps and not (src / "app.py").exists():
            root = nested_apps[0].parent
            temp = maru_vault_project_dir(label) / "_flatten_temp"
            if temp.exists():
                shutil.rmtree(temp)
            shutil.copytree(root, temp)
            shutil.rmtree(src)
            temp.rename(src)
    else:
        (src / filename).write_bytes(raw_path.read_bytes())
        if filename != "app.py" and filename.lower().endswith(".py"):
            shutil.copy2(src / filename, src / "app.py")
    api_urls = [x.strip() for x in str(api_urls_text).splitlines() if x.strip()]
    meta = {
        "label": label,
        "project_name": MARU_PROJECT_PRESETS.get(label, dict()).get("project_name", label),
        "filename": filename,
        "api_key": api_key,
        "api_urls": api_urls,
        "src": str(src),
    }
    maru_write_vault_meta(label, meta)
    return src, meta
# ===== /MARU V14 project vault auto apply =====


# ===== MARU V14.1 continuous patch-test-log loop =====
def maru_run_basic_project_test(src):
    """보관소/프로젝트 소스 기준 기본 테스트: 파일 존재, 문법, requirements 확인."""
    result = {
        "ok": True,
        "checks": [],
        "errors": [],
        "logs": [],
    }
    src = Path(src)
    app_file = src / "app.py"
    if not app_file.exists():
        result["ok"] = False
        result["errors"].append("app.py 없음")
    else:
        result["checks"].append("app.py 확인")
        try:
            py_compile.compile(str(app_file), doraise=True)
            result["checks"].append("app.py 문법 검사 통과")
        except Exception as e:
            result["ok"] = False
            result["errors"].append("app.py 문법 오류: " + str(e))
    req = src / "requirements.txt"
    if req.exists():
        result["checks"].append("requirements.txt 확인")
    else:
        result["logs"].append("requirements.txt 없음: Streamlit 기본 의존성만 사용 가능")
    return result

def maru_analyze_loop_logs(test_result):
    """테스트 결과를 로그분석 형태로 정리하고 다음 패치 힌트 생성."""
    hints = []
    for e in test_result.get("errors", []):
        if "app.py 없음" in e:
            hints.append("보관소 ZIP 구조를 확인하고 app.py가 루트에 오도록 평탄화하세요.")
        elif "SyntaxError" in e or "문법 오류" in e:
            hints.append("app.py 문법 오류 위치를 찾아 자동 패치 후보로 등록하세요.")
        elif "NameError" in e:
            hints.append("누락 함수/변수 호환 helper를 상단에 추가하세요.")
        else:
            hints.append("오류 로그 기반으로 해당 파일을 재검사하세요: " + e[:160])
    if not hints and test_result.get("ok"):
        hints.append("테스트 통과: GitHub 자동반영 후 Streamlit 로그 확인 단계로 진행 가능")
    return hints

def maru_loop_event(mem_obj, project_name, step, status, detail):
    mem_obj.setdefault("continuous_loop_history", []).append({
        "time": maru_now_kst_text(),
        "project": project_name,
        "step": step,
        "status": status,
        "detail": detail,
    })
    mem_obj["continuous_loop_history"] = mem_obj["continuous_loop_history"][-100:]
    save_memory(mem_obj)

def maru_get_project_info_from_choice(mem_obj, label):
    ok, msg = maru_load_project_from_vault(mem_obj, label)
    if not ok:
        return None, msg
    pname = MARU_PROJECT_PRESETS[label]["project_name"]
    return mem_obj.get("projects", {}).get(pname), msg

def maru_run_continuous_loop_once(mem_obj, label, do_github=False, github_token="", commit_msg="MARU auto loop patch"):
    """한 번의 연속 루프: 보관소 불러오기 -> 테스트 -> 로그분석 -> 필요 시 GitHub 자동반영."""
    info, msg = maru_get_project_info_from_choice(mem_obj, label)
    if not info:
        return [{"step": "보관소 불러오기", "status": "실패", "detail": msg}]
    project_name = info.get("name", MARU_PROJECT_PRESETS[label]["project_name"])
    src = Path(info.get("src", ""))
    rows = []
    rows.append({"step": "보관소 불러오기", "status": "성공", "detail": msg})
    maru_loop_event(mem_obj, project_name, "보관소 불러오기", "성공", msg)

    test_result = maru_run_basic_project_test(src)
    rows.append({"step": "자동 테스트", "status": "성공" if test_result.get("ok") else "실패", "detail": json.dumps(test_result, ensure_ascii=False)})
    maru_loop_event(mem_obj, project_name, "자동 테스트", "성공" if test_result.get("ok") else "실패", json.dumps(test_result, ensure_ascii=False))

    hints = maru_analyze_loop_logs(test_result)
    rows.append({"step": "로그분석", "status": "완료", "detail": " / ".join(hints)})
    maru_loop_event(mem_obj, project_name, "로그분석", "완료", " / ".join(hints))

    if test_result.get("ok") and do_github:
        gh = info.get("github", {})
        owner = gh.get("owner", "skytins3-png")
        repo = gh.get("repo", project_name)
        branch = gh.get("branch", "main")
        token = github_token or (get_github_token_from_secret() if "get_github_token_from_secret" in globals() else "")
        if not token:
            rows.append({"step": "GitHub 자동반영", "status": "대기", "detail": "GITHUB_TOKEN 없음"})
            maru_loop_event(mem_obj, project_name, "GitHub 자동반영", "대기", "GITHUB_TOKEN 없음")
        else:
            try:
                upload_rows = gh_upload_folder(src, owner, repo, branch, token, commit_msg, "")
                ok_count = sum(1 for r in upload_rows if r.get("ok"))
                fail_count = sum(1 for r in upload_rows if not r.get("ok"))
                detail = f"성공 {ok_count}, 실패 {fail_count}"
                rows.append({"step": "GitHub 자동반영", "status": "성공" if fail_count == 0 else "일부실패", "detail": detail})
                maru_loop_event(mem_obj, project_name, "GitHub 자동반영", "성공" if fail_count == 0 else "일부실패", detail)
            except Exception as e:
                rows.append({"step": "GitHub 자동반영", "status": "실패", "detail": str(e)})
                maru_loop_event(mem_obj, project_name, "GitHub 자동반영", "실패", str(e))
    elif not test_result.get("ok"):
        rows.append({"step": "재패치 대기", "status": "필요", "detail": "테스트 실패 → 로그분석 힌트 기반 패치 필요"})
        maru_loop_event(mem_obj, project_name, "재패치 대기", "필요", "테스트 실패 → 로그분석 힌트 기반 패치 필요")
    else:
        rows.append({"step": "GitHub 자동반영", "status": "선택안함", "detail": "테스트까지만 실행"})
        maru_loop_event(mem_obj, project_name, "GitHub 자동반영", "선택안함", "테스트까지만 실행")
    return rows
# ===== /MARU V14.1 continuous patch-test-log loop =====


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
    "default_profile": {"project_name": "maru-kra-final-clean", "app_url": "https://maru-kra-final-clean.streamlit.app", "api_key": "", "api_urls": "", "github_owner": "skytins3-png", "github_repo": "maru-kra-final-clean", "github_branch": "main"},
    "saved_profiles": {},
    "lessons": [],
}


PROJECT_PRESETS = {
    "경마앱": {
        "project_name": "maru-kra-final-clean",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-kra-final-clean",
        "github_branch": "main",
    },
    "토토앱": {
        "project_name": "skytoto-ai-hub",
        "app_url": "",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "skytoto-ai-hub",
        "github_branch": "main",
    },
    "AI 코드 생성기": {
        "project_name": "maru-ai-code-maker",
        "app_url": "https://maru-ai-code-maker.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-ai-code-maker",
        "github_branch": "main",
    },
    "직접입력": {
        "project_name": "",
        "app_url": "",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "",
        "github_branch": "main",
    },
}

def maru_profile_from_choice(choice, mem=None):
    base = PROJECT_PRESETS.get(choice, PROJECT_PRESETS["직접입력"]).copy()
    if choice == "직접입력" and mem is not None:
        current = maru_get_default_profile(mem).copy()
        current.setdefault("github_owner", "skytins3-png")
        current.setdefault("github_branch", "main")
        return current
    if mem is not None:
        current = maru_get_default_profile(mem)
        # API 키와 API URL은 사용자가 저장한 값이 있으면 유지해서 재입력 줄이기
        if current.get("api_key") and not base.get("api_key"):
            base["api_key"] = current.get("api_key", "")
        if current.get("api_urls") and not base.get("api_urls"):
            base["api_urls"] = current.get("api_urls", "")
    return base


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
    "새 버전 ZIP 생성", "프로젝트 보관소 최신파일 자동불러오기", "패치-반영-테스트-로그분석 연속자동화", "개선 요구사항 승인 후 진행", "승인 후 패치 무승인 연속루프", "GitHub 대상 저장소 자동 업로드/커밋",
    "Streamlit Cloud 자동 재배포 유도", "구글시트 저장 구조", 
    "GitHub Actions 예약 테스트 파일 생성", "진화형 AI 코드 생성", "생성 앱 GitHub 허브 자동 업로드", "구글시트 허브 저장", "로그파일 붙여넣기/업로드 분석", "사진 첨부/명령 입력 분석", "HTML 카드 코드노출 수정", "경마시간 추천없음 표시 보정", "화면 디버그 출력 제거", "자동구매/자동결제 차단"
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
        st.download_button('현재 앱 ZIP 다운로드', buf.getvalue(), 'current_app_export.zip', 'application/zip', width="stretch")
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
    if st.button("통신 점검", type="primary", width="stretch"):
        final_url = url.replace("{{api_key}}", token).replace("{{serviceKey}}", token).replace("{{token}}", token)
        info, data = safe_get(final_url)
        st.json(info)
        if data is not None:
            st.json(data)

with tab3:
    st.subheader("기록")
    mem = load_memory()
    memo = st.text_area("메모/테스트 결과")
    if st.button("기록 저장", width="stretch"):
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
    if r.status_code == 200:
        try:
            return r.json().get("sha")
        except Exception:
            return None
    if r.status_code == 404:
        # 파일이 아직 없다는 뜻. 실패가 아니라 새 파일 생성 대상으로 처리.
        return None
    try:
        data = r.json()
    except Exception:
        data = {"message": r.text[:500]}
    raise RuntimeError(f"GitHub file lookup failed {r.status_code}: {data.get('message', '')}")

def gh_put(owner, repo, branch, path, b, msg, token):
    payload = {"message": msg, "content": base64.b64encode(b).decode(), "branch": branch}
    try:
        sha = gh_sha(owner, repo, branch, path, token)
    except Exception as e:
        return False, 0, {"message": str(e)}
    if sha:
        payload["sha"] = sha
    r = requests.put(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=gh_headers(token), json=payload, timeout=30)
    try:
        data = r.json()
    except Exception:
        data = {"text": r.text[:1000]}
    if r.status_code in [200, 201]:
        data["_mode"] = "update" if sha else "create"
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

def maru_get_default_profile(mem):
    return mem.setdefault("default_profile", {
        "project_name": "maru-kra-final-clean",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-kra-final-clean",
        "github_branch": "main",
    })

def set_default_profile(mem, profile):
    mem["default_profile"] = profile
    mem.setdefault("saved_profiles", {})[profile.get("project_name", "default")] = profile
    save(mem)

def get_secret_value(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

def maru_github_token():
    # Streamlit Secrets에 GITHUB_TOKEN / MARU_GITHUB_TOKEN 저장하면 모바일에서도 자동 입력됨
    for key in ["GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token"]:
        val = get_secret_value(key, "")
        if val:
            return val
    return ""

m = load()
st.set_page_config(page_title="MARU V15.1 경고제거 풀자동화 AI", page_icon="🧠", layout="wide")
st.markdown("<style>.block-container{max-width:1280px;padding-top:1rem}.stButton>button{height:3rem;font-weight:800}</style>", unsafe_allow_html=True)
st.title("🧠 MARU V14.4 KST 보관소 안정화 AI")
st.caption("코드생성 + 패치 + GitHub 허브 자동 업로드 → Streamlit Cloud 자동 재배포")
st.info("핵심: 이제 ZIP 다운로드 후 사람이 다시 올리는 단계 없이, 승인 후 대상 GitHub 저장소까지 자동 반영합니다.")



# ===== MARU V14.2 approval gate for improvement requirements =====
def maru_new_req_id():
    return maru_now_kst().strftime("%Y%m%d%H%M%S") + "_" + str(uuid.uuid4())[:8]

def maru_add_improvement_request(mem_obj, project_label, title, detail, priority="보통"):
    mem_obj.setdefault("improvement_requests", [])
    item = {
        "id": maru_new_req_id(),
        "time": maru_now_kst_text(),
        "project": project_label,
        "title": title.strip(),
        "detail": detail.strip(),
        "priority": priority,
        "status": "승인대기",
        "approved_at": "",
        "decision_note": "",
    }
    mem_obj["improvement_requests"].append(item)
    save_memory(mem_obj)
    return item

def maru_decide_improvement_request(mem_obj, req_id, decision, note=""):
    mem_obj.setdefault("improvement_requests", [])
    for item in mem_obj["improvement_requests"]:
        if item.get("id") == req_id:
            item["status"] = decision
            item["decision_note"] = note
            if decision == "승인":
                item["approved_at"] = maru_now_kst_text()
                mem_obj.setdefault("approved_patch_queue", [])
                mem_obj["approved_patch_queue"].append({
                    "id": req_id,
                    "time": item["approved_at"],
                    "project": item.get("project", ""),
                    "title": item.get("title", ""),
                    "detail": item.get("detail", ""),
                    "source": "개선요구 승인",
                    "status": "패치대기",
                })
            save_memory(mem_obj)
            return True, item
    return False, None

def maru_get_improvement_requests(mem_obj, status=None):
    rows = mem_obj.setdefault("improvement_requests", [])
    if status:
        return [r for r in rows if r.get("status") == status]
    return rows

def maru_get_approved_patch_queue(mem_obj, status=None):
    rows = mem_obj.setdefault("approved_patch_queue", [])
    if status:
        return [r for r in rows if r.get("status") == status]
    return rows

def maru_mark_patch_queue_done(mem_obj, req_id, status="패치진행중"):
    for item in mem_obj.setdefault("approved_patch_queue", []):
        if item.get("id") == req_id:
            item["status"] = status
            item["updated_at"] = maru_now_kst_text()
            save_memory(mem_obj)
            return True
    return False
# ===== /MARU V14.2 approval gate for improvement requirements =====



# ===== MARU V14.3 no-extra-approval auto patch loop =====
def maru_auto_patch_from_log_hints(mem_obj, project_label, hints):
    """
    승인된 개선요구 이후에는 패치마다 추가 승인 없이 자동 패치 후보를 적용하는 루프용.
    현재는 안전 패치만 수행:
    - 누락 README/requirements 생성
    - ai_memory.json 기본 구조 보정
    - app.py 문법 실패 시 자동수정 대신 로그 기록 후 재패치 필요 표시
    """
    info, msg = maru_get_project_info_from_choice(mem_obj, project_label)
    if not info:
        return {"ok": False, "patched": [], "message": msg}
    src = Path(info.get("src", ""))
    patched = []

    # 안전 보정 1: requirements.txt 없으면 기본값 생성
    req = src / "requirements.txt"
    if not req.exists():
        req.write_text("streamlit\npandas\nnumpy\nrequests\n", encoding="utf-8")
        patched.append("requirements.txt 기본 생성")

    # 안전 보정 2: README.md 없으면 생성
    readme = src / "README.md"
    if not readme.exists():
        readme.write_text(f"# {info.get('name', project_label)}\n\nMARU 자동 보관소 프로젝트입니다.\n", encoding="utf-8")
        patched.append("README.md 기본 생성")

    # 안전 보정 3: ai_memory.json 없으면 생성
    memfile = src / "ai_memory.json"
    if not memfile.exists():
        memfile.write_text(json.dumps({"version": "auto-created", "project": info.get("name", project_label)}, ensure_ascii=False, indent=2), encoding="utf-8")
        patched.append("ai_memory.json 기본 생성")

    detail = " / ".join(patched) if patched else "적용 가능한 안전 자동패치 없음"
    maru_loop_event(mem_obj, info.get("name", project_label), "무승인 자동패치", "완료", detail)
    return {"ok": True, "patched": patched, "message": detail}

def maru_run_no_approval_patch_loop(mem_obj, label, repeat=3, do_github=True, github_token="", commit_msg="MARU no approval auto patch loop"):
    """
    승인된 개선요구가 있거나 사용자가 루프를 시작하면:
    패치 추가승인 없이 테스트 → 로그분석 → 안전 자동패치 → 재테스트 → 자동반영 흐름 실행
    """
    all_rows = []
    for n in range(int(repeat)):
        info, msg = maru_get_project_info_from_choice(mem_obj, label)
        if not info:
            all_rows.append({"round": n+1, "step": "보관소 불러오기", "status": "실패", "detail": msg})
            break

        project_name = info.get("name", MARU_PROJECT_PRESETS[label]["project_name"])
        src = Path(info.get("src", ""))

        all_rows.append({"round": n+1, "step": "보관소 불러오기", "status": "성공", "detail": msg})
        test_result = maru_run_basic_project_test(src)
        all_rows.append({"round": n+1, "step": "자동 테스트", "status": "성공" if test_result.get("ok") else "실패", "detail": json.dumps(test_result, ensure_ascii=False)})
        maru_loop_event(mem_obj, project_name, "자동 테스트", "성공" if test_result.get("ok") else "실패", json.dumps(test_result, ensure_ascii=False))

        hints = maru_analyze_loop_logs(test_result)
        all_rows.append({"round": n+1, "step": "로그분석", "status": "완료", "detail": " / ".join(hints)})
        maru_loop_event(mem_obj, project_name, "로그분석", "완료", " / ".join(hints))

        if not test_result.get("ok"):
            patch_result = maru_auto_patch_from_log_hints(mem_obj, label, hints)
            all_rows.append({"round": n+1, "step": "무승인 자동패치", "status": "완료" if patch_result.get("ok") else "실패", "detail": patch_result.get("message", "")})
            # 안전 자동패치가 없으면 무한 반복 방지
            if not patch_result.get("patched"):
                all_rows.append({"round": n+1, "step": "재패치 중지", "status": "수동확인필요", "detail": "자동으로 안전하게 고칠 수 없는 오류입니다. 로그를 보고 코드패치 필요"})
                break
            continue

        if test_result.get("ok") and do_github:
            gh = info.get("github", {})
            owner = gh.get("owner", "skytins3-png")
            repo = gh.get("repo", project_name)
            branch = gh.get("branch", "main")
            token = github_token or (get_github_token_from_secret() if "get_github_token_from_secret" in globals() else "")
            if not token:
                all_rows.append({"round": n+1, "step": "GitHub 자동반영", "status": "대기", "detail": "GITHUB_TOKEN 없음"})
                break
            try:
                upload_rows = gh_upload_folder(src, owner, repo, branch, token, f"{commit_msg} #{n+1}", "")
                ok_count = sum(1 for r in upload_rows if r.get("ok"))
                fail_count = sum(1 for r in upload_rows if not r.get("ok"))
                status = "성공" if fail_count == 0 else "일부실패"
                detail = f"성공 {ok_count}, 실패 {fail_count}"
                all_rows.append({"round": n+1, "step": "GitHub 자동반영", "status": status, "detail": detail})
                maru_loop_event(mem_obj, project_name, "GitHub 자동반영", status, detail)
            except Exception as e:
                all_rows.append({"round": n+1, "step": "GitHub 자동반영", "status": "실패", "detail": str(e)})
            break
        else:
            all_rows.append({"round": n+1, "step": "완료", "status": "테스트통과", "detail": "GitHub 자동반영 선택 안 함"})
            break
    save_memory(mem_obj)
    return all_rows
# ===== /MARU V14.3 no-extra-approval auto patch loop =====



# ===== MARU V15 full automation repair engine =====
def maru_read_text_safe(path):
    path = Path(path)
    for enc in ["utf-8", "utf-8-sig", "cp949", "euc-kr"]:
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(errors="ignore")

def maru_write_text_safe(path, text):
    Path(path).write_text(text, encoding="utf-8")

def maru_compile_app_file(app_file):
    try:
        py_compile.compile(str(app_file), doraise=True)
        return True, ""
    except Exception as e:
        return False, str(e)

def maru_ensure_required_files(src, project_name="MARU Project"):
    src = Path(src)
    src.mkdir(parents=True, exist_ok=True)
    patched = []
    req = src / "requirements.txt"
    if not req.exists():
        req.write_text("streamlit\npandas\nnumpy\nrequests\n", encoding="utf-8")
        patched.append("requirements.txt 생성")
    readme = src / "README.md"
    if not readme.exists():
        readme.write_text(f"# {project_name}\n\nMARU 자동화 프로젝트입니다.\n", encoding="utf-8")
        patched.append("README.md 생성")
    memfile = src / "ai_memory.json"
    if not memfile.exists():
        memfile.write_text(json.dumps({"version": "auto-created", "project": project_name}, ensure_ascii=False, indent=2), encoding="utf-8")
        patched.append("ai_memory.json 생성")
    return patched

def maru_fix_nameerror_from_log(src, error_text):
    app_file = Path(src) / "app.py"
    if not app_file.exists():
        return {"ok": False, "patched": [], "message": "app.py 없음"}
    text = maru_read_text_safe(app_file)
    original = text
    patched = []
    names = re.findall(r"name '([^']+)' is not defined", str(error_text))
    names = list(dict.fromkeys(names))
    insert = []

    if "KST" in names and "KST = timezone(timedelta(hours=9))" not in text:
        insert.append("try:\n    KST\nexcept NameError:\n    KST = timezone(timedelta(hours=9))")
        patched.append("KST 자동삽입")

    if "save_memory" in names and "def save_memory(" not in text:
        insert.append("def save_memory(mem_obj):\n    try:\n        target = globals().get('MEM', None)\n        if target is None:\n            target = Path(__file__).parent / 'ai_memory.json'\n        Path(target).write_text(json.dumps(mem_obj, ensure_ascii=False, indent=2), encoding='utf-8')\n        return True\n    except Exception:\n        return False\n")
        patched.append("save_memory 자동삽입")

    if "default_api_key_for" in names and "def default_api_key_for(" not in text:
        insert.append("def default_api_key_for(choice, mem_obj=None):\n    try:\n        if choice == '경마앱':\n            return st.secrets.get('KRA_API_KEY', st.secrets.get('PUBLIC_DATA_API_KEY', ''))\n        if choice == '토토앱':\n            return st.secrets.get('TOTO_API_KEY', st.secrets.get('SPORTMONKS_TOKEN', ''))\n    except Exception:\n        pass\n    try:\n        return mem_obj.get('default_profile', {}).get('api_key', '') if mem_obj else ''\n    except Exception:\n        return ''\n")
        patched.append("default_api_key_for 자동삽입")

    if "default_api_urls_for" in names and "def default_api_urls_for(" not in text:
        insert.append("def default_api_urls_for(choice, mem_obj=None):\n    try:\n        cur = mem_obj.get('default_profile', {}).get('api_urls', '') if mem_obj else ''\n        if cur:\n            return cur\n    except Exception:\n        pass\n    if choice == '경마앱':\n        return '\\n'.join(['https://apis.data.go.kr/B551015/API310/raceInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json','https://apis.data.go.kr/B551015/API310/entryInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json','https://apis.data.go.kr/B551015/API310/horseInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json'])\n    return ''\n")
        patched.append("default_api_urls_for 자동삽입")

    if insert:
        if "from pathlib import Path" not in text:
            insert.insert(0, "from pathlib import Path")
        if "import json" not in text:
            insert.insert(0, "import json")
        if "KST" in names:
            if "from datetime import" in text:
                def dt_repl(m):
                    parts = [p.strip() for p in m.group(1).split(",")]
                    for x in ["datetime", "timezone", "timedelta"]:
                        if x not in parts:
                            parts.append(x)
                    return "from datetime import " + ", ".join(parts)
                text = re.sub(r"from datetime import ([^\n]+)", dt_repl, text, count=1)
            else:
                insert.insert(0, "from datetime import datetime, timezone, timedelta")
        import_end = 0
        for m in re.finditer(r"^(import .+|from .+ import .+)\n", text, flags=re.M):
            import_end = max(import_end, m.end())
        text = text[:import_end] + "\n# MARU V15 auto inserted helpers\n" + "\n".join(insert) + "\n# /MARU V15 auto inserted helpers\n\n" + text[import_end:]
        try:
            app_file.with_suffix(".py.bak_nameerror_v15").write_text(original, encoding="utf-8")
        except Exception:
            pass
        maru_write_text_safe(app_file, text)

    ok, err = maru_compile_app_file(app_file)
    return {"ok": ok, "patched": patched, "message": " / ".join(patched) if patched else err}

def maru_fix_common_syntax_errors(src):
    app_file = Path(src) / "app.py"
    if not app_file.exists():
        return {"ok": False, "patched": [], "message": "app.py 없음"}
    text = maru_read_text_safe(app_file)
    original = text
    patched = []
    if "\t" in text:
        text = text.replace("\t", "    ")
        patched.append("탭 공백 변환")
    if "<<<<<<<" in text or "=======" in text or ">>>>>>>" in text:
        lines, skip = [], False
        for line in text.splitlines():
            if line.startswith("<<<<<<<"):
                skip = True
                patched.append("Git 충돌 마커 제거")
                continue
            if line.startswith("======="):
                skip = False
                continue
            if line.startswith(">>>>>>>"):
                continue
            if not skip:
                lines.append(line)
        text = "\n".join(lines) + "\n"

    lines = text.splitlines()
    new_lines, changed = [], False
    for i, line in enumerate(lines):
        new_lines.append(line)
        stripped = line.strip()
        if not stripped or not stripped.endswith(":"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines):
            new_lines.append(" " * (indent + 4) + "pass")
            changed = True
        else:
            next_indent = len(lines[j]) - len(lines[j].lstrip(" "))
            if next_indent <= indent and not lines[j].strip().startswith(("#", "elif", "else", "except", "finally")):
                new_lines.append(" " * (indent + 4) + "pass")
                changed = True
    if changed:
        text = "\n".join(new_lines) + "\n"
        patched.append("빈 블록 pass 추가")

    if text != original:
        try:
            app_file.with_suffix(".py.bak_syntax_v15").write_text(original, encoding="utf-8")
        except Exception:
            pass
        maru_write_text_safe(app_file, text)

    ok, err = maru_compile_app_file(app_file)
    return {"ok": ok, "patched": patched, "message": " / ".join(patched) if patched else err}

def maru_full_auto_repair_once(mem_obj, label):
    info, msg = maru_get_project_info_from_choice(mem_obj, label)
    if not info:
        return [{"step": "보관소 불러오기", "status": "실패", "detail": msg}]
    project_name = info.get("name", MARU_PROJECT_PRESETS[label]["project_name"])
    src = Path(info.get("src", ""))
    rows = [{"step": "보관소 불러오기", "status": "성공", "detail": msg}]
    file_patches = maru_ensure_required_files(src, project_name)
    if file_patches:
        rows.append({"step": "누락파일 보정", "status": "완료", "detail": " / ".join(file_patches)})
    test_result = maru_run_basic_project_test(src)
    rows.append({"step": "자동 테스트", "status": "성공" if test_result.get("ok") else "실패", "detail": json.dumps(test_result, ensure_ascii=False)})
    if test_result.get("ok"):
        rows.append({"step": "자동수정", "status": "불필요", "detail": "테스트 통과"})
        return rows
    detail = json.dumps(test_result, ensure_ascii=False)
    namefix = maru_fix_nameerror_from_log(src, detail)
    if namefix.get("patched"):
        rows.append({"step": "NameError 자동수정", "status": "완료", "detail": namefix.get("message", "")})
    syntaxfix = maru_fix_common_syntax_errors(src)
    if syntaxfix.get("patched"):
        rows.append({"step": "문법오류 자동수정", "status": "완료", "detail": syntaxfix.get("message", "")})
    elif not syntaxfix.get("ok"):
        rows.append({"step": "문법오류 자동수정", "status": "보류", "detail": syntaxfix.get("message", "")})
    retest = maru_run_basic_project_test(src)
    rows.append({"step": "재테스트", "status": "성공" if retest.get("ok") else "실패", "detail": json.dumps(retest, ensure_ascii=False)})
    return rows

def maru_full_auto_loop(mem_obj, label, repeat=5, do_github=True, github_token="", commit_msg="MARU full auto repair"):
    all_rows = []
    final_ok = False
    for n in range(int(repeat)):
        rows = maru_full_auto_repair_once(mem_obj, label)
        for r in rows:
            r["round"] = n + 1
            all_rows.append(r)
        if rows and rows[-1].get("status") in ["성공", "불필요"]:
            final_ok = True
            break
        applied = any(r.get("status") == "완료" and ("자동수정" in r.get("step","") or r.get("step") == "누락파일 보정") for r in rows)
        if not applied:
            break
    info, msg = maru_get_project_info_from_choice(mem_obj, label)
    if final_ok and do_github and info:
        project_name = info.get("name", MARU_PROJECT_PRESETS[label]["project_name"])
        src = Path(info.get("src", ""))
        gh = info.get("github", {})
        owner = gh.get("owner", "skytins3-png")
        repo = gh.get("repo", project_name)
        branch = gh.get("branch", "main")
        token = github_token or (get_github_token_from_secret() if "get_github_token_from_secret" in globals() else "")
        if not token:
            all_rows.append({"round": "final", "step": "GitHub 자동반영", "status": "대기", "detail": "GITHUB_TOKEN 없음"})
        else:
            try:
                upload_rows = gh_upload_folder(src, owner, repo, branch, token, commit_msg, "")
                ok_count = sum(1 for r in upload_rows if r.get("ok"))
                fail_count = sum(1 for r in upload_rows if not r.get("ok"))
                all_rows.append({"round": "final", "step": "GitHub 자동반영", "status": "성공" if fail_count == 0 else "일부실패", "detail": f"성공 {ok_count}, 실패 {fail_count}"})
            except Exception as e:
                all_rows.append({"round": "final", "step": "GitHub 자동반영", "status": "실패", "detail": str(e)})
    elif not final_ok:
        all_rows.append({"round": "final", "step": "풀자동화 종료", "status": "수동확인필요", "detail": "안전 자동수정 범위를 넘어선 오류입니다. 로그 기반 코드패치 필요"})
    return all_rows
# ===== /MARU V15 full automation repair engine =====

tabs = st.tabs(["📋 기능",
    "📦 보관소",
    "🔁 연속자동화", "🤖 코드생성", "📁 등록", "📡 테스트", "🧯 로그분석", "🖼️ 사진분석/명령", "✅ 패치", "🔍 검사", "📦 버전", "🚀 GitHub 자동반영", "☁️ 구글시트", "📚 기록"    "📝 개선승인",
    "♻️ 무승인패치루프",
    "🤖 풀자동화",
])

with tabs[0]:
    st.write(FEATURES)
    st.warning("GitHub 자동반영은 GitHub 토큰이 필요합니다. 토큰은 공개 저장소에 절대 올리지 마세요.")
    st.divider()
    st.subheader("⚙️ 기본설정 자동불러오기")
    st.caption("경마앱/토토앱/AI 코드 생성기를 선택하면 프로젝트 이름, 앱 주소, GitHub repo가 자동으로 바뀝니다.")
    preset_choice = st.selectbox("프로젝트 선택", ["경마앱", "토토앱", "AI 코드 생성기", "직접입력"], key="default_project_choice")
    prof = maru_profile_from_choice(preset_choice, m)
    st.info(f"현재 선택: {preset_choice} → {prof.get('project_name','') or '직접입력'}")
    c1, c2 = st.columns(2)
    with c1:
        p_name = st.text_input("기본 프로젝트 이름", value=prof.get("project_name", "maru-kra-final-clean"), key=f"default_project_name_{preset_choice}")
        p_url = st.text_input("기본 배포 앱 주소", value=prof.get("app_url", "https://maru-kra-final-clean.streamlit.app"), key=f"default_app_url_{preset_choice}")
        auto_api_key = maru_api_key_for(preset_choice, m)
        p_api_key = st.text_input("기본 API KEY/TOKEN", value=auto_api_key, type="password", key=f"default_api_key_{preset_choice}", placeholder="Secrets에 있으면 자동 입력")
    with c2:
        p_owner = st.text_input("기본 GitHub owner", value=prof.get("github_owner", "skytins3-png"), key=f"default_gh_owner_{preset_choice}")
        p_repo = st.text_input("기본 GitHub repo", value=prof.get("github_repo", "maru-kra-final-clean"), key=f"default_gh_repo_{preset_choice}")
        p_branch = st.text_input("기본 branch", value=prof.get("github_branch", "main"), key=f"default_gh_branch_{preset_choice}")
    p_api_urls = st.text_area("기본 API URL 목록", value=maru_api_urls_for(preset_choice, m), height=120, key=f"default_api_urls_{preset_choice}")
    secret_token = maru_github_token()
    if secret_token:
        st.success("Streamlit Secrets의 GITHUB_TOKEN 감지: GitHub 자동반영 탭에서 자동 사용됩니다.")
    else:
        st.info("토큰 반복 입력이 불편하면 Streamlit Secrets에 GITHUB_TOKEN으로 저장하세요. 파일에는 저장하지 않습니다.")
    if st.button("기본설정 저장", type="primary", width="stretch"):
        set_default_profile(m, {"project_name": p_name.strip(), "app_url": p_url.strip(), "api_key": p_api_key, "api_urls": p_api_urls, "github_owner": p_owner.strip() or "skytins3-png", "github_repo": p_repo.strip() or p_name.strip(), "github_branch": p_branch.strip() or "main"})
        st.success("기본설정 저장 완료")
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("경마앱 기본값", width="stretch"):
            set_default_profile(m, {"project_name":"maru-kra-final-clean","app_url":"https://maru-kra-final-clean.streamlit.app","api_key":prof.get("api_key", ""),"api_urls":prof.get("api_urls", ""),"github_owner":"skytins3-png","github_repo":"maru-kra-final-clean","github_branch":"main"})
            st.rerun()
    with q2:
        if st.button("코드생성기 기본값", width="stretch"):
            set_default_profile(m, {"project_name":"maru-ai-code-maker","app_url":"https://maru-ai-code-maker.streamlit.app","api_key":"","api_urls":"","github_owner":"skytins3-png","github_repo":"maru-ai-code-maker","github_branch":"main"})
            st.rerun()
    with q3:
        if st.button("토토앱 기본값", width="stretch"):
            set_default_profile(m, {"project_name":"skytoto-ai-hub","app_url":"","api_key":prof.get("api_key", ""),"api_urls":prof.get("api_urls", ""),"github_owner":"skytins3-png","github_repo":"skytoto-ai-hub","github_branch":"main"})
            st.rerun()



with tabs[1]:
    st.subheader("📦 프로젝트 보관소")
    st.caption("최신파일을 한 번 저장해두면 다음부터는 등록 없이 프로젝트 클릭으로 불러와 패치/업그레이드/자동반영합니다.")

    vault_choice = st.selectbox("보관소 프로젝트 선택", ["경마앱", "토토앱", "AI 코드 생성기"], key="vault_choice")
    meta = maru_read_vault_meta(vault_choice)
    src = maru_vault_src_dir(vault_choice)
    has_app = (src / "app.py").exists()

    c1, c2 = st.columns(2)
    with c1:
        st.metric("보관 상태", "저장됨" if has_app else "비어 있음")
        st.write("프로젝트:", MARU_PROJECT_PRESETS[vault_choice]["project_name"])
        st.write("GitHub repo:", MARU_PROJECT_PRESETS[vault_choice]["github_repo"])
    with c2:
        st.write("마지막 저장:", meta.get("updated_at", "-"))
        st.write("파일:", meta.get("filename", "-"))

    if st.button("이 프로젝트 최신파일 불러오기", type="primary", width="stretch"):
        ok, msg = maru_load_project_from_vault(m, vault_choice)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

    st.divider()
    st.markdown("### 최초 1회 또는 새 버전 저장")
    st.info("여기에 한 번 저장하면 이후에는 📁 등록을 반복하지 않아도 됩니다.")
    vault_upload = st.file_uploader("보관소에 저장할 ZIP 또는 app.py", type=["zip", "py"], key="vault_upload")
    try:
        auto_key = default_api_key_for(vault_choice, m)
    except Exception:
        auto_key = ""
    try:
        auto_urls = default_api_urls_for(vault_choice, m)
    except Exception:
        auto_urls = ""
    vault_api_key = st.text_input("API KEY/TOKEN 자동 저장값", value=auto_key, type="password", key="vault_api_key")
    vault_api_urls = st.text_area("API URL 목록 저장값", value=auto_urls, height=120, key="vault_api_urls")

    if st.button("보관소에 저장하고 바로 불러오기", width="stretch"):
        if not vault_upload:
            st.error("ZIP 또는 app.py를 선택하세요. 이건 최초 1회 보관용입니다.")
        else:
            src, meta = maru_save_upload_to_vault(vault_choice, vault_upload, vault_api_key, vault_api_urls)
            ok, msg = maru_load_project_from_vault(m, vault_choice)
            if ok:
                st.success("보관소 저장 완료 + 프로젝트 자동 선택 완료")
                st.write(str(src))
            else:
                st.error(msg)



with tabs[2]:
    st.subheader("🔁 패치-반영-테스트-로그분석 연속자동화")
    st.caption("보관소 최신파일 기준으로 프로젝트 선택 → 테스트 → 로그분석 → GitHub 자동반영까지 한 흐름으로 연결합니다.")

    loop_choice = st.selectbox("연속자동화 프로젝트", ["경마앱", "토토앱", "AI 코드 생성기"], key="loop_choice")
    loop_repeat = st.number_input("반복 횟수", min_value=1, max_value=5, value=1, step=1, key="loop_repeat")
    loop_github = st.checkbox("테스트 통과 시 GitHub 자동반영까지 실행", value=True, key="loop_github")
    try:
        loop_token = get_github_token_from_secret()
    except Exception:
        loop_token = ""
    if loop_token:
        st.success("GITHUB_TOKEN 감지됨: 자동반영 때 토큰 재입력 안 해도 됩니다.")
    else:
        st.warning("GITHUB_TOKEN이 없으면 GitHub 자동반영은 대기 상태가 됩니다.")
    commit_msg = st.text_input("자동 커밋 메시지", value="MARU continuous loop auto update", key="loop_commit_msg")

    if st.button("연속자동화 시작", type="primary", width="stretch"):
        all_rows = []
        for n in range(int(loop_repeat)):
            rows = maru_run_continuous_loop_once(
                m,
                loop_choice,
                do_github=loop_github,
                github_token=loop_token,
                commit_msg=f"{commit_msg} #{n+1}",
            )
            for r in rows:
                r["round"] = n + 1
                all_rows.append(r)
            # 테스트 실패면 무한 반복하지 않고 멈춤
            if any(r.get("step") == "재패치 대기" and r.get("status") == "필요" for r in rows):
                break
        st.dataframe(all_rows, width="stretch")
        st.info("테스트 실패가 나오면 로그분석 힌트를 패치 탭으로 넘겨 다시 패치한 뒤, 같은 루프를 재실행하는 구조입니다.")

    st.divider()
    st.markdown("### 최근 연속자동화 기록")
    hist = m.get("continuous_loop_history", [])[-30:]
    if hist:
        st.dataframe(hist, width="stretch")
    else:
        st.caption("아직 연속자동화 기록이 없습니다.")

with tabs[3]:
    st.subheader("진화형 AI 코드 생성기 + 자동 허브 업로드")
    st.caption("목표를 입력하면 Streamlit 앱을 생성하고, 검사 후 GitHub 허브 저장소로 자동 업로드할 수 있습니다.")
    gen_name = st.text_input("생성 프로젝트 이름", placeholder="maru-new-app")
    gen_kind = st.selectbox("앱 종류", ["기본앱", "경마 분석앱 뼈대", "토토/스포츠 분석앱 뼈대", "API 대시보드", "기록/허브앱"])
    gen_goal = st.text_area("앱 목표 / 필요한 기능", height=150, placeholder="예: 경마 API를 점검하고 오류 로그를 저장하는 모바일용 대시보드")
    gen_repo = st.text_input("생성 결과를 올릴 GitHub repo 이름", placeholder="maru-new-app")
    if st.button("코드 생성 + 자동검사", type="primary", width="stretch"):
        pname = infer_project_name(gen_name, "", None)
        src = generate_streamlit_project(pname, gen_goal, gen_kind)
        info = register_generated_project(m, pname, src, github_repo=(gen_repo.strip() or pname))
        st.success(f"생성/검사 완료: {pname}")
        st.json(info["scan"])
        st.json(info["analysis"])
        st.download_button("생성 앱 ZIP 다운로드", zip_bytes(src), f"{sname(pname)}_GENERATED.zip", "application/zip", width="stretch")

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
            prof = maru_get_default_profile(m)
            hub_owner = st.text_input("허브 GitHub owner", value=gh.get("owner", prof.get("github_owner", "skytins3-png")), key="hub_owner_codegen")
            hub_repo = st.text_input("허브 대상 repo", value=gh.get("repo", prof.get("github_repo", hub_project)), key="hub_repo_codegen")
            hub_branch = st.text_input("branch", value=gh.get("branch", prof.get("github_branch", "main")), key="hub_branch_codegen")
        with c2:
            hub_token = st.text_input("GitHub 토큰", value=maru_github_token(), type="password", key="hub_token_codegen")
            hub_msg = st.text_input("커밋 메시지", value=f"MARU generated code hub upload {datetime.now().strftime('%Y-%m-%d %H:%M')}", key="hub_msg_codegen")
            st.warning("토큰은 저장하지 않습니다. 채팅창/README/GitHub 파일에 붙이지 마세요.")
        if st.button("생성 앱 GitHub 허브에 자동 업로드/커밋", type="primary", width="stretch"):
            if not hub_token:
                st.error("GitHub 토큰이 없습니다. Streamlit Secrets에 GITHUB_TOKEN을 저장하면 모바일에서 입력하지 않아도 됩니다.")
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

with tabs[4]:
    st.subheader("프로젝트 등록")
    reg_choice = st.selectbox("프로젝트 선택", ["경마앱", "토토앱", "AI 코드 생성기", "직접입력"], key="reg_project_choice")
    prof = maru_profile_from_choice(reg_choice, m)
    st.info(f"{reg_choice} 선택됨: 프로젝트/주소/repo 자동 적용")
    name = st.text_input("프로젝트 이름", value=prof.get("project_name", "maru-kra-final-clean"), placeholder="maru-kra-final-clean", key=f"maru_project_name_{reg_choice}")
    app_url = st.text_input("배포 앱 주소", value=prof.get("app_url", "https://maru-kra-final-clean.streamlit.app"), placeholder="https://maru-kra-final-clean.streamlit.app", key=f"maru_app_url_{reg_choice}")
    auto_api_key = maru_api_key_for(reg_choice, m)
    api_key = st.text_input("API KEY/TOKEN 자동값", value=auto_api_key, type="password", key=f"reg_api_key_{reg_choice}", placeholder="Secrets/기본설정에서 자동")
    api_urls = st.text_area("API URL 목록 - 한 줄에 하나", value=maru_api_urls_for(reg_choice, m), key=f"reg_api_urls_{reg_choice}")
    up = st.file_uploader("ZIP 또는 app.py", type=["zip","py"])
    if st.button("저장 + 자동검사", type="primary", width="stretch"):
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
            m["default_profile"] = {"project_name": pname, "app_url": app_url.strip() or old.get("app_url", ""), "api_key": api_key or old.get("api_key", ""), "api_urls": "\n".join(info.get("api_urls", [])), "github_owner": m.get("default_profile", {}).get("github_owner", "skytins3-png"), "github_repo": m.get("default_profile", {}).get("github_repo", pname), "github_branch": m.get("default_profile", {}).get("github_branch", "main")}
            m.setdefault("saved_profiles", {})[pname] = m["default_profile"]
            m["file_checks"].append({"time": datetime.now().isoformat(timespec="seconds"), "project": pname, "scan": info["scan"]})
            save_event(m, "projects", {"type":"project_register","project":pname,"status":"SAVED","summary":"프로젝트 등록/검사"})
            save(m)
            st.success(f"등록/검사 완료: {pname}")
            st.json(info["scan"]); st.json(info["analysis"])

with tabs[9]:
    ps = list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel = st.selectbox("프로젝트", ps, key="scan")
        info = m["projects"][sel]; src = Path(info["src"])
        if st.button("다시 검사", type="primary", width="stretch"):
            app_path = find_app(src)
            info.update({"scan": scan(src), "syntax": syntax_all(src), "errors": inspect_error_files(src), "analysis": analyze_app(app_path)})
            save(m); st.success("검사 완료")
        st.subheader("파일 목록"); st.json(info.get("scan", {}))
        st.subheader("문법 검사"); st.json(info.get("syntax", []))
        st.subheader("오류 파일"); st.json(info.get("errors", []))
        st.subheader("기능 분석"); st.json(info.get("analysis", {}))

with tabs[5]:
    ps = list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel = st.selectbox("프로젝트", ps, key="test")
        cnt = st.number_input("반복 횟수", 1, 20, 1)
        if st.button("자동/반복 테스트", type="primary", width="stretch"):
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
        st.download_button("PC 꺼져도 테스트용 maru_auto_test.yml", workflow(info.get("app_url",""), info.get("api_urls",[])).encode(), "maru_auto_test.yml", "text/yaml", width="stretch")

with tabs[6]:
    st.subheader("로그파일 / 오류 로그 분석")
    st.caption("Streamlit Cloud 로그를 복사해 붙여넣거나 log/txt/json 파일을 업로드하면 오류 패턴을 분석하고 필요한 패치를 추천합니다.")
    ps = list(m["projects"].keys())
    if not ps:
        st.info("먼저 프로젝트를 등록하세요.")
    else:
        sel = st.selectbox("로그 분석 대상 프로젝트", ps, key="log_project")
        pasted_log = st.text_area("로그 붙여넣기", height=220, placeholder="Streamlit Cloud 로그, Traceback, HTTP 오류, NameError 등을 여기에 붙여넣으세요.")
        log_file = st.file_uploader("로그파일 업로드", type=["txt", "log", "json", "csv"], key="manual_log_upload")
        if st.button("로그 분석 + 패치 추천 저장", type="primary", width="stretch"):
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

with tabs[7]:
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
        if st.button("사진 저장 + 명령 분석 + 패치 추천 저장", type="primary", width="stretch"):
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

with tabs[8]:
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
        if st.button("승인 항목 실제 패치 → 새 ZIP 생성", type="primary", width="stretch"):
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
            with open(zp,"rb") as f: st.download_button("패치 ZIP 다운로드", f, file_name=zp.name, mime="application/zip", width="stretch")

with tabs[11]:
    gh_choice = st.selectbox("자동반영 대상 선택", ["경마앱", "토토앱", "AI 코드 생성기", "등록된 프로젝트"], key="gh_target_choice")
    ps=list(m["projects"].keys())
    if gh_choice == "등록된 프로젝트":
        if not ps:
            st.info("등록 먼저")
            st.stop()
        sel=st.selectbox("프로젝트", ps, key="gh")
        info=m["projects"][sel]; old=info.get("github",{})
    else:
        prof_choice = maru_profile_from_choice(gh_choice, m)
        sel = prof_choice.get("project_name", gh_choice)
        if sel in m.get("projects", {}):
            info=m["projects"][sel]; old=info.get("github",{})
        else:
            info={"src": "", "github": prof_choice}; old=prof_choice
            st.info("아직 등록되지 않은 대상입니다. 먼저 📁 등록에서 ZIP/app.py를 등록하면 자동반영할 수 있습니다.")
        c1,c2=st.columns(2)
        with c1:
            prof = maru_get_default_profile(m)
            owner=st.text_input("GitHub owner", old.get("owner", prof.get("github_owner","skytins3-png")))
            repo=st.text_input("대상 repo", old.get("repo", prof.get("github_repo", sel)))
            branch=st.text_input("branch", old.get("branch", prof.get("github_branch","main")))
            prefix=st.text_input("업로드 폴더 prefix", old.get("prefix",""), placeholder="비우면 루트")
        with c2:
            token=st.text_input("GitHub 토큰", value=maru_github_token(), type="password")
            msg=st.text_input("커밋 메시지", f"MARU auto patch deploy {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            savecfg=st.checkbox("토큰 제외 설정 저장", value=True)
            st.warning("토큰은 파일에 저장하지 않습니다. 반복 입력이 불편하면 Streamlit Secrets에 GITHUB_TOKEN으로 저장하세요.")
            st.info(".github/workflows 폴더는 GitHub 보안권한 문제 방지를 위해 자동 업로드에서 제외합니다. 파일이 없어서 404가 나오는 경우는 새 파일 생성으로 처리합니다.")
        if st.button("연결 확인", width="stretch"):
            if not token: st.error("토큰 필요")
            else:
                code,data=gh_repo(owner,repo,token)
                st.success("연결 성공") if code==200 else st.error(f"실패 HTTP {code}")
                st.json(data)
        if st.button("대상 GitHub 저장소에 자동 업로드/커밋", type="primary", width="stretch"):
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

with tabs[10]:
    ps=list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트", ps, key="ver")
        info=m["projects"][sel]; src=Path(info["src"])
        st.metric("현재 버전", info.get("version",0))
        st.download_button("현재 보관본 ZIP", zip_bytes(src), f"{sname(sel)}_CURRENT.zip", "application/zip", width="stretch")
        app_path=Path(info.get("app_file","")) if info.get("app_file") else find_app(src)
        if app_path and app_path.exists():
            st.download_button("단일 app.py", read(app_path).encode(), f"{sname(sel)}_app.py", "text/x-python", width="stretch")


with tabs[12]:
    st.subheader("구글시트 허브 저장")
    st.caption("프로젝트, 테스트, 패치, GitHub 자동반영, 코드생성 허브 업로드 기록을 Google Sheets에 저장합니다.")
    cfg = get_gsheet_config(m)
    enabled = st.checkbox("구글시트 저장 사용", value=bool(cfg.get("enabled")))
    sheet_id = st.text_input("Google Sheet ID", value=cfg.get("sheet_id", ""))
    service_json = st.text_area("서비스계정 JSON", value=cfg.get("service_account_json", ""), height=180)
    st.info("서비스계정 JSON 안의 client_email을 Google Sheet 편집자로 공유해야 연결됩니다.")
    if st.button("구글시트 설정 저장", type="primary", width="stretch"):
        cfg.update({"enabled": enabled, "sheet_id": sheet_id.strip(), "service_account_json": service_json.strip()})
        m["google_sheets"] = cfg
        save(m)
        st.success("구글시트 설정 저장 완료")
    if st.button("연결 테스트", width="stretch"):
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

with tabs[13]:
    st.subheader("GitHub 자동반영 기록"); st.json(m.get("github_deploys", [])[-20:])
    st.subheader("코드생성 허브 업로드 기록"); st.json(m.get("hub_uploads", [])[-20:])
    st.subheader("패치 기록"); st.json(m.get("patch_records", [])[-20:])
    st.subheader("테스트 기록"); st.json(m.get("test_records", [])[-20:])
    st.subheader("로그 분석 기록"); st.json(m.get("log_analyses", [])[-20:])
    st.subheader("사진/명령 분석 기록"); st.json(m.get("image_analyses", [])[-20:])
    st.subheader("학습"); st.json(m.get("lessons", [])[-50:])


with tabs[-1]:
    st.subheader("📝 개선 요구사항 승인 후 진행")
    st.caption("개선 요구사항은 바로 패치하지 않고 승인대기 → 승인 → 패치대기 → 반영/테스트 순서로 진행합니다.")

    c1, c2 = st.columns([1, 1])
    with c1:
        req_project = st.selectbox("대상 프로젝트", ["경마앱", "토토앱", "AI 코드 생성기", "직접입력"], key="approval_project")
        req_priority = st.selectbox("우선순위", ["낮음", "보통", "높음", "긴급"], index=1, key="approval_priority")
        req_title = st.text_input("개선 제목", placeholder="예: 보관소 선택 후 자동 테스트까지 연결", key="approval_title")
    with c2:
        req_detail = st.text_area("개선 상세", placeholder="원하는 개선 내용을 적으면 승인대기함에 저장됩니다.", height=160, key="approval_detail")

    if st.button("개선 요구사항 승인대기 등록", type="primary", width="stretch"):
        if not req_title.strip() or not req_detail.strip():
            st.error("개선 제목과 상세 내용을 입력하세요.")
        else:
            item = maru_add_improvement_request(m, req_project, req_title, req_detail, req_priority)
            st.success("승인대기 등록 완료")
            st.json(item)

    st.divider()
    st.markdown("### 승인대기 목록")
    pending = maru_get_improvement_requests(m, "승인대기")
    if pending:
        for item in pending:
            with st.expander(f"{item.get('priority','보통')} · {item.get('project','')} · {item.get('title','')}"):
                st.write(item.get("detail", ""))
                note = st.text_input("결정 메모", key=f"note_{item['id']}")
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("승인", key=f"approve_{item['id']}", width="stretch"):
                        ok, updated = maru_decide_improvement_request(m, item["id"], "승인", note)
                        if ok:
                            st.success("승인 완료 → 패치대기열로 이동")
                            st.rerun()
                with b2:
                    if st.button("보류", key=f"hold_{item['id']}", width="stretch"):
                        ok, updated = maru_decide_improvement_request(m, item["id"], "보류", note)
                        if ok:
                            st.warning("보류 처리")
                            st.rerun()
                with b3:
                    if st.button("거절", key=f"reject_{item['id']}", width="stretch"):
                        ok, updated = maru_decide_improvement_request(m, item["id"], "거절", note)
                        if ok:
                            st.error("거절 처리")
                            st.rerun()
    else:
        st.caption("승인대기 중인 개선 요구사항이 없습니다.")

    st.divider()
    st.markdown("### 승인된 패치 대기열")
    queue = maru_get_approved_patch_queue(m)
    if queue:
        st.dataframe(queue, width="stretch")
        patch_ids = [q["id"] for q in queue if q.get("status") == "패치대기"]
        if patch_ids:
            selected_patch_id = st.selectbox("패치 진행할 승인 항목", patch_ids, key="selected_approved_patch")
            if st.button("선택 항목 패치진행중으로 표시", width="stretch"):
                maru_mark_patch_queue_done(m, selected_patch_id, "패치진행중")
                st.success("패치진행중으로 변경했습니다. 패치 탭에서 이 요구사항 기준으로 작업하세요.")
                st.rerun()
    else:
        st.caption("승인된 패치 대기열이 없습니다.")

    st.divider()
    st.markdown("### 전체 개선 요구사항 기록")
    all_reqs = maru_get_improvement_requests(m)
    if all_reqs:
        st.dataframe(all_reqs, width="stretch")
    else:
        st.caption("기록 없음")


with tabs[-1]:
    st.subheader("♻️ 승인 후 무승인 패치 연속 루프")
    st.caption("개선 요구사항 승인 후에는 패치마다 다시 승인 묻지 않고 테스트 → 로그분석 → 자동패치 → 재테스트 → 반영으로 이어갑니다.")

    auto_project = st.selectbox("자동패치 루프 프로젝트", ["경마앱", "토토앱", "AI 코드 생성기"], key="auto_patch_loop_project")
    auto_repeat = st.number_input("최대 반복 횟수", min_value=1, max_value=10, value=3, step=1, key="auto_patch_repeat")
    auto_github = st.checkbox("테스트 통과 시 GitHub 자동반영", value=True, key="auto_patch_github")
    try:
        auto_token = get_github_token_from_secret()
    except Exception:
        auto_token = ""
    if auto_token:
        st.success("GITHUB_TOKEN 감지됨: 반영 때 토큰 입력 없이 진행")
    else:
        st.warning("GITHUB_TOKEN 없음: 자동반영은 대기 상태가 됩니다.")
    auto_msg = st.text_input("커밋 메시지", value="MARU auto patch loop update", key="auto_patch_commit_msg")

    st.info("안전 자동패치 범위: requirements.txt / README.md / ai_memory.json 누락 보정, 기본 구조 보정. 위험한 코드 수정은 로그 기록 후 재패치 필요로 멈춥니다.")

    if st.button("무승인 패치 루프 시작", type="primary", width="stretch"):
        rows = maru_run_no_approval_patch_loop(
            m,
            auto_project,
            repeat=int(auto_repeat),
            do_github=auto_github,
            github_token=auto_token,
            commit_msg=auto_msg,
        )
        st.dataframe(rows, width="stretch")

    st.divider()
    st.markdown("### 승인된 요구사항 + 무승인 루프 연결")
    queue = maru_get_approved_patch_queue(m) if "maru_get_approved_patch_queue" in globals() else []
    ready = [q for q in queue if q.get("status") in ["패치대기", "패치진행중"]]
    if ready:
        st.dataframe(ready, width="stretch")
        st.caption("위 승인 항목들은 추가 승인 없이 패치 루프에 태울 수 있습니다.")
    else:
        st.caption("승인된 패치 대기 항목이 없습니다.")


with tabs[-1]:
    st.subheader("🤖 풀자동화: 자동수정 → 재테스트 → 자동반영")
    st.caption("보관소 최신파일 기준으로 문법오류/NameError/누락파일을 안전 범위에서 자동수정하고, 재테스트 후 GitHub 자동반영까지 진행합니다.")
    fa_project = st.selectbox("풀자동화 프로젝트", ["경마앱", "토토앱", "AI 코드 생성기"], key="full_auto_project")
    fa_repeat = st.number_input("최대 자동수정 반복 횟수", min_value=1, max_value=10, value=5, step=1, key="full_auto_repeat")
    fa_github = st.checkbox("통과 시 GitHub 자동반영", value=True, key="full_auto_github")
    try:
        fa_token = get_github_token_from_secret()
    except Exception:
        fa_token = ""
    if fa_token:
        st.success("GITHUB_TOKEN 감지됨: 통과 시 자동반영 가능")
    else:
        st.warning("GITHUB_TOKEN 없음: 자동반영은 대기 상태가 됩니다.")
    fa_msg = st.text_input("커밋 메시지", value="MARU full auto repair update", key="full_auto_commit_msg")
    st.info("자동수정 범위: 누락파일 생성, NameError helper 삽입, KST/save_memory/default_api 함수 보정, 안전한 문법오류 보정, 재테스트 반복. 위험한 코드 추정 수정은 멈추고 로그를 남깁니다.")
    if st.button("풀자동화 시작", type="primary", width="stretch"):
        rows = maru_full_auto_loop(m, fa_project, repeat=int(fa_repeat), do_github=fa_github, github_token=fa_token, commit_msg=fa_msg)
        st.dataframe(rows, width="stretch")
        if rows and rows[-1].get("step") == "GitHub 자동반영":
            st.success("풀자동화 루프 완료")
        elif rows and rows[-1].get("status") == "수동확인필요":
            st.warning("자동수정 안전범위를 넘어선 오류입니다. 로그분석 결과를 패치 탭에 넘겨야 합니다.")
    st.divider()
    st.markdown("### 풀자동화 원칙")
    st.write("- 개선 요구사항은 최초 승인 후 진행")
    st.write("- 승인 후에는 패치마다 추가 승인 없이 자동수정/재테스트")
    st.write("- 자동구매/자동결제는 계속 차단")
    st.write("- 위험한 코드 추정 수정은 무리하게 밀어붙이지 않고 멈춤")

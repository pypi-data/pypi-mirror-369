import json
import os
import platform
from datetime import datetime
from typing import Optional, Tuple
from base64 import b64decode

try:
    from nacl.signing import VerifyKey  # type: ignore
    from nacl.exceptions import BadSignatureError  # type: ignore
except Exception:  # pragma: no cover
    VerifyKey = None  # type: ignore
    BadSignatureError = Exception  # type: ignore


APP_NAME = "cameleon_dp"


def _config_dir() -> str:
    try:
        if platform.system().lower().startswith("win"):
            base = os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
            return os.path.join(base, APP_NAME)
        # Linux/macOS
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
        return os.path.join(base, APP_NAME)
    except Exception:
        return os.path.expanduser(f"~/.{APP_NAME}")


def _license_path() -> str:
    return os.path.join(_config_dir(), "license.json")


def _parse_key(key: str) -> Tuple[bool, Optional[str]]:
    """Validate a signed license key.

    Expected JSON, base64-encoded, with fields:
      {"tier":"PRO|ENT","expires":"YYYYMMDD","name":"...","sig":"<base64>"}
    The signature is Ed25519 over the canonical bytes of {tier,expires,name} JSON
    using the vendor public key (env CAMELEON_PUBKEY_B64). Fallback: accept legacy
    CAMELEON-PRO-YYYYMMDD-NAME format without signature (not recommended).
    """
    # Ed25519 path
    try:
        pub_b64 = os.environ.get("CAMELEON_PUBKEY_B64")
        if pub_b64 and VerifyKey is not None:
            data = json.loads(b64decode(key).decode("utf-8"))
            tier = data.get("tier"); exp = data.get("expires"); name = data.get("name"); sig_b64 = data.get("sig")
            if tier not in ("PRO", "ENT"):
                return False, "invalid_tier"
            datetime.strptime(exp, "%Y%m%d")
            payload = json.dumps({"tier": tier, "expires": exp, "name": name}, separators=(",", ":")).encode("utf-8")
            sig = b64decode(sig_b64)
            vk = VerifyKey(b64decode(pub_b64))
            vk.verify(payload, sig)
            return True, None
    except BadSignatureError:
        return False, "bad_signature"
    except Exception:
        pass
    # Legacy fallback (non-crypto)
    try:
        parts = key.strip().split("-")
        if len(parts) < 4:
            return False, "invalid_format"
        if parts[0] != "CAMELEON" or parts[1] not in ("PRO", "ENT"):
            return False, "invalid_tier"
        expiry = parts[2]
        datetime.strptime(expiry, "%Y%m%d")
        return True, None
    except Exception:
        return False, "invalid_key"


def activate_license(key: str) -> dict:
    ok, err = _parse_key(key)
    if not ok:
        return {"ok": False, "error": f"{err}"}
    os.makedirs(_config_dir(), exist_ok=True)
    record = {"key": key, "activated_utc": datetime.utcnow().isoformat()}
    with open(_license_path(), "w", encoding="utf-8") as f:
        json.dump(record, f)
    return {"ok": True, "status": license_status()}


def deactivate_license() -> dict:
    try:
        p = _license_path()
        if os.path.exists(p):
            os.remove(p)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def license_status() -> dict:
    p = _license_path()
    if not os.path.exists(p):
        return {"tier": "COMMUNITY", "valid": False, "reason": "not_activated"}
    try:
        rec = json.load(open(p, "r", encoding="utf-8"))
        key = rec.get("key", "")
        # Try decode signed JSON
        try:
            data = json.loads(b64decode(key).decode("utf-8"))
            tier = data.get("tier", "COMMUNITY")
            expiry = data.get("expires", "19700101")
        except Exception:
            parts = key.split("-")
            tier = parts[1] if len(parts) >= 4 else "COMMUNITY"
            expiry = parts[2] if len(parts) >= 3 else "19700101"
        exp = datetime.strptime(expiry, "%Y%m%d")
        now = datetime.utcnow()
        valid = now <= exp
        return {"tier": tier, "valid": bool(valid), "expires": expiry}
    except Exception:
        return {"tier": "COMMUNITY", "valid": False, "reason": "corrupt_license"}


def is_pro_enabled() -> bool:
    st = license_status()
    return st.get("valid") and st.get("tier") in ("PRO", "ENT")



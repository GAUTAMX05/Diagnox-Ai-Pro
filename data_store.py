"""JSON persistence for analysis history, saved records, settings, and notifications."""
import json
import os
import re
import uuid
from datetime import datetime
from threading import Lock

import user_db
from pdf_report import build_clinical_advice

lock = Lock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")
RECORDS_PATH = os.path.join(DATA_DIR, "saved_records.json")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")
NOTIFICATIONS_PATH = os.path.join(DATA_DIR, "notifications.json")
PROFILE_DIR = os.path.join(DATA_DIR, "profiles")

DEFAULT_AVATAR = "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=80&h=80&fit=crop&crop=face"
ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PROFILE_DIR, exist_ok=True)


def _load(path):
    _ensure_data_dir()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(path, data):
    _ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _is_sample_entry(entry):
    return str(entry.get("id", "")).startswith("sample-")


def purge_sample_history(username=None):
    """Remove demo/sample analyses for one or all users."""
    with lock:
        data = _load(HISTORY_PATH)
        users = [username] if username else list(data.keys())
        for user in users:
            if user in data:
                data[user] = [e for e in data[user] if not _is_sample_entry(e)]
        _save(HISTORY_PATH, data)


def risk_from_severity(severity, symptom_count):
    s = (severity or "moderate").lower()
    if s == "severe" or symptom_count >= 8:
        return "High", "high"
    if s == "mild" and symptom_count <= 4:
        return "Low", "low"
    if s == "severe" and symptom_count >= 6:
        return "Critical", "critical"
    return "Medium", "medium"


def _initials(name):
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper() if name else "PT"


AVATAR_COLORS = ["purple", "green", "blue", "orange", "teal"]


def get_history(username):
    purge_sample_history(username)
    with lock:
        data = _load(HISTORY_PATH)
        return list(reversed(data.get(username, [])))


def add_history_entry(username, prediction, suggestion, symptoms_list, severity, patient_name=None):
    count = len(symptoms_list)
    risk, risk_class = risk_from_severity(severity, count)
    patient = patient_name.strip() if patient_name else f"Patient {datetime.now().strftime('%b %d')}"
    home_remedy, doctor_advice = build_clinical_advice(suggestion, risk, severity)
    entry = {
        "id": str(uuid.uuid4()),
        "patient": patient,
        "initials": _initials(patient),
        "avatar_color": AVATAR_COLORS[len(patient) % len(AVATAR_COLORS)],
        "date": datetime.now().strftime("%b %d, %Y"),
        "symptoms_count": count,
        "risk": risk,
        "risk_class": risk_class,
        "status": "Completed",
        "prediction": prediction,
        "severity": severity,
        "symptoms": symptoms_list,
        "suggestion": suggestion,
        "home_remedy": home_remedy,
        "doctor_advice": doctor_advice,
    }
    with lock:
        data = _load(HISTORY_PATH)
        data.setdefault(username, [])
        data[username].append(entry)
        _save(HISTORY_PATH, data)

    add_notification(
        username,
        "Analysis completed",
        f"{patient}: {prediction} ({risk} risk)",
        link=f"/reports",
        entry_id=entry["id"],
    )
    return entry


def delete_history_entry(username, entry_id):
    with lock:
        data = _load(HISTORY_PATH)
        data[username] = [e for e in data.get(username, []) if e.get("id") != entry_id]
        _save(HISTORY_PATH, data)


def clear_all_history(username):
    with lock:
        data = _load(HISTORY_PATH)
        data[username] = []
        _save(HISTORY_PATH, data)


def get_history_entry(username, entry_id):
    for item in get_history(username):
        if item.get("id") == entry_id:
            return item
    return None


def get_insights(username):
    items = get_history(username)
    total = len(items)
    if not total:
        return {"total": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
    counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for item in items:
        rc = item.get("risk_class", "medium")
        if rc in counts:
            counts[rc] += 1
        elif item.get("risk") == "Low":
            counts["low"] += 1
        elif item.get("risk") == "High":
            counts["high"] += 1
        else:
            counts["medium"] += 1
    return {
        "total": total,
        "low": round(100 * counts["low"] / total),
        "medium": round(100 * counts["medium"] / total),
        "high": round(100 * counts["high"] / total),
        "critical": round(100 * counts["critical"] / total),
    }


def get_saved_records(username):
    with lock:
        data = _load(RECORDS_PATH)
        return data.get(username, [])


def add_saved_record(username, patient, notes=""):
    record = {
        "id": str(uuid.uuid4()),
        "patient": patient.strip(),
        "initials": _initials(patient),
        "avatar_color": AVATAR_COLORS[len(patient) % len(AVATAR_COLORS)],
        "notes": notes.strip(),
        "date": datetime.now().strftime("%b %d, %Y"),
    }
    with lock:
        data = _load(RECORDS_PATH)
        data.setdefault(username, [])
        data[username].append(record)
        _save(RECORDS_PATH, data)
    return record


def delete_saved_record(username, record_id):
    with lock:
        data = _load(RECORDS_PATH)
        records = data.get(username, [])
        data[username] = [r for r in records if r.get("id") != record_id]
        _save(RECORDS_PATH, data)


def _user_key(username):
    return (username or "").strip()


def _safe_username(username):
    return re.sub(r"[^\w\-]", "_", _user_key(username))[:64]


def get_settings(username):
    username = _user_key(username)
    db_user = user_db.get_user(username) or {}
    with lock:
        data = _load(SETTINGS_PATH)
        defaults = {
            "display_name": db_user.get("display_name") or (username.split()[0].title() if username else "John"),
            "role": db_user.get("role") or "Clinician",
            "email": db_user.get("email", ""),
            "notifications": True,
            "keep_signed_in": True,
            "profile_image": db_user.get("profile_image", ""),
        }
        user_settings = data.get(username, {})
        merged = {**defaults, **user_settings}
        if db_user.get("profile_image"):
            merged["profile_image"] = db_user["profile_image"]
        return merged


def save_settings(username, settings):
    username = _user_key(username)
    db_fields = {}
    for key in ("display_name", "role", "email", "profile_image"):
        if key in settings:
            db_fields[key] = settings[key]
    if db_fields:
        user_db.update_user_fields(username, db_fields)
    with lock:
        data = _load(SETTINGS_PATH)
        data.setdefault(username, {})
        data[username].update(settings)
        _save(SETTINGS_PATH, data)
        return data[username]


def load_profile_from_database(username):
    """Load profile image path from user database into settings cache."""
    username = _user_key(username)
    filename = user_db.get_profile_image(username)
    if filename:
        save_settings(username, {"profile_image": filename})
    return filename


def get_profile_image_url(username):
    username = _user_key(username)
    settings = get_settings(username)
    filename = settings.get("profile_image", "")
    if filename:
        path = os.path.join(PROFILE_DIR, filename)
        if os.path.isfile(path):
            version = int(os.path.getmtime(path))
            return f"/uploads/profile/{filename}?v={version}"
    return DEFAULT_AVATAR


def save_profile_image(username, file_storage):
    username = _user_key(username)
    if not file_storage:
        return False, "No file selected."

    original_name = getattr(file_storage, "filename", None) or ""
    ext = os.path.splitext(original_name)[1].lower()
    if not ext and getattr(file_storage, "content_type", ""):
        mime = file_storage.content_type.lower()
        ext = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif",
        }.get(mime, "")
    if ext not in ALLOWED_IMAGE_EXT:
        return False, "Use JPG, PNG, WEBP, or GIF."

    _ensure_data_dir()
    delete_profile_image(username, remove_setting_only=True)
    safe = _safe_username(username)
    filename = f"{safe}_{uuid.uuid4().hex[:8]}{ext}"
    path = os.path.abspath(os.path.join(PROFILE_DIR, filename))

    try:
        file_storage.save(path)
    except OSError as exc:
        return False, f"Could not save file: {exc}"

    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return False, "Upload failed. Please try again."

    save_settings(username, {"profile_image": filename})
    user_db.set_profile_image(username, filename)
    return True, "Profile picture saved to your account."


def delete_profile_image(username, remove_setting_only=False):
    username = _user_key(username)
    settings = get_settings(username)
    filename = settings.get("profile_image", "")
    if filename and not remove_setting_only:
        path = os.path.join(PROFILE_DIR, filename)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
    save_settings(username, {"profile_image": ""})
    user_db.set_profile_image(username, "")
    return True


# --- Notifications ---
def get_notifications(username, limit=20):
    with lock:
        data = _load(NOTIFICATIONS_PATH)
        items = data.get(username, [])
        return sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)[:limit]


def get_unread_count(username):
    return sum(1 for n in get_notifications(username, limit=100) if not n.get("read"))


def add_notification(username, title, message, link="/home", entry_id=None):
    with lock:
        data = _load(NOTIFICATIONS_PATH)
        data.setdefault(username, [])
        data[username].insert(0, {
            "id": str(uuid.uuid4()),
            "title": title,
            "message": message,
            "link": link,
            "entry_id": entry_id,
            "read": False,
            "created_at": datetime.now().isoformat(),
            "time": datetime.now().strftime("%b %d, %I:%M %p"),
        })
        data[username] = data[username][:50]
        _save(NOTIFICATIONS_PATH, data)


def mark_notification_read(username, notification_id):
    with lock:
        data = _load(NOTIFICATIONS_PATH)
        for n in data.get(username, []):
            if n.get("id") == notification_id:
                n["read"] = True
        _save(NOTIFICATIONS_PATH, data)


def mark_all_notifications_read(username):
    with lock:
        data = _load(NOTIFICATIONS_PATH)
        for n in data.get(username, []):
            n["read"] = True
        _save(NOTIFICATIONS_PATH, data)


def build_report_text(entry):
    lines = [
        "DiagnoX AI Pro — Clinical Analysis Report",
        "=" * 48,
        f"Patient: {entry.get('patient', 'N/A')}",
        f"Date: {entry.get('date', 'N/A')}",
        f"Symptoms reported: {entry.get('symptoms_count', 0)}",
        f"Severity: {entry.get('severity', 'N/A')}",
        f"Risk level: {entry.get('risk', 'N/A')}",
        f"Status: {entry.get('status', 'N/A')}",
        "",
        "AI Prediction:",
        f"  {entry.get('prediction', 'N/A')}",
        "",
        "Clinical Suggestion:",
        f"  {entry.get('suggestion', 'N/A')}",
        "",
        "Disclaimer: For educational triage only. Not a substitute for professional diagnosis.",
    ]
    return "\n".join(lines)


# One-time cleanup of demo data for all users on import
purge_sample_history()

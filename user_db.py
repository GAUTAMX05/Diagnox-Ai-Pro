"""User credentials database (CSV) — profile and settings synced per account."""
import os
import pandas as pd
from threading import Lock

lock = Lock()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_PATH = os.path.join(BASE_DIR, "data", "users.csv")

USER_COLUMNS = ["username", "email", "password", "profile_image", "display_name", "role"]


def _ensure_users_file():
    os.makedirs(os.path.dirname(USERS_PATH), exist_ok=True)
    if not os.path.exists(USERS_PATH):
        pd.DataFrame(columns=USER_COLUMNS).to_csv(USERS_PATH, index=False)
        return
    with lock:
        df = pd.read_csv(USERS_PATH)
        changed = False
        for col in USER_COLUMNS:
            if col not in df.columns:
                df[col] = ""
                changed = True
        if changed:
            df.to_csv(USERS_PATH, index=False)


def get_user(username):
    _ensure_users_file()
    username = (username or "").strip()
    with lock:
        df = pd.read_csv(USERS_PATH)
        match = df[df["username"].astype(str).str.strip() == username]
        if match.empty:
            return None
        row = match.iloc[0]
        return {col: ("" if pd.isna(row[col]) else str(row[col]).strip()) for col in df.columns}


def find_user_by_email_or_username(identifier):
    _ensure_users_file()
    ident = (identifier or "").strip().lower()
    with lock:
        df = pd.read_csv(USERS_PATH)
        mask = (
            (df["email"].astype(str).str.lower().str.strip() == ident)
            | (df["username"].astype(str).str.lower().str.strip() == ident)
        )
        rows = df.loc[mask]
        if rows.empty:
            return None
        row = rows.iloc[0]
        return {col: ("" if pd.isna(row[col]) else str(row[col]).strip()) for col in df.columns}


def update_user_fields(username, fields):
    _ensure_users_file()
    username = (username or "").strip()
    with lock:
        df = pd.read_csv(USERS_PATH)
        idx = df[df["username"].astype(str).str.strip() == username].index
        if idx.empty:
            return False
        for key, value in fields.items():
            if key in df.columns:
                df.at[idx[0], key] = value if value is not None else ""
        df.to_csv(USERS_PATH, index=False)
        return True


def get_profile_image(username):
    user = get_user(username)
    if user:
        return user.get("profile_image", "")
    return ""


def set_profile_image(username, filename):
    return update_user_fields(username, {"profile_image": filename or ""})


def sync_signup_user(username, email, password):
    _ensure_users_file()
    if get_user(username.strip()) or find_user_by_email_or_username(email):
        return False
    with lock:
        df = pd.read_csv(USERS_PATH)
        new_row = {col: "" for col in USER_COLUMNS}
        new_row.update({
            "username": username.strip(),
            "email": email.strip(),
            "password": password,
            "profile_image": "",
            "display_name": username.split()[0].title() if username else "",
            "role": "Clinician",
        })
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(USERS_PATH, index=False)
        return True

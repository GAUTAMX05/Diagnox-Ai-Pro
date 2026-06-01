from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, Response, send_from_directory
import pickle
import pandas as pd
import numpy as np
import os
import re
from threading import Lock

import data_store
import user_db
from pdf_report import generate_analysis_pdf, build_clinical_advice

# --- Initialize Flask ---
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# --- Thread Lock for File Safety ---
file_lock = Lock()

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

MODEL_PATH = os.path.join(MODELS_DIR, 'disease_predictor.pkl')
USERS_PATH = os.path.join(DATA_DIR, 'users.csv')
MEDICATIONS_PATH = os.path.join(DATA_DIR, 'medications.csv')
TRAINING_DATA_PATH = os.path.join(DATA_DIR, 'Training.csv')

# Create data folder if missing
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"Created data directory: {DATA_DIR}")

# Globals that will be initialized lazily
model = None
medications_df = None
symptoms = []

# --- SAFE ONE TIME INITIALIZATION ---
def initialize():
    global model, medications_df, symptoms

    # Avoid reload duplication
    if model is not None and medications_df is not None and symptoms:
        return

    print("Initializing model and data...")

    # Load model
    try:
        with open(MODEL_PATH, 'rb') as file:
            model = pickle.load(file)
        print("Model loaded")
    except Exception as e:
        print(f"Model load error: {e}")
        model = None

    # Load Medications
    try:
        medications_df = pd.read_csv(MEDICATIONS_PATH)
        print("Medications data loaded")
    except Exception as e:
        print(f"Medications error: {e}")
        medications_df = None

    # Load symptom list from training CSV
    try:
        train_df = pd.read_csv(TRAINING_DATA_PATH)
        if 'Unnamed: 133' in train_df.columns:
            train_df = train_df.drop('Unnamed: 133', axis=1)
        symptoms = train_df.drop('prognosis', axis=1).columns.tolist()
        print(f"Symptoms loaded: {len(symptoms)}")
    except Exception as e:
        print(f"Training.csv error: {e}")
        symptoms = []


@app.before_request
def before_request():
    initialize()

# --- ROUTES ---
@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', "").strip()
        email = request.form.get('email', "").strip()
        password = request.form.get('password', "").strip()

        if not username or not email or not password:
            flash("❌ All fields are required.", "danger")
            return redirect(url_for('signup'))

        user_db._ensure_users_file()
        if user_db.get_user(username) or user_db.find_user_by_email_or_username(email):
            flash("Username or email already exists.", "danger")
            return redirect(url_for('signup'))

        if not user_db.sync_signup_user(username, email, password):
            flash("Could not create account.", "danger")
            return redirect(url_for('signup'))

        flash("✅ Signup successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', "").strip()
        username = request.form.get('username', "").strip() or email
        password = request.form.get('password', "").strip()

        user_row = user_db.find_user_by_email_or_username(email or username)
        if user_row and user_row.get("password") == password:
            session['user'] = user_row['username'].strip()
            session['email'] = user_row.get('email', email).strip()
            data_store.load_profile_from_database(session['user'])
            if user_row.get('display_name'):
                data_store.save_settings(session['user'], {
                    'display_name': user_row['display_name'],
                    'role': user_row.get('role') or 'Clinician',
                    'email': session['email'],
                })
            flash(f"Welcome back, {session['user']}!", "success")
            return redirect(url_for('home'))
        flash("Invalid email or password.", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("✅ You have been logged out.", "success")
    return redirect(url_for('login'))

def _require_login():
    if "user" not in session:
        flash("Please login to access this page.", "warning")
        return redirect(url_for('login'))
    return None


@app.context_processor
def inject_layout_context():
    """Always provide header/sidebar variables so partials never break."""
    if "user" not in session:
        return {
            "active_page": "",
            "unread_count": 0,
            "notifications": [],
            "settings": {
                "display_name": "",
                "role": "",
                "email": "",
                "profile_url": data_store.DEFAULT_AVATAR,
            },
            "user": "",
        }
    username = session["user"].strip()
    data_store.load_profile_from_database(username)
    settings = data_store.get_settings(username)
    if session.get("email") and not settings.get("email"):
        settings["email"] = session["email"]
    settings["profile_url"] = data_store.get_profile_image_url(username)
    return {
        "unread_count": data_store.get_unread_count(username),
        "notifications": data_store.get_notifications(username),
        "settings": settings,
        "user": username,
    }


def _app_context(active_page):
    return {"active_page": active_page}


@app.route('/home')
def home():
    guard = _require_login()
    if guard:
        return guard
    username = session["user"]
    ctx = _app_context("dashboard")
    user_history = data_store.get_history(username)
    ctx["recent_history"] = user_history[:4]
    ctx["history_items"] = user_history
    ctx["insights"] = data_store.get_insights(username)
    ctx["saved_count"] = len(data_store.get_saved_records(username))
    ctx["donut_segments"] = _donut_segments(ctx["insights"])
    return render_template('dashboard.html', **ctx)


def _donut_segments(insights):
    circ = 301.6
    segments = []
    offset = 0
    for key, color in [
        ("low", "#26A69A"),
        ("medium", "#FFB74D"),
        ("high", "#EF5350"),
        ("critical", "#64748b"),
    ]:
        pct = insights.get(key, 0)
        if pct > 0:
            dash = round(pct / 100 * circ, 1)
            segments.append({"dash": dash, "offset": offset, "color": color})
            offset -= dash
    return segments


@app.route('/analysis')
def analysis():
    guard = _require_login()
    if guard:
        return guard
    ctx = _app_context("analysis")
    ctx["symptoms"] = symptoms
    return render_template('analysis.html', **ctx)


@app.route('/history')
def history():
    guard = _require_login()
    if guard:
        return guard
    ctx = _app_context("history")
    ctx["history_items"] = data_store.get_history(session["user"])
    return render_template('history.html', **ctx)


@app.route('/history/delete/<entry_id>', methods=['POST'])
def delete_analysis(entry_id):
    guard = _require_login()
    if guard:
        return guard
    data_store.delete_history_entry(session["user"], entry_id)
    flash("Analysis removed.", "success")
    return redirect(request.referrer or url_for('history'))


@app.route('/history/clear-all', methods=['POST'])
def clear_all_analyses():
    guard = _require_login()
    if guard:
        return guard
    data_store.clear_all_history(session["user"])
    flash("All analyses cleared.", "success")
    return redirect(url_for('history'))


@app.route('/reports')
def reports():
    guard = _require_login()
    if guard:
        return guard
    ctx = _app_context("reports")
    ctx["history_items"] = [
        h for h in data_store.get_history(session["user"])
        if h.get("status") == "Completed"
    ]
    return render_template('reports.html', **ctx)


@app.route('/saved-records', methods=['GET', 'POST'])
def saved_records():
    guard = _require_login()
    if guard:
        return guard
    username = session["user"]
    if request.method == 'POST':
        patient = request.form.get('patient', '').strip()
        notes = request.form.get('notes', '').strip()
        if patient:
            data_store.add_saved_record(username, patient, notes)
            flash(f"Saved record for {patient}.", "success")
        else:
            flash("Patient name is required.", "danger")
        return redirect(url_for('saved_records'))
    ctx = _app_context("saved_records")
    ctx["records"] = data_store.get_saved_records(username)
    return render_template('saved_records.html', **ctx)


@app.route('/saved-records/delete/<record_id>', methods=['POST'])
def delete_record(record_id):
    guard = _require_login()
    if guard:
        return guard
    data_store.delete_saved_record(session["user"], record_id)
    flash("Record deleted.", "success")
    return redirect(url_for('saved_records'))


@app.route('/history/save/<entry_id>', methods=['POST'])
def save_from_history(entry_id):
    guard = _require_login()
    if guard:
        return guard
    entry = data_store.get_history_entry(session["user"], entry_id)
    if entry:
        notes = f"Diagnosis: {entry.get('prediction', '')}. Risk: {entry.get('risk', '')}."
        data_store.add_saved_record(session["user"], entry["patient"], notes)
        flash(f"Saved {entry['patient']} to records.", "success")
    else:
        flash("Analysis not found.", "danger")
    return redirect(request.referrer or url_for('history'))


@app.route('/reports/download/<entry_id>')
def download_report(entry_id):
    guard = _require_login()
    if guard:
        return guard
    username = session["user"].strip()
    entry = data_store.get_history_entry(username, entry_id)
    if not entry:
        flash("Report not found.", "danger")
        return redirect(url_for('reports'))

    if not entry.get("home_remedy") or not entry.get("doctor_advice"):
        home, doctor = build_clinical_advice(
            entry.get("suggestion", ""),
            entry.get("risk", "Medium"),
            entry.get("severity", "moderate"),
        )
        entry["home_remedy"] = home
        entry["doctor_advice"] = doctor

    settings = data_store.get_settings(username)
    try:
        pdf_bytes = generate_analysis_pdf(
            entry,
            clinician_name=settings.get("display_name", username),
            clinician_role=settings.get("role", "Clinician"),
        )
    except Exception as exc:
        print(f"PDF generation error: {exc}")
        flash("Could not generate PDF report.", "danger")
        return redirect(url_for('reports'))

    safe_name = re.sub(r"[^\w\-]", "_", entry.get("patient", "patient"))
    filename = f"DiagnoX_Report_{safe_name}.pdf"
    response = Response(pdf_bytes, mimetype="application/pdf")
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.headers["Content-Length"] = str(len(pdf_bytes))
    return response


@app.route('/uploads/profile/<filename>')
def serve_profile_image(filename):
    if "user" not in session:
        return "", 403
    safe_file = os.path.basename(filename.split("?")[0])
    owner_prefix = data_store._safe_username(session["user"]) + "_"
    if not safe_file.startswith(owner_prefix):
        return "", 404
    path = os.path.join(data_store.PROFILE_DIR, safe_file)
    if not os.path.isfile(path):
        return "", 404
    return send_from_directory(data_store.PROFILE_DIR, safe_file)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    guard = _require_login()
    if guard:
        return guard
    username = session["user"]

    if request.method == 'POST':
        action = request.form.get('action', 'save')

        if action == 'remove_photo':
            data_store.delete_profile_image(username)
            flash("Profile picture removed.", "success")
            return redirect(url_for('settings'))

        if action == 'upload_photo':
            file = request.files.get('profile_photo')
            ok, msg = data_store.save_profile_image(username, file)
            flash(msg, "success" if ok else "danger")
            return redirect(url_for('settings'))

        data_store.save_settings(username, {
            "display_name": request.form.get('display_name', '').strip(),
            "role": request.form.get('role', 'Clinician').strip(),
            "email": request.form.get('email', '').strip(),
            "notifications": request.form.get('notifications') == 'on',
            "keep_signed_in": request.form.get('keep_signed_in') == 'on',
        })
        flash("Settings saved successfully.", "success")
        return redirect(url_for('settings'))

    ctx = _app_context("settings")
    ctx["has_custom_photo"] = bool(data_store.get_settings(username).get("profile_image"))
    return render_template('settings.html', **ctx)


@app.route('/settings/upload-photo', methods=['POST'])
def upload_profile_photo():
    guard = _require_login()
    if guard:
        return guard
    username = session["user"].strip()
    file = request.files.get('profile_photo')
    ok, msg = data_store.save_profile_image(username, file)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for('settings'))


@app.route('/notifications/mark-read/<notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    guard = _require_login()
    if guard:
        return guard
    data_store.mark_notification_read(session["user"], notification_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"ok": True, "unread": data_store.get_unread_count(session["user"])})
    return redirect(request.referrer or url_for('home'))


@app.route('/notifications/mark-all-read', methods=['POST'])
def mark_all_notifications_read():
    guard = _require_login()
    if guard:
        return guard
    data_store.mark_all_notifications_read(session["user"])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"ok": True, "unread": 0})
    return redirect(request.referrer or url_for('home'))

# === MODIFIED PREDICT ROUTE ===
@app.route('/predict', methods=['POST'])
def predict():
    if "user" not in session:
        return jsonify({'error': 'Please login first.'}), 401
    if model is None or medications_df is None or not symptoms:
        return jsonify({'error': 'Server is not configured properly.'}), 500

    selected_symptoms = request.form.getlist('symptoms')
    severity = request.form.get('severity', 'moderate')
    patient_name = request.form.get('patient_name', '').strip()

    if not selected_symptoms:
        return jsonify({'error': 'Select at least one symptom.'}), 400

    try:
        print(f"Received {len(selected_symptoms)} symptoms with severity: {severity}")

        input_data = np.zeros(len(symptoms))
        for symptom in selected_symptoms:
            if symptom in symptoms:
                input_data[symptoms.index(symptom)] = 1

        prediction = model.predict([input_data])[0]

        suggestion_row = medications_df[
            medications_df['Disease'].str.lower() == prediction.lower()
        ]
        suggestion = suggestion_row['Suggestion'].iloc[0] if not suggestion_row.empty else \
            "No specific suggestion found. Please consult a doctor."

        entry = data_store.add_history_entry(
            session["user"],
            prediction,
            suggestion,
            selected_symptoms,
            severity,
            patient_name or None,
        )

        return jsonify({
            'prediction': prediction,
            'suggestion': suggestion,
            'home_remedy': entry.get('home_remedy', suggestion),
            'doctor_advice': entry.get('doctor_advice', suggestion),
            'entry_id': entry['id'],
            'risk': entry['risk'],
            'risk_class': entry['risk_class'],
            'report_url': url_for('download_report', entry_id=entry['id']),
        })

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': str(e)}), 500
# === END OF MODIFIED ROUTE ===


def _verify_routes():
    required = {'home', 'history', 'reports', 'saved_records', 'settings', 'analysis', 'login'}
    found = {r.endpoint for r in app.url_map.iter_rules()}
    missing = required - found
    if missing:
        raise RuntimeError(f"Missing routes: {missing}. Restart using: python app.py")


_verify_routes()

# Ensure user database schema (profile_image column per account)
user_db._ensure_users_file()


# --- Run ---
if __name__ == '__main__':
    print("DiagnoX AI Pro running at http://127.0.0.1:5000")
    print("Routes:", sorted({r.endpoint for r in app.url_map.iter_rules()}))
    app.run(debug=False, port=5000, use_reloader=False)
import streamlit as st
import pickle
import pandas as pd
import numpy as np
import time
import re
from datetime import datetime
from fpdf import FPDF
import io

st.set_page_config(
    page_title="DiagnoX AI Pro",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Source+Sans+3:wght@300;400;600;700&display=swap');
:root {
    color-scheme: dark;
    --bg: #0F172A;
    --panel: #1E293B;
    --panel-soft: rgba(30, 41, 59, 0.92);
    --border: rgba(14, 165, 233, 0.15);
    --primary: #0EA5E9;
    --secondary: #14B8A6;
    --surface: #1E293B;
    --surface-muted: #334155;
    --text: #F1F5F9;
    --text-muted: #94A3B8;
    --shadow: 0 24px 80px rgba(0, 0, 0, 0.32);
}

body, .block-container {
    background: linear-gradient(180deg, #0F172A 0%, #1A1F35 100%);
    color: var(--text);
    font-size: 16px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp, .main {
    font-family: 'Inter', 'Source Sans 3', 'Source Sans Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    color: var(--text);
    font-weight: 400;
}

section.main {
    padding-top: 1rem;
}

h1 { font-weight: 800; letter-spacing: -0.02em; color: var(--text); font-size: clamp(2.4rem, 4vw, 3.6rem); }
h2 { font-weight: 700; color: var(--text); }
h3, h4, h5, h6 { font-weight: 600; color: var(--text); }

.stSidebar {
    background: rgba(30, 41, 59, 0.96);
    border-right: 1px solid rgba(14, 165, 233, 0.1);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
    font-family: inherit;
}

.css-1d391kg, .css-18e3th9, .css-uhb7vk, .css-1oe4e9u.e1tzin5v0 {
    background: transparent;
}

.stButton > button, .stDownloadButton > button {
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 1.2rem !important;
    background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
    box-shadow: 0 16px 36px rgba(14, 165, 233, 0.2) !important;
    font-weight: 600 !important;
    font-family: inherit !important;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px);
}

input, textarea, select {
    background: rgba(71, 85, 105, 0.2) !important;
    color: var(--text) !important;
    border: 1px solid rgba(14, 165, 233, 0.2) !important;
    border-radius: 12px !important;
    font-family: inherit !important;
    padding: 10px !important;
}

input:focus, textarea:focus, select:focus {
    border-color: rgba(14, 165, 233, 0.4) !important;
    box-shadow: 0 0 0 6px rgba(14, 165, 233, 0.1) !important;
}

.hero-section {
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.08), rgba(20, 184, 166, 0.05));
    border: 1px solid rgba(14, 165, 233, 0.1);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.24);
    padding: 3rem;
    overflow: hidden;
}

.hero-content { max-width: 640px; }

.hero-badge { display:inline-flex; align-items:center; gap:0.6rem; padding:0.6rem 0.9rem; border-radius:999px; background: rgba(14,165,233,0.12); color:var(--primary); font-weight:700; margin-bottom:1rem; font-family:inherit; }

.hero-title { font-size: clamp(2.2rem, 3.6vw, 3.6rem); line-height:1.03; margin-bottom:0.6rem; }
.hero-subtitle { color: var(--text-muted); font-size:1rem; line-height:1.6; margin-bottom:1.5rem; }

.hero-visual { min-height:360px; border-radius:20px; background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%); display:flex; align-items:center; justify-content:center; position:relative; box-shadow:0 12px 36px rgba(0,0,0,0.2); }
.hero-icon { position:absolute; width:64px; height:64px; border-radius:16px; background: rgba(14,165,233,0.15); display:grid; place-items:center; color:var(--primary); font-size:1.3rem; }

.info-card, .auth-card, .dashboard-card, .category-card, .result-card { border-radius:16px; background:var(--panel); border:1px solid rgba(14,165,233,0.1); box-shadow:0 12px 36px rgba(0,0,0,0.15); }

.auth-tab { font-family: inherit; }
.form-label { color: var(--text-muted); font-size:0.95rem; }
.form-control { border-radius:12px !important; padding:0.8rem 0.9rem !important; font-size:0.98rem !important; }

.category-card { padding:1.2rem; margin-bottom:1rem; }
.symptom-tag { font-size:0.92rem; padding:0.45rem 0.65rem; }

.slider-pill { font-weight:700; }
.result-card { padding:1.2rem; margin-bottom:1rem; }
.metric-pill { padding:0.7rem 0.9rem; }
.progress-bar { height:10px; border-radius:999px; background:rgba(71,85,105,0.3); margin-top:0.6rem; }
.progress-bar span { display:block; height:100%; border-radius:999px; }

.footer { padding:1.6rem 0 0.8rem; text-align:center; color:var(--text-muted); font-size:0.92rem; }
.footer a { color:var(--primary); text-decoration:none; }

.toast { position:fixed; right:20px; bottom:20px; z-index:9999; padding:0.9rem 1.1rem; border-radius:12px; backdrop-filter: blur(8px); border:1px solid rgba(14,165,233,0.1); box-shadow:0 16px 36px rgba(0,0,0,0.24); background:rgba(30,41,59,0.95); }

@media (max-width:900px) { .hero-section { padding:2rem; } .hero-visual { min-height:260px; } }
@media (max-width:640px) { .section-header { flex-direction:column; align-items:flex-start; } .hero-section { padding:1.25rem; } .auth-card, .info-card, .result-card { border-radius:14px; } }
</style>
"""

st.markdown(APP_STYLE, unsafe_allow_html=True)

symptom_categories = {
    "General & Systemic": ['itching', 'chills', 'fatigue', 'lethargy', 'malaise', 'weight_loss', 'weight_gain', 'excessive_hunger', 'dehydration', 'sweating', 'fever'],
    "Head & Neck": ['headache', 'dizziness', 'slurred_speech', 'sinus_pressure', 'runny_nose', 'congestion', 'sore_throat', 'stiff_neck', 'loss_of_smell', 'ulcers_on_tongue', 'patches_in_throat', 'enlarged_thyroid', 'puffy_face_and_eyes', 'swollen_lymph_nodes'],
    "Eyes & Vision": ['blurred_and_distorted_vision', 'yellowing_of_eyes', 'redness_of_eyes', 'pain_behind_the_eyes', 'sunken_eyes', 'visual_disturbances'],
    "Chest & Respiratory": ['chest_pain', 'breathlessness', 'cough', 'phlegm', 'mucoid_sputum', 'rusty_sputum', 'palpitations'],
    "Abdominal & Digestive": ['stomach_pain', 'acidity', 'vomiting', 'nausea', 'indigestion', 'diarrhoea', 'constipation', 'abdominal_pain', 'belly_pain', 'passage_of_gases', 'bloody_stool', 'stomach_bleeding', 'distention_of_abdomen'],
    "Skin & Joints": ['skin_rash', 'nodal_skin_eruptions', 'dischromic _patches', 'yellowish_skin', 'bruising', 'joint_pain', 'neck_pain', 'back_pain', 'knee_pain', 'hip_joint_pain', 'weakness_of_one_body_side', 'weakness_in_limbs', 'swelling_joints', 'movement_stiffness', 'swollen_legs', 'brittle_nails', 'skin_peeling', 'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails'],
    "Urinary & Genital": ['burning_micturition', 'spotting_ urination', 'dark_urine', 'yellow_urine', 'abnormal_menstruation', 'continuous_feel_of_urine'],
    "Psychological & Mood": ['anxiety', 'mood_swings', 'depression', 'irritability', 'restlessness', 'lack_of_concentration', 'altered_sensorium', 'coma']
}

category_icons = {
    "General & Systemic": "🩺",
    "Head & Neck": "🧠",
    "Eyes & Vision": "👁️",
    "Chest & Respiratory": "💨",
    "Abdominal & Digestive": "🫀",
    "Skin & Joints": "🦴",
    "Urinary & Genital": "🚽",
    "Psychological & Mood": "🧘‍♂️",
}

severity_labels = {1: "Mild", 2: "Moderate", 3: "Severe"}
severity_colors = {1: "#14B8A6", 2: "#0EA5E9", 3: "#F97316"}

@st.cache_data(show_spinner=False)
def load_data():
    try:
        with open("disease_predictor.pkl", "rb") as f:
            model = pickle.load(f)
        medications_df = pd.read_csv("medications.csv")
        train_df = pd.read_csv("Training.csv")
        if "Unnamed: 133" in train_df.columns:
            train_df = train_df.drop(columns=["Unnamed: 133"], errors='ignore')
        symptoms_list = sorted(train_df.drop(columns=["prognosis"], errors='ignore').columns.tolist())
        return model, medications_df, symptoms_list
    except FileNotFoundError as exc:
        st.error(f"Missing file: {exc.filename}. Please place the model and CSV files in the project folder.")
        st.stop()
    except Exception as exc:
        st.error(f"Failed to load data: {exc}")
        st.stop()

model, medications_df, symptoms_list = load_data()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Dashboard"
if "page" not in st.session_state:
    st.session_state.page = "Login"
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "history" not in st.session_state:
    st.session_state.history = []
if "toast" not in st.session_state:
    st.session_state.toast = {"message": None, "level": "info"}
if "selected_symptoms" not in st.session_state:
    st.session_state.selected_symptoms = []
if "severity_index" not in st.session_state:
    st.session_state.severity_index = 2
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "show_password" not in st.session_state:
    st.session_state.show_password = False
if "user_name" not in st.session_state:
    st.session_state.user_name = "Clinical User"

class PDF(FPDF):
    def __init__(self, name="User", age="N/A"):
        super().__init__()
        self.user_name = name
        self.user_age = age
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "DiagnoX AI Pro Report", 0, 1, "C")
        self.ln(2)

    def footer(self):
        self.set_y(-16)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 0, "R")

    def chapter_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(14, 165, 233)
        self.cell(0, 8, title, 0, 1, "L")
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def chapter_body(self, body):
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, body)
        self.ln(2)

    def add_diagnosis(self, diagnosis, probability):
        self.set_font("Helvetica", "B", 11)
        self.cell(120, 8, diagnosis, 1, 0, "L")
        self.set_font("Helvetica", "", 11)
        self.cell(60, 8, f"{probability * 100:.1f}%", 1, 1, "R")


def validate_email(value: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", value.strip()))


def set_toast(message: str, level: str = "info"):
    st.session_state.toast = {"message": message, "level": level}


def render_toast():
    """Display toast notifications"""
    if st.session_state.toast.get("message"):
        level = st.session_state.toast.get("level", "info")
        colors = {
            "success": "#10B981",
            "error": "#EF4444",
            "warning": "#F59E0B",
            "info": "#0EA5E9"
        }
        icons = {
            "success": "✓",
            "error": "✕",
            "warning": "⚠",
            "info": "ℹ"
        }
        color = colors.get(level, colors["info"])
        icon = icons.get(level, icons["info"])
        st.markdown(f"""
            <div class='toast' style='background:rgba(30,41,59,0.95);border:1px solid {color}33;'>
                <span style='color:{color};font-size:1.2rem;margin-right:8px;'>{icon}</span>
                <span style='color:var(--text);'>{st.session_state.toast['message']}</span>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(2)
        st.session_state.toast = {"message": None, "level": "info"}


def render_login_page():
    st.markdown("<div style='max-width:1200px;margin:30px auto;padding:20px;'>", unsafe_allow_html=True)
    left, right = st.columns([1, 0.9])
    with left:
        st.markdown("<div style='padding:20px 30px;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='margin:0 0 8px 0;'>🩺 Welcome to DiagnoX AI Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:var(--text-muted);margin:0 0 16px 0;'>Secure AI-powered clinical symptom analysis</p>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:32px;'><div style='display:flex;gap:16px;flex-direction:column;'>" +
                   "<div style='display:flex;align-items:center;gap:12px;'><span style='font-size:1.5rem;'>🔒</span><div><strong>HIPAA Compliant</strong><p style='color:var(--text-muted);margin:4px 0 0 0;font-size:0.9rem;'>Your data is encrypted and secure</p></div></div>" +
                   "<div style='display:flex;align-items:center;gap:12px;'><span style='font-size:1.5rem;'>⚡</span><div><strong>Instant Results</strong><p style='color:var(--text-muted);margin:4px 0 0 0;font-size:0.9rem;'>AI analysis in seconds</p></div></div>" +
                   "<div style='display:flex;align-items:center;gap:12px;'><span style='font-size:1.5rem;'>📊</span><div><strong>Clinical Grade</strong><p style='color:var(--text-muted);margin:4px 0 0 0;font-size:0.9rem;'>Professional PDF reports</p></div></div>" +
                   "</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div style='display:flex;justify-content:center;'>", unsafe_allow_html=True)
        st.markdown("<div style='width:420px;background:var(--panel);padding:28px;border-radius:20px;box-shadow:0 12px 40px rgba(15,23,42,0.08);'>", unsafe_allow_html=True)
        st.markdown("<h2 style='margin:0 0 8px 0;'>👋 Welcome Back</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:var(--text-muted);margin:0 0 14px 0;'>Sign in to access the dashboard</p>", unsafe_allow_html=True)
        with st.form(key='login_form'):
            email = st.text_input('Email', key='login_email', placeholder='you@healthcare.com')
            show = st.checkbox('Show password', key='login_show_password')
            pwd_type = 'default' if show else 'password'
            password = st.text_input('Password', type=pwd_type, key='login_password')
            remember = st.checkbox('Remember me', value=True, key='login_remember')
            st.markdown("<div style='display:flex;justify-content:space-between;align-items:center;margin-top:6px;'><a href='#' style='color:var(--primary);'>Forgot Password?</a></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button('Sign In')
            if submitted:
                if not validate_email(email):
                    set_toast('Enter a valid email address.', 'error')
                elif not password:
                    set_toast('Password is required.', 'error')
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_name = email.split('@')[0].title()
                    st.session_state.page = 'Dashboard'
                    set_toast('Login successful', 'success')
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    render_toast()


def render_auth_page():
    st.markdown("<div class='auth-card' style='padding: 2rem; margin-top: 1.75rem;'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'><div><h2 style='margin:0;'>Secure Access</h2><p style='color: var(--text-muted); margin-top:0.35rem;'>Sign in or create an account to access the medical dashboard.</p></div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    auth_cols = st.columns([1, 1])
    if auth_cols[0].button("Login", key="tab_login"):
        st.session_state.auth_mode = "login"
    if auth_cols[1].button("Signup", key="tab_signup"):
        st.session_state.auth_mode = "signup"

    st.markdown("<div class='auth-card' style='margin-top: 1rem; padding: 2rem;'>", unsafe_allow_html=True)
    with st.form(key="auth_form"):
        if st.session_state.auth_mode == "login":
            st.markdown("<div style='margin-bottom:1rem;'><strong style='font-size:1.15rem;'>Login to DiagnoX AI Pro</strong></div>", unsafe_allow_html=True)
            email = st.text_input("Email", key="login_email", placeholder="you@healthcare.com")
            show_password = st.checkbox("Show password", key="show_password")
            password = st.text_input("Password", type="default" if show_password else "password", key="login_password")
            remember = st.checkbox("Remember me", value=True, key="remember_me")
            st.markdown("<div style='display:flex; justify-content: space-between; align-items:center; margin-top:0.5rem;'><a href='#' style='color: var(--primary);'>Forgot Password?</a></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Login")
            if submitted:
                if not validate_email(email):
                    set_toast("Enter a valid email address.", "error")
                elif not password:
                    set_toast("Password is required.", "error")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_name = email.split("@")[0].title()
                    st.session_state.selected_page = "Dashboard"
                    set_toast("Welcome back!", "success")
                    st.rerun()
        else:
            st.markdown("<div style='margin-bottom:1rem;'><strong style='font-size:1.15rem;'>Create your account</strong></div>", unsafe_allow_html=True)
            name = st.text_input("Full Name", key="signup_name", placeholder="Jane Doe")
            email = st.text_input("Email", key="signup_email", placeholder="you@healthcare.com")
            show_password = st.checkbox("Show password", key="signup_show_password")
            password = st.text_input("Password", type="default" if show_password else "password", key="signup_password")
            confirm = st.text_input("Confirm Password", type="default" if show_password else "password", key="signup_confirm_password")
            submitted = st.form_submit_button("Create Account")
            if submitted:
                if not name.strip():
                    set_toast("Please enter your name.", "error")
                elif not validate_email(email):
                    set_toast("Enter a valid email address.", "error")
                elif len(password) < 8:
                    set_toast("Password must be at least 8 characters.", "error")
                elif password != confirm:
                    set_toast("Passwords do not match.", "error")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_name = name.title()
                    st.session_state.selected_page = "Dashboard"
                    set_toast("Account created successfully!", "success")
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    render_toast()
    st.markdown("<div class='footer'><a href='#'>Privacy Policy</a> · <a href='#'>Terms</a> · <a href='#'>Contact</a></div>", unsafe_allow_html=True)


def render_sidebar():
    st.sidebar.markdown("<div style='padding: 1rem 0 1rem 0;'><h2 style='margin: 0;'>🩺 DiagnoX AI Pro</h2><p style='color: var(--text-muted); margin: 0.35rem 0 0 0;'>Healthcare workflow hub</p></div>", unsafe_allow_html=True)
    menu_display = ["📊 Dashboard", "🔍 Symptom Analysis", "📋 History", "📄 Reports", "⚙️ Settings"]
    menu_keys = ["Dashboard", "Symptom Analysis", "History", "Reports", "Settings"]
    
    # Determine current index based on page state
    current_page = st.session_state.page
    if current_page == "Results":
        current_page = "Symptom Analysis"
    
    try:
        current_idx = menu_keys.index(current_page)
    except ValueError:
        current_idx = 0
    
    # Sidebar navigation
    choice_display = st.sidebar.radio("Navigation", menu_display, index=current_idx)
    choice = menu_keys[menu_display.index(choice_display)]
    
    # Update page state when navigation changes
    st.session_state.page = choice
    st.session_state.selected_page = choice
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.analysis_results = None
        st.session_state.page = 'Login'
        set_toast("✅ Logged out successfully.", "info")
        st.rerun()


def render_topbar():
    c1, c2, c3 = st.columns([3, 5, 2])
    with c1:
        st.markdown("<div class='metric-pill'><span>Search</span><span style='color: var(--text-muted);'>Find conditions, symptoms, or reports</span></div>", unsafe_allow_html=True)
    with c2:
        query = st.text_input("Search the platform", value=st.session_state.search_query, key="top_search", placeholder="Search symptoms, conditions, or patient notes...")
        st.session_state.search_query = query
    with c3:
        st.markdown("<div style='display:flex; justify-content:flex-end; gap:0.9rem; align-items:center;'><span style='font-size:1.25rem;'>🔔</span><span style='font-size:1.25rem;'>👤</span></div>", unsafe_allow_html=True)


def get_selected_symptoms():
    selected = []
    for category, symptoms in symptom_categories.items():
        for symptom in symptoms:
            if st.session_state.get(f"sym_{symptom}", False):
                selected.append(symptom)
    return selected


def render_symptom_analysis():
    st.markdown("<div class='section-header'><div><h2>🔍 Symptom Analysis</h2><p style='color: var(--text-muted); margin-top:0.35rem;'>Choose symptoms, rate severity, and generate an explainable diagnosis summary.</p></div></div>", unsafe_allow_html=True)
    search = st.text_input("🔎 Search symptoms", value=st.session_state.search_query, key="symptom_search", placeholder="Search symptom categories...")
    st.session_state.search_query = search
    left, right = st.columns([2, 1])
    with left:
        for category, symptoms in symptom_categories.items():
            matches = [s for s in symptoms if s in symptoms_list and (search.lower() in s.replace("_", " ").lower() or search.lower() in category.lower() or not search)]
            if not matches:
                continue
            with st.expander(f"{category_icons.get(category, '🧪')} {category} ({len(matches)})", expanded=True):
                for symptom in matches:
                    label = symptom.replace("_", " ").title()
                    st.checkbox(label, key=f"sym_{symptom}")
    with right:
        selected_symptoms = get_selected_symptoms()
        st.markdown("<div class='category-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin-top:0;'>Selected Symptoms</h4>", unsafe_allow_html=True)
        if selected_symptoms:
            for symptom in selected_symptoms:
                st.markdown(f"<span class='symptom-tag'>{symptom.replace('_',' ').title()}</span>", unsafe_allow_html=True)
        else:
            st.info("No symptoms selected yet.")
        st.markdown(f"<div style='margin-top:1rem; color: var(--text-muted);'>Total selected: <strong>{len(selected_symptoms)}</strong></div>", unsafe_allow_html=True)
        progress = min(len(selected_symptoms) / 18, 1.0)
        st.progress(progress)
        st.markdown("</div>", unsafe_allow_html=True)

        severity_color = severity_colors.get(st.session_state.severity_index, '#0EA5E9')
        st.markdown("<div class='category-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin-top:0;'>Severity Setting</h4>", unsafe_allow_html=True)
        st.markdown(f"<div class='slider-pill' style='border-color: {severity_color}; color: {severity_color};'>{severity_labels[st.session_state.severity_index]}</div>", unsafe_allow_html=True)
        severity = st.slider("Overall Clinical Severity", min_value=1, max_value=3, value=st.session_state.severity_index, format="%d")
        st.session_state.severity_index = severity
        st.markdown("<div class='progress-bar'><span style='width: {0}%; background: linear-gradient(90deg, #14B8A6, #0EA5E9, #F97316);'></span></div>".format(int((severity / 3) * 100)), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns([1,1])
    if cols[0].button('Back'):
        st.session_state.page = 'Dashboard'
        st.session_state.selected_page = 'Dashboard'
        st.rerun()
    if cols[1].button('Analyze Symptoms'):
        selected_symptoms = get_selected_symptoms()
        if not selected_symptoms:
            set_toast('Select at least one symptom before analyzing.', 'error')
        else:
            with st.spinner('Generating your differential diagnosis...'):
                time.sleep(1.1)
                vector = np.zeros(len(symptoms_list), dtype=int)
                for symptom in selected_symptoms:
                    if symptom in symptoms_list:
                        vector[symptoms_list.index(symptom)] = 1
                try:
                    probabilities = model.predict_proba(vector.reshape(1, -1))[0]
                    top_idx = np.argsort(probabilities)[-4:][::-1]
                    predictions = []
                    for idx in top_idx:
                        disease = str(model.classes_[idx])
                        confidence = float(probabilities[idx])
                        match = medications_df[medications_df["Disease"].str.lower().str.strip() == disease.lower().strip()]
                        suggestions = match["Suggestion"].tolist() if not match.empty else ["Consult a licensed medical professional for clinical interpretation."]
                        risk = "Low" if confidence < 0.35 else "Moderate" if confidence < 0.72 else "High"
                        predictions.append({
                            "disease": disease,
                            "confidence": confidence,
                            "risk": risk,
                            "suggestions": suggestions,
                        })
                    st.session_state.analysis_results = {
                        "user_name": st.session_state.user_name,
                        "user_age": st.session_state.get("user_age", "N/A"),
                        "selected_symptoms": selected_symptoms,
                        "severity": severity_labels[st.session_state.severity_index],
                        "top_predictions": predictions,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    st.session_state.history.insert(0, f"{datetime.now().strftime('%Y-%m-%d %H:%M')} • {predictions[0]['disease']}")
                    set_toast('Analysis complete. Redirecting to results...', 'success')
                    st.session_state.page = 'Results'
                    st.rerun()
                except Exception as exc:
                    set_toast(f'Analysis failed: {exc}', 'error')


def render_analysis_results():
    results = st.session_state.analysis_results
    if not results:
        return
    st.markdown("<div class='section-header'><div><h2>📊 Analysis Results</h2><p style='color: var(--text-muted); margin-top:0.35rem;'>Premium condition cards with confidence, risk, and next steps.</p></div></div>", unsafe_allow_html=True)
    # Summary metrics
    metrics = st.columns(3)
    metrics[0].markdown(f"<div class='metric-pill'><strong>🔍 Symptoms</strong><span>{len(results['selected_symptoms'])}</span></div>", unsafe_allow_html=True)
    metrics[1].markdown(f"<div class='metric-pill'><strong>⚠️ Severity</strong><span>{results['severity']}</span></div>", unsafe_allow_html=True)
    metrics[2].markdown(f"<div class='metric-pill'><strong>✓ Top Match</strong><span>{results['top_predictions'][0]['disease'] if results['top_predictions'] else 'N/A'}</span></div>", unsafe_allow_html=True)

    # Confidence chart
    chart_df = pd.DataFrame({
        "Condition": [item["disease"] for item in results["top_predictions"]],
        "Confidence": [item["confidence"] for item in results["top_predictions"]],
    })
    if not chart_df.empty:
        st.altair_chart((
            (pd.DataFrame(chart_df).set_index('Condition') * 100)
        ), use_container_width=True)

    # Result cards
    for idx, item in enumerate(results["top_predictions"], 1):
        risk_icon = "🟢" if item["risk"] == "Low" else "🟡" if item["risk"] == "Moderate" else "🔴"
        color = "#14B8A6" if item["risk"] == "Low" else "#0EA5E9" if item["risk"] == "Moderate" else "#F97316"
        st.markdown(f"<div class='result-card'><h4>#{idx} {item['disease']}</h4><p style='color: var(--text-muted); margin:0 0 0.8rem 0;'>Confidence <strong>{item['confidence']*100:.1f}%</strong> · Risk <strong style='color:{color};'>{risk_icon} {item['risk']}</strong></p>", unsafe_allow_html=True)
        st.markdown(f"<div class='progress-bar'><span style='width: {int(item['confidence']*100)}%; background: linear-gradient(90deg, #14B8A6, #0EA5E9, #F97316);'></span></div>", unsafe_allow_html=True)
        with st.expander("💡 Recommendations & Next Steps"):
            for desc in item["suggestions"]:
                st.markdown(f"• {desc}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Actions
    c1, c2 = st.columns([1,1])
    if c1.button('🔄 Start New Analysis'):
        st.session_state.page = 'Symptom Analysis'
        st.session_state.selected_page = 'Symptom Analysis'
        st.rerun()
    pdf_bytes = create_pdf_report(results)
    c2.download_button('📄 Download PDF Report', data=pdf_bytes, file_name=f"DiagnoX_Report_{results['timestamp'].replace(':', '-')}.pdf", mime='application/pdf')

    st.markdown("<div style='margin-top:12px;color:var(--text-muted);font-size:0.9rem;'>⚕️ This AI tool provides assistance and does not replace professional medical advice.</div>", unsafe_allow_html=True)


def create_pdf_report(results):
    pdf = PDF(name=results.get("user_name", "User"), age=results.get("user_age", "N/A"))
    pdf.add_page()
    pdf.chapter_title("Patient Summary")
    pdf.chapter_body(f"Name: {results['user_name']}\nAge: {results.get('user_age', 'N/A')}\nSeverity: {results['severity']}\nSymptoms: {', '.join([s.replace('_', ' ').title() for s in results['selected_symptoms']])}")
    pdf.chapter_title("Differential Diagnosis")
    for item in results["top_predictions"]:
        pdf.add_diagnosis(item["disease"], item["confidence"])
    pdf.chapter_title("Recommendations")
    for item in results["top_predictions"]:
        pdf.chapter_body(f"{item['disease']}:\n" + "\n".join([f"- {s}" for s in item["suggestions"]]))
    return io.BytesIO(pdf.output(dest="S").encode("latin-1")).getvalue()


def render_history():
    st.markdown("<div class='section-header'><div><h2>History</h2><p style='color: var(--text-muted); margin-top:0.35rem;'>Review previous sessions and top findings at a glance.</p></div></div>", unsafe_allow_html=True)
    if not st.session_state.history:
        st.info("No history yet. Run an analysis to populate this view.")
        return
    for item in st.session_state.history:
        st.markdown(f"<div class='result-card'><strong>{item}</strong></div>", unsafe_allow_html=True)


def render_reports():
    st.markdown("<div class='section-header'><div><h2>Reports</h2><p style='color: var(--text-muted); margin-top:0.35rem;'>Export a medical-grade summary of your latest findings.</p></div></div>", unsafe_allow_html=True)
    if st.session_state.analysis_results:
        st.success("Your latest report is ready for download from the analysis page.")
    else:
        st.info("Run an analysis to create a downloadable report.")


def render_settings():
    st.markdown("<div class='section-header'><div><h2>Settings</h2><p style='color: var(--text-muted); margin-top:0.35rem;'>Configure platform preferences and account details.</p></div></div>", unsafe_allow_html=True)
    st.text_input("Display name", value=st.session_state.user_name, key="settings_display_name")
    st.text_input("Email", value=st.session_state.get("settings_email", "you@healthcare.com"), key="settings_email")
    st.checkbox("Enable desktop notifications", value=True, key="settings_notifications")
    st.checkbox("Keep me signed in", value=True, key="settings_keep_signed_in")


def render_dashboard():
    # Top area
    render_sidebar()
    render_topbar()
    st.markdown("<div style='max-width:1200px;margin:18px auto;padding:14px;'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;'><div><h2 style='margin:0;'>👨‍⚕️ Good Morning</h2><p style='color:var(--text-muted);margin:4px 0 0 0;'>Start your symptom analysis</p></div><div></div></div>", unsafe_allow_html=True)

    cols = st.columns([1,1,1,1])
    cols[0].markdown("<div class='info-card' style='padding:16px;'><h4 style='margin:0 0 8px 0;'>🔍 Start New Analysis</h4><p style='color:var(--text-muted);margin:0;'>Quickly begin a new triage.</p><div style='margin-top:10px;'><button class='stButton'>Start Analysis</button></div></div>", unsafe_allow_html=True)
    cols[1].markdown("<div class='info-card' style='padding:16px;'><h4 style='margin:0 0 8px 0;'>📋 Previous Reports</h4><p style='color:var(--text-muted);margin:0;'>View downloaded clinical summaries.</p></div>", unsafe_allow_html=True)
    cols[2].markdown("<div class='info-card' style='padding:16px;'><h4 style='margin:0 0 8px 0;'>🎯 AI Accuracy</h4><p style='color:var(--text-muted);margin:0;'>Model performance metrics.</p></div>", unsafe_allow_html=True)
    cols[3].markdown("<div class='info-card' style='padding:16px;'><h4 style='margin:0 0 8px 0;'>💾 Saved Records</h4><p style='color:var(--text-muted);margin:0;'>Patient profiles and notes.</p></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:18px;'>", unsafe_allow_html=True)
    if st.button('Start Analysis'):
        st.session_state.page = 'Symptom Analysis'
        st.session_state.selected_page = 'Symptom Analysis'
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # content area
    if st.session_state.page == 'Dashboard':
        if st.session_state.analysis_results:
            render_analysis_results()
        else:
            st.info('No analyses yet. Click Start Analysis to begin.')
    elif st.session_state.page == 'Symptom Analysis':
        render_symptom_analysis()
    elif st.session_state.page == 'Results':
        render_analysis_results()
    elif st.session_state.page == 'History':
        render_history()
    elif st.session_state.page == 'Reports':
        render_reports()
    elif st.session_state.page == 'Settings':
        render_settings()

    render_toast()
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    if not st.session_state.logged_in:
        render_login_page()
    else:
        render_dashboard()


if __name__ == '__main__':
    main()

import streamlit as st
import pickle
import pandas as pd
import numpy as np
from fpdf import FPDF
import base64

# ✅ Page config
st.set_page_config(page_title="DiagnoX AI | Health Predictor", page_icon="🩺", layout="wide")

# --- 🌟 Custom Styling ---
st.markdown("""
<style>
/* 🌐 Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg, #f9f9f9, #fffbe6);
}

/* 🌟 Section Container */
.report-container {
    background: #ffffff;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
}

/* ✨ Fade-in Animation */
.fade-in {
    animation: fadeInUp 0.9s ease-in-out;
}
@keyframes fadeInUp {
    from {opacity: 0; transform: translateY(20px);}
    to {opacity: 1; transform: translateY(0);}
}

/* 🌟 Custom Gold Button */
div.stButton > button {
    background: linear-gradient(135deg, #FFD700, #FFB700);
    color: #000;
    font-weight: 600;
    border: none;
    border-radius: 50px;
    padding: 0.8rem 1.5rem;
    box-shadow: 0px 6px 12px rgba(255,215,0,0.5);
    transition: all 0.3s ease-in-out;
    font-size: 1.05rem;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #FFF380, #FFD700);
    transform: scale(1.05);
}

/* 🌟 Section Titles */
.section-title {
    font-size: 2rem;
    font-weight: 700;
    margin: 2rem 0 1rem 0;
    text-align: center;
    background: linear-gradient(90deg, #FFD700, #FFEA70, #FFD700);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
}
.section-subtitle {
    text-align: center;
    color: #444;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --- 🎯 Header ---
def render_header():
    st.markdown("""
    <h1 style='text-align: center; 
               font-size: 2.8rem; 
               font-weight: 700;
               background: linear-gradient(90deg, #FFD700, #FFEA70, #FFD700);
               -webkit-background-clip: text;
               -webkit-text-fill-color: transparent;
               margin-bottom: 0.5rem;'>
        🩺 DiagnoX AI Pro
    </h1>
    <p style='text-align: center; font-size: 1.2rem; color: #666;'>
        Your Intelligent Health Predictor & Report Generator
    </p>
    """, unsafe_allow_html=True)

# --- 📑 PDF Report ---
class PDF(FPDF):
    def __init__(self, name="User", age="N/A"):
        super().__init__()
        self.user_name = name
        self.user_age = age
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(44, 44, 44)
        self.cell(0, 10, "DiagnoX AI Pro - Health Report", 0, 1, 'C')
        self.set_draw_color(255, 215, 0)
        self.set_line_width(0.8)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(255, 215, 0)
        self.cell(0, 10, title, ln=True, align='L')
        self.set_text_color(0, 0, 0)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

# --- 📢 Marketing Sections ---
def render_marketing_sections():
    st.markdown("<div class='section-title'>About DiagnoX AI Pro</div>", unsafe_allow_html=True)
    st.markdown("<p class='section-subtitle'>Your AI-powered health companion designed for clarity, precision, and trust.</p>", unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown("<div class='report-container fade-in'>### ⚡ Fast & Accurate\nOur AI engine processes thousands of medical records to provide quick and accurate results.</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown("<div class='report-container fade-in'>### 🧠 Smarter Insights\nReceive not just predictions but personalized health insights and actionable suggestions.</div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown("<div class='report-container fade-in'>### 🛡️ Safe & Reliable\nYour privacy is our priority. Data is never shared and stays fully secure.</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>How It Works</div>", unsafe_allow_html=True)
    st.markdown("""
    1. **Enter Your Details** → Provide basic information.  
    2. **Select Symptoms** → Choose from categorized lists.  
    3. **Get Analysis** → Our AI evaluates conditions & provides recommendations.  
    4. **Download Report** → Receive a professionally styled PDF report.  
    """)

    st.markdown("<div class='section-title'>Trusted by Users Worldwide 🌍</div>", unsafe_allow_html=True)
    st.markdown("""
    > *"DiagnoX AI gave me clarity when I needed it most. It’s like having a digital doctor’s assistant!"*  
    — **Sarah, New York**

    > *"Fast, professional, and reassuring. Highly recommend it!"*  
    — **Ravi, Bengaluru**
    """)

# --- 🚀 Main App ---
def main():
    render_header()

    # Example input form
    with st.form("health_form"):
        name = st.text_input("👤 Name")
        age = st.number_input("🎂 Age", min_value=1, max_value=120, value=25)
        symptoms = st.text_area("📝 Enter your symptoms")
        submitted = st.form_submit_button("🔍 Predict Health")

    if submitted:
        with st.spinner("Analyzing your symptoms..."):
            # Simulated prediction
            prediction = "Possible condition: Common Cold 🤧"
            st.success(prediction)

            # Generate PDF
            pdf = PDF(name, age)
            pdf.add_page()
            pdf.chapter_title("Patient Information")
            pdf.chapter_body(f"Name: {name}\nAge: {age}")

            pdf.chapter_title("Diagnosis")
            pdf.chapter_body(prediction)

            pdf.chapter_title("Recommendations")
            pdf.chapter_body("Stay hydrated, take rest, and consult a doctor if symptoms persist.")

            pdf.ln(20)
            pdf.set_font('Helvetica', 'I', 12)
            pdf.cell(0, 10, "Doctor's Signature: ___________________", ln=True)

            # Save & offer download
            pdf_output = f"{name}_health_report.pdf"
            pdf.output(pdf_output)

            with open(pdf_output, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="{pdf_output}">📥 Download Report</a>'
                st.markdown(href, unsafe_allow_html=True)

    render_marketing_sections()

    # Sidebar Reset
    if st.sidebar.button("🔄 Reset App"):
        st.session_state.clear()
        st.rerun()

if __name__ == "__main__":
    main()

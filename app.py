import streamlit as st
import random
import json
import streamlit.components.v1 as components
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Love Letter Generator", page_icon="💌", layout="centered")

# ---------- Google Sheets ----------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def get_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client.open("LoveLetters").sheet1

def log_entry(for_name: str, gender: str):
    """Log only timestamp + recipient name + gender. No letter."""
    try:
        get_sheet().append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            for_name,
            gender,
        ])
    except Exception as e:
        st.toast(f"⚠️ Could not save: {e}", icon="⚠️")

# ---------- Building blocks ----------
GREETINGS = ["Dear {name},", "Hey {name},", "My dearest {name},"]

COMPLIMENTS = [
    "You are {adjective} in every way.",
    "You're simply {adjective}.",
    "Everything about you is {adjective}.",
]

FEELINGS = [
    "I smile every time I think of you.",
    "You make my days brighter.",
    "My heart feels lighter around you.",
    "I'm so glad you exist.",
]

CLOSINGS = [
    "Forever my {nickname}.",
    "Always my {nickname}.",
    "You'll always be my {nickname}.",
]

SIGNOFFS = ["— With love", "— Yours always", "— Thinking of you"]

TERMS = {
    "her": {"adjective": ["beautiful", "gorgeous", "radiant"],
            "nickname":  ["princess", "queen", "angel"]},
    "him": {"adjective": ["handsome", "charming", "dashing"],
            "nickname":  ["prince", "king", "superstar"]},
}

def generate_letter(name: str, gender: str) -> str:
    t = TERMS[gender]
    adj  = random.choice(t["adjective"])
    nick = random.choice(t["nickname"])
    return "\n".join([
        random.choice(GREETINGS).format(name=name),
        "",
        random.choice(COMPLIMENTS).format(adjective=adj),
        random.choice(FEELINGS),
        "",
        random.choice(CLOSINGS).format(nickname=nick),
        random.choice(SIGNOFFS),
    ])

# ---------- UI ----------
st.title("💌 Love Letter Generator")
st.caption("Enter a name, pick a vibe, get a fresh short love letter.")

with st.form("input_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        name_input = st.text_input("Their name", placeholder="e.g. Sarah")
    with col2:
        gender_input = st.radio("Gender", ["Her 💕", "Him 💙"], horizontal=True)
    go = st.form_submit_button("💘 Generate Letter", use_container_width=True)

if go:
    if not name_input.strip():
        st.warning("Please enter a name first.")
    else:
        g = "her" if "Her" in gender_input else "him"
        st.session_state.for_name = name_input.strip()
        st.session_state.gender = g
        st.session_state.letter = generate_letter(st.session_state.for_name, g)
        log_entry(st.session_state.for_name, g)
        st.balloons()

# ---------- Output ----------
if "letter" in st.session_state:
    letter = st.session_state.letter
    st.divider()
    st.subheader(f"💖 For {st.session_state.for_name}")

    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #ffe0ec 0%, #fff5f8 100%);
            border-left: 6px solid #e91e63; border-radius: 12px;
            padding: 20px; font-size: 17px; line-height: 1.7;
            color: #333; font-family: Georgia, serif;
            white-space: pre-wrap;
            box-shadow: 0 4px 20px rgba(233,30,99,0.15);
        ">{letter}</div>
    """, unsafe_allow_html=True)

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        js_letter = json.dumps(letter)
        components.html(f"""
            <button onclick='navigator.clipboard.writeText({js_letter});
                             this.innerText="✅ Copied!";
                             setTimeout(()=>this.innerText="📋 Copy Letter",1800);'
                style="width:100%; padding:12px; background:#e91e63; color:white;
                       border:none; border-radius:8px; cursor:pointer;
                       font-size:15px; font-weight:600;">
                📋 Copy Letter
            </button>
        """, height=55)
    with c2:
        if st.button("🔄 New Letter", use_container_width=True):
            st.session_state.letter = generate_letter(
                st.session_state.for_name, st.session_state.gender
            )
            log_entry(st.session_state.for_name, st.session_state.gender)
            st.rerun()

    with st.expander("📄 Backup copy (manual)"):
        st.code(letter, language=None)
"""
Digital Heritage Archive
National Heritage Discovery Platform • Ministry of Culture
"""

import streamlit as st
from pathlib import Path
from config import ASSETS_DIR
from core.auth import get_current_user, is_logged_in, logout_user
from views.home import render_home
from views.search import render_search
from views.document_viewer import render_document_viewer
from views.ai_assistant import render_ai_assistant
from views.multilingual import render_multilingual
from views.timeline import render_timeline
from views.audiovisual import render_audiovisual
from views.institutional_upload import render_admin_upload
from views.login import render_login

# Configure Streamlit Page
st.set_page_config(
    page_title="Digital Heritage Archive",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load Custom Heritage Styling
css_file = ASSETS_DIR / "style.css"
if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. INITIAL AUTHENTICATION GATEWAY (LOGIN FIRST)
# -----------------------------------------------------------------------------
current_user = get_current_user()
is_guest = st.session_state.get("guest_mode", False)

# If the user has not authenticated and has not entered as guest, show ONLY the creative login screen
if not current_user and not is_guest:
    render_login()
    st.stop()

# -----------------------------------------------------------------------------
# 2. TOP GLOBAL HEADER NAVBAR (ACTIVE ONCE AUTHENTICATED / GUEST)
# -----------------------------------------------------------------------------
nav_col_logo, nav_col_links, nav_col_auth = st.columns([1.5, 2.6, 1.4], gap="small")

with nav_col_logo:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; padding: 4px 0;">
            <span style="font-size: 1.6rem;">🏛️</span>
            <div>
                <strong style="color: #fbbf24; font-family: 'Cinzel', serif; font-size: 1.05rem; letter-spacing: 0.04em;">
                    Digital Heritage Archive
                </strong><br/>
                <span style="color: #94a3b8; font-size: 0.72rem;">Ministry of Culture • Government of India</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_col_links:
    t_c1, t_c2, t_c3, t_c4, t_c5 = st.columns(5)
    with t_c1:
        if st.button("Home", key="top_nav_home", use_container_width=True):
            st.session_state["current_page"] = "Home"
            st.rerun()
    with t_c2:
        if st.button("Explore", key="top_nav_explore", use_container_width=True):
            st.session_state["current_page"] = "Search"
            st.rerun()
    with t_c3:
        if st.button("Timeline", key="top_nav_timeline", use_container_width=True):
            st.session_state["current_page"] = "Timeline"
            st.rerun()
    with t_c4:
        if st.button("Audio-Visual", key="top_nav_av", use_container_width=True):
            st.session_state["current_page"] = "Audio-Visual"
            st.rerun()
    with t_c5:
        if st.button("AI Assistant", key="top_nav_ai", use_container_width=True):
            st.session_state["current_page"] = "AI Assistant"
            st.rerun()

with nav_col_auth:
    if current_user:
        u_col1, u_col2 = st.columns([2.0, 1.2])
        with u_col1:
            if st.button(
                f"{current_user.get('avatar', '👤')} {current_user.get('name', 'Scholar').split()[0]}",
                key="top_profile_btn",
                help=f"Logged in as {current_user.get('role')}",
                use_container_width=True,
            ):
                st.session_state["current_page"] = "Login"
                st.rerun()
        with u_col2:
            if st.button("Sign Out", key="top_logout_btn", type="secondary", use_container_width=True):
                logout_user()
                st.rerun()
    else:
        u_col1, u_col2 = st.columns([1.8, 1.4])
        with u_col1:
            st.markdown("<div style='padding-top:6px; font-size:0.82rem; color:#94a3b8;'>👤 Guest Mode</div>", unsafe_allow_html=True)
        with u_col2:
            if st.button("🔑 Login", key="top_login_btn", type="primary", use_container_width=True):
                st.session_state["guest_mode"] = False
                st.session_state["current_page"] = "Login"
                st.rerun()

st.markdown("<hr style='margin: 8px 0 20px 0; border-color: rgba(212, 175, 55, 0.2);'/>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION HUB
# -----------------------------------------------------------------------------
st.sidebar.markdown(
    """
    <div style="padding: 5px 0 10px 0;">
        <h2 style="color: #fbbf24; margin: 0; font-family: 'Cinzel', serif; font-size: 1.25rem;">
            🏛️ Heritage Archive
        </h2>
        <p style="color: #94a3b8; font-size: 0.78rem; margin: 2px 0 0 0;">
            National Archival Discovery Platform
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if current_user:
    st.sidebar.markdown(
        f"""
        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid {current_user.get('badge_color', '#fbbf24')}; border-radius: 8px; padding: 10px; margin-bottom: 12px;">
            <div style="font-size: 0.75rem; color: {current_user.get('badge_color', '#fbbf24')}; font-weight: 700; text-transform: uppercase;">
                {current_user.get('role_badge', '👤 Active Session')}
            </div>
            <strong style="color: #fef08a; font-size: 0.92rem;">{current_user.get('name')}</strong><br/>
            <span style="color: #94a3b8; font-size: 0.75rem;">{current_user.get('institution')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Navigation Menu Configuration
nav_items = [
    ("🏠 Home Hub", "Home"),
    ("🔍 Smart Search", "Search"),
    ("📜 Document Viewer", "Document Viewer"),
    ("🤖 AI Assistant", "AI Assistant"),
    ("🌐 Multilingual Access", "Multilingual Access"),
    ("⏳ Heritage Timeline", "Timeline"),
    ("🎙️ Audio-Visual", "Audio-Visual"),
    ("🏛️ Institutional Admin", "Admin"),
    ("🔐 Scholar Portal", "Login"),
]

valid_pages = [item[1] for item in nav_items]

# Synchronize active page in session state
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

# Consume any pending programmatic navigation target
target_page = (
    st.session_state.pop("nav_target", None)
    or st.session_state.pop("sidebar_nav_radio", None)
    or st.session_state.pop("target_page", None)
)
if target_page and target_page in valid_pages:
    st.session_state["current_page"] = target_page

if st.session_state["current_page"] not in valid_pages:
    st.session_state["current_page"] = "Home"

current_page = st.session_state["current_page"]

# Render Sidebar Navigation Buttons
st.sidebar.markdown(
    """
    <div style="font-size: 0.82rem; font-weight: 700; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.08em; margin: 5px 0 8px 0;">
        🧭 Navigation Hub:
    </div>
    """,
    unsafe_allow_html=True,
)

for label, page_key in nav_items:
    display_label = label
    if page_key == "Login" and current_user:
        display_label = f"👤 Profile ({current_user.get('name').split()[0]})"

    is_active = (current_page == page_key)
    btn_type = "primary" if is_active else "secondary"
    if st.sidebar.button(display_label, key=f"sidebar_nav_btn_{page_key}", type=btn_type, use_container_width=True):
        if st.session_state["current_page"] != page_key:
            st.session_state["current_page"] = page_key
            st.rerun()

menu = current_page

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="background: rgba(15, 23, 42, 0.7); padding: 10px; border-radius: 6px; border-left: 3px solid #fbbf24; font-size: 0.78rem; color: #cbd5e1;">
        <strong style="color: #fbbf24;">💡 Core Capabilities:</strong><br/>
        • <strong>Search</strong>: FAISS Dense Vector Search<br/>
        • <strong>Viewer</strong>: 13-Point Archival Inspector<br/>
        • <strong>AI Assistant</strong>: Source-Grounded RAG<br/>
        • <strong>Multilingual</strong>: English • Hindi • Kannada • Tamil<br/>
        • <strong>Audio-Visual</strong>: Image • Audio • Video<br/>
        • <strong>Admin</strong>: Preprocess & Multi-OCR
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.caption("National Heritage Archive • Ministry of Culture")

# -----------------------------------------------------------------------------
# 4. ROUTE TO SELECTED PAGE
# -----------------------------------------------------------------------------
if menu == "Home":
    render_home()

elif menu == "Search":
    render_search()

elif menu == "Document Viewer":
    render_document_viewer()

elif menu == "AI Assistant":
    render_ai_assistant()

elif menu == "Multilingual Access":
    render_multilingual()

elif menu == "Timeline":
    render_timeline()

elif menu == "Audio-Visual":
    render_audiovisual()

elif menu == "Admin":
    render_admin_upload()

elif menu == "Login":
    render_login()

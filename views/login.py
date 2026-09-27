"""
Digital Heritage Archive - Full-Screen Creative Heritage Login Portal
Features full-page Dr. B. R. Ambedkar archival background wallpaper,
centered frosted glassmorphism login card, Dublin Core branding, SSO, and 1-click role switcher.
"""

import streamlit as st
import base64
from pathlib import Path
from config import ASSETS_DIR
from core.auth import (
    get_current_user,
    is_logged_in,
    login_user,
    register_user,
    logout_user,
    DEMO_ACCOUNTS,
)


def get_image_base64(image_path: Path) -> str:
    """Encodes an image file to a base64 string for CSS background rendering."""
    if image_path.exists():
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def render_login():
    """Renders the creative heritage login screen matching the reference layout."""
    current_user = get_current_user()

    # If already logged in, provide profile management & quick jump to archive
    if current_user:
        _render_authenticated_profile(current_user)
        return

    # -------------------------------------------------------------------------
    # 1. FULL-SCREEN BACKGROUND WALLPAPER & GLASSMORPHIC STYLING
    # -------------------------------------------------------------------------
    bg_wallpaper_path = ASSETS_DIR / "heritage_login_wallpaper.jpg"
    if not bg_wallpaper_path.exists():
        bg_wallpaper_path = ASSETS_DIR / "heritage_login_bg.jpg"

    b64_bg = get_image_base64(bg_wallpaper_path)

    bg_css = f"""
    <style>
    /* Hide sidebar and collapsed controls on the initial Login Screen */
    [data-testid="stSidebar"] {{
        display: none !important;
    }}
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}
    
    /* Full-Screen Heritage Backdrop with Dr. Ambedkar face clear in upper half */
    .stApp {{
        background: linear-gradient(rgba(10, 15, 29, 0.15), rgba(5, 7, 13, 0.60)),
                    url('data:image/jpeg;base64,{b64_bg}') no-repeat center top fixed !important;
        background-size: cover !important;
    }}
    
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    .login-top-spacer {{
        height: 110px;
    }}

    .auth-glass-box {{
        background: rgba(15, 23, 42, 0.82) !important;
        border: 1px solid rgba(251, 191, 36, 0.4) !important;
        border-radius: 18px !important;
        padding: 26px 28px !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.75), 0 0 35px rgba(251, 191, 36, 0.12) !important;
        text-align: center;
        margin-bottom: 16px;
    }}

    .auth-logo-pillar {{
        font-size: 2.6rem;
        line-height: 1;
        margin-bottom: 6px;
        text-shadow: 0 0 25px rgba(251, 191, 36, 0.6);
    }}

    .auth-main-title {{
        font-family: 'Cinzel', serif !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #fef08a !important;
        margin: 4px 0 2px 0 !important;
        letter-spacing: 0.04em !important;
        text-shadow: 0 2px 12px rgba(212, 175, 55, 0.4) !important;
    }}

    .auth-motto {{
        font-size: 0.78rem !important;
        color: #94a3b8 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        margin-bottom: 18px !important;
    }}

    .auth-welcome-heading {{
        font-family: 'Cinzel', serif !important;
        font-size: 1.45rem !important;
        color: #fbbf24 !important;
        margin: 0 0 4px 0 !important;
    }}

    .auth-welcome-sub {{
        font-size: 0.88rem !important;
        color: #cbd5e1 !important;
        margin-bottom: 16px !important;
    }}

    .sso-separator {{
        display: flex;
        align-items: center;
        text-align: center;
        margin: 18px 0 14px 0;
        color: #64748b;
        font-size: 0.78rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }}

    .sso-separator::before,
    .sso-separator::after {{
        content: '';
        flex: 1;
        border-bottom: 1px solid rgba(212, 175, 55, 0.25);
    }}

    .sso-separator:not(:empty)::before {{
        margin-right: .8em;
    }}

    .sso-separator:not(:empty)::after {{
        margin-left: .8em;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. CENTERED GLASSMORPHIC LOGIN CARD (BELOW PORTRAIT FACE)
    # -------------------------------------------------------------------------
    st.markdown("<div class='login-top-spacer'></div>", unsafe_allow_html=True)

    col_left, col_card, col_right = st.columns([0.65, 1.7, 0.65])

    with col_card:
        # Card Header Branding
        st.markdown(
            """
            <div class="auth-glass-box">
                <div class="auth-logo-pillar">🏛️</div>
                <div class="auth-main-title">Digital Heritage Archive</div>
                <div class="auth-motto">
                    Preserving History &nbsp;|&nbsp; Enabling Knowledge &nbsp;|&nbsp; Inspiring Generations
                </div>
                <div class="auth-welcome-heading">Welcome</div>
                <div class="auth-welcome-sub">
                    Login to explore our digital heritage collection
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Authentication Mode Tabs
        tab_login, tab_roles, tab_signup = st.tabs([
            "🔑 Sign In",
            "⚡ 1-Click Roles",
            "✨ Create Account",
        ])

        # ---------------------------------------------------------------------
        # TAB 1: Main Sign In Form
        # ---------------------------------------------------------------------
        with tab_login:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            with st.form("main_auth_form", clear_on_submit=False):
                email_input = st.text_input(
                    "Email Address",
                    value="archivist@heritage.gov.in",
                    placeholder="Enter institutional email",
                    help="Default: archivist@heritage.gov.in / heritage2026",
                )
                password_input = st.text_input(
                    "Password",
                    value="heritage2026",
                    type="password",
                    placeholder="Enter your archive password",
                )

                col_chk, col_fpass = st.columns([1, 1])
                with col_chk:
                    rem_box = st.checkbox("Remember me", value=True)
                with col_fpass:
                    st.markdown(
                        "<div style='text-align: right; padding-top: 4px;'><span style='color: #fbbf24; font-size: 0.82rem; cursor: pointer;'>Forgot Password?</span></div>",
                        unsafe_allow_html=True,
                    )

                submit_btn = st.form_submit_button(
                    "Login",
                    type="primary",
                    use_container_width=True,
                )

                if submit_btn:
                    res = login_user(email=email_input, password=password_input)
                    if res["success"]:
                        st.success(res["message"])
                        st.session_state["current_page"] = "Home"
                        st.rerun()
                    else:
                        st.error(res["message"])

            # Single Sign-On (SSO) Row
            st.markdown(
                """
                <div class="sso-separator">
                    or continue with
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                if st.button("🌐 Google", key="sso_g_login", use_container_width=True):
                    login_user("scholar.google@delhi.ac.in", bypass_password=True)
                    st.session_state["current_page"] = "Home"
                    st.rerun()
            with col_s2:
                if st.button("🏢 Microsoft", key="sso_m_login", use_container_width=True):
                    login_user("scholar.ms@university.edu", bypass_password=True)
                    st.session_state["current_page"] = "Home"
                    st.rerun()
            with col_s3:
                if st.button("🇮🇳 DigiLocker", key="sso_d_login", use_container_width=True):
                    login_user("archivist@heritage.gov.in", bypass_password=True)
                    st.session_state["current_page"] = "Home"
                    st.rerun()

            # Guest Explore / Home Direct Access
            st.markdown("<hr style='margin: 16px 0; border-color: rgba(255, 255, 255, 0.08);'/>", unsafe_allow_html=True)
            if st.button(
                "🏛️ Explore Archive as Guest (Continue to Home) ➔",
                key="btn_guest_enter",
                type="secondary",
                use_container_width=True,
            ):
                st.session_state["guest_mode"] = True
                st.session_state["current_page"] = "Home"
                st.rerun()

        # ---------------------------------------------------------------------
        # TAB 2: 1-Click Quick Demo Roles
        # ---------------------------------------------------------------------
        with tab_roles:
            st.markdown(
                """
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 8px; padding: 12px; margin: 10px 0; font-size: 0.84rem; color: #cbd5e1;">
                    💡 <strong>Institutional Scholar Access:</strong> Select any pre-configured archival role below for instant authenticated access.
                </div>
                """,
                unsafe_allow_html=True,
            )

            for email_acc, data_acc in DEMO_ACCOUNTS.items():
                r_c1, r_c2 = st.columns([2.0, 1.2])
                with r_c1:
                    st.markdown(
                        f"""
                        <div style="margin-bottom: 6px;">
                            <strong style="color: {data_acc['badge_color']}; font-size: 0.95rem;">
                                {data_acc['avatar']} {data_acc['name']}
                            </strong><br/>
                            <span style="color: #94a3b8; font-size: 0.78rem;">
                                {data_acc['role']}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with r_c2:
                    if st.button(
                        f"Enter as {data_acc['role'].split()[0]}",
                        key=f"demo_role_btn_{email_acc}",
                        type="primary" if "Chief" in data_acc["role"] else "secondary",
                        use_container_width=True,
                    ):
                        login_user(email_acc, bypass_password=True)
                        st.session_state["current_page"] = "Home"
                        st.rerun()
                st.markdown("<hr style='margin: 6px 0; border-color: rgba(255,255,255,0.06);'/>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # TAB 3: New Scholar Registration
        # ---------------------------------------------------------------------
        with tab_signup:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            with st.form("new_scholar_reg_form"):
                n_name = st.text_input("Full Name", placeholder="e.g. Dr. Rajeshwari Sundaram")
                n_email = st.text_input("Institutional Email", placeholder="e.g. rajeshwari@jnu.ac.in")
                n_inst = st.text_input("University / Research Institution", placeholder="e.g. Jawaharlal Nehru University")
                n_role = st.selectbox(
                    "Academic Role",
                    ["Historical Researcher", "Archivist / Curator", "University Faculty", "Postgraduate Scholar", "Independent Historian"],
                )
                n_pass = st.text_input("Password", type="password", placeholder="Create secure password")

                reg_btn = st.form_submit_button("Create Scholar Account", type="primary", use_container_width=True)
                if reg_btn:
                    res = register_user(
                        name=n_name,
                        email=n_email,
                        password=n_pass,
                        institution=n_inst,
                        role=n_role,
                    )
                    if res["success"]:
                        st.success(res["message"])
                        st.session_state["current_page"] = "Home"
                        st.rerun()
                    else:
                        st.error(res["message"])


def _render_authenticated_profile(user):
    """Renders the profile view when the user navigates to Scholar Portal after logging in."""
    st.markdown(
        f"""
        <div class="auth-glass-card" style="border-left: 6px solid {user.get('badge_color', '#fbbf24')};">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span class="auth-brand-badge" style="border-color: {user.get('badge_color', '#fbbf24')}; color: {user.get('badge_color', '#fbbf24')};">
                        {user.get('role_badge', '👤 Scholar')}
                    </span>
                    <h2 style="margin: 6px 0 2px 0; color: #fef08a; font-family: 'Cinzel', serif;">
                        {user.get('name', 'Scholar')}
                    </h2>
                    <p style="color: #94a3b8; font-size: 0.88rem; margin: 0;">
                        🏛️ <strong>Affiliation:</strong> {user.get('institution', 'National Heritage Archive')} | 📧 <strong>Email:</strong> {user.get('email', '')}
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_acts, c_perms = st.columns([1.5, 1.0], gap="large")

    with c_acts:
        st.subheader("⚡ Quick Navigation")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Return to Home Hub", type="primary", use_container_width=True):
                st.session_state["current_page"] = "Home"
                st.rerun()
            if st.button("🔍 Smart Search", use_container_width=True):
                st.session_state["current_page"] = "Search"
                st.rerun()
            if st.button("🤖 AI Assistant", use_container_width=True):
                st.session_state["current_page"] = "AI Assistant"
                st.rerun()
        with c2:
            if st.button("📜 Document Viewer", use_container_width=True):
                st.session_state["current_page"] = "Document Viewer"
                st.rerun()
            if st.button("🎙️ Audio-Visual Gallery", use_container_width=True):
                st.session_state["current_page"] = "Audio-Visual"
                st.rerun()
            if st.button("⏳ Timeline", use_container_width=True):
                st.session_state["current_page"] = "Timeline"
                st.rerun()

        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out of Archive Session", type="secondary"):
            logout_user()
            st.rerun()

    with c_perms:
        st.subheader("🛡️ Active Scholar Clearance")
        perms = user.get("permissions", [])
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; padding: 18px; line-height: 1.8; color: #cbd5e1; font-size: 0.85rem;">
                {'✅' if 'view' in perms else '❌'} High-Resolution Document Inspection<br/>
                {'✅' if 'ai_assistant' in perms else '❌'} Source-Grounded RAG Inquiries<br/>
                {'✅' if 'multilingual' in perms else '❌'} Indic Multilingual Translation<br/>
                {'✅' if 'audiovisual' in perms else '❌'} Audio & Video Playback & Transcripts<br/>
                {'✅' if 'admin_upload' in perms else '❌'} Institutional Ingestion & Multi-OCR<br/>
            </div>
            """,
            unsafe_allow_html=True,
        )

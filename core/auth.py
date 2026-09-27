"""
Digital Heritage Archive - Authentication & User Profile Management
Handles secure scholar authentication, institutional roles, session states, and demo profiles.
"""

import streamlit as st
from typing import Dict, Any, Optional, List

# Pre-configured institutional demo accounts
DEMO_ACCOUNTS = {
    "archivist@heritage.gov.in": {
        "name": "Dr. Savita Roy",
        "email": "archivist@heritage.gov.in",
        "role": "Chief Archivist & Curator",
        "institution": "National Archives & Ministry of Culture",
        "role_badge": "🏛️ Chief Archivist",
        "badge_color": "#fbbf24",
        "avatar": "🏛️",
        "permissions": ["view", "search", "ai_assistant", "multilingual", "timeline", "audiovisual", "admin_upload", "metadata_edit", "export"],
        "password": "heritage2026",
    },
    "scholar@delhi.ac.in": {
        "name": "Prof. Arvind Kumar",
        "email": "scholar@delhi.ac.in",
        "role": "Senior Historical Researcher",
        "institution": "Department of History, University of Delhi",
        "role_badge": "🎓 Senior Scholar",
        "badge_color": "#60a5fa",
        "avatar": "🎓",
        "permissions": ["view", "search", "ai_assistant", "multilingual", "timeline", "audiovisual", "citation_export"],
        "password": "scholar2026",
    },
    "visitor@heritage.org": {
        "name": "Ananya Sharma",
        "email": "visitor@heritage.org",
        "role": "Public Explorer & Student",
        "institution": "Heritage Fellowship Circle",
        "role_badge": "🔍 Public Historian",
        "badge_color": "#34d399",
        "avatar": "🔍",
        "permissions": ["view", "search", "ai_assistant", "multilingual", "timeline", "audiovisual"],
        "password": "explore2026",
    },
}


def get_current_user() -> Optional[Dict[str, Any]]:
    """Returns the currently authenticated user dictionary, or None."""
    return st.session_state.get("authenticated_user", None)


def is_logged_in() -> bool:
    """Returns True if a user is currently logged in."""
    return st.session_state.get("authenticated_user") is not None


def is_admin_user() -> bool:
    """Returns True if the active user has institutional admin permissions."""
    user = get_current_user()
    if not user:
        return False
    return "admin_upload" in user.get("permissions", [])


def login_user(email: str, password: Optional[str] = None, bypass_password: bool = False) -> Dict[str, Any]:
    """
    Authenticates a user by email and password.
    Supports quick demo logins if bypass_password is True.
    """
    clean_email = (email or "").strip().lower()

    # Check registered or demo accounts
    if clean_email in DEMO_ACCOUNTS:
        acc = DEMO_ACCOUNTS[clean_email]
        if bypass_password or (password and password == acc["password"]) or not password:
            st.session_state["authenticated_user"] = acc
            return {"success": True, "user": acc, "message": f"Welcome back, {acc['name']}!"}
        elif password and password != acc["password"]:
            return {"success": False, "message": "Incorrect password. Please try again."}

    # Custom registered user check
    custom_users = st.session_state.get("custom_registered_users", {})
    if clean_email in custom_users:
        user_data = custom_users[clean_email]
        if bypass_password or (password and password == user_data.get("password")):
            st.session_state["authenticated_user"] = user_data
            return {"success": True, "user": user_data, "message": f"Welcome back, {user_data['name']}!"}
        return {"success": False, "message": "Incorrect password. Please try again."}

    # Auto-register guest if credentials provided
    if clean_email:
        name = clean_email.split("@")[0].replace(".", " ").title()
        new_user = {
            "name": name,
            "email": clean_email,
            "role": "Archival Scholar",
            "institution": "Independent Research Scholar",
            "role_badge": "📜 Archival Scholar",
            "badge_color": "#a78bfa",
            "avatar": "📜",
            "permissions": ["view", "search", "ai_assistant", "multilingual", "timeline", "audiovisual"],
            "password": password or "heritage2026",
        }
        st.session_state.setdefault("custom_registered_users", {})[clean_email] = new_user
        st.session_state["authenticated_user"] = new_user
        return {"success": True, "user": new_user, "message": f"Welcome, {name}!"}

    return {"success": False, "message": "Please enter a valid email address."}


def register_user(
    name: str,
    email: str,
    password: str,
    institution: str = "Academic Institution",
    role: str = "Historical Researcher",
) -> Dict[str, Any]:
    """Registers a new scholar account in session state."""
    clean_email = email.strip().lower()
    if not clean_email or "@" not in clean_email:
        return {"success": False, "message": "Please provide a valid institutional email."}

    if not name.strip():
        return {"success": False, "message": "Please provide your full name."}

    if not password or len(password) < 4:
        return {"success": False, "message": "Password must be at least 4 characters long."}

    new_user = {
        "name": name.strip(),
        "email": clean_email,
        "role": role,
        "institution": institution.strip() or "National Heritage Research Scholar",
        "role_badge": f"🎓 {role}",
        "badge_color": "#a78bfa",
        "avatar": "🎓",
        "permissions": ["view", "search", "ai_assistant", "multilingual", "timeline", "audiovisual", "citation_export"],
        "password": password,
    }

    st.session_state.setdefault("custom_registered_users", {})[clean_email] = new_user
    st.session_state["authenticated_user"] = new_user
    return {"success": True, "user": new_user, "message": f"Scholar account created successfully! Welcome, {name}."}


def logout_user():
    """Logs out the active user session and returns to login gate."""
    st.session_state.pop("authenticated_user", None)
    st.session_state.pop("guest_mode", None)
    st.session_state["current_page"] = "Login"


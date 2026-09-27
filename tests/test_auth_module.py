"""
Digital Heritage Archive - Authentication & Login Module Test
Verifies scholar authentication, demo roles, password validation, and permissions.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.auth import (
    login_user,
    register_user,
    logout_user,
    get_current_user,
    is_logged_in,
    is_admin_user,
    DEMO_ACCOUNTS,
)


def test_auth_pipeline():
    print("--- 1. Testing Demo User Logins ---")
    # Test Chief Archivist Login
    archivist_res = login_user("archivist@heritage.gov.in", "heritage2026")
    assert archivist_res["success"] is True, "Chief Archivist login must succeed"
    assert is_logged_in() is True
    assert is_admin_user() is True
    user = get_current_user()
    assert user["name"] == "Dr. Savita Roy"
    assert "admin_upload" in user["permissions"]
    print(f"    [OK] Archivist Logged In: {user['name']} ({user['role']})")

    # Test Senior Scholar Login
    scholar_res = login_user("scholar@delhi.ac.in", "scholar2026")
    assert scholar_res["success"] is True
    user = get_current_user()
    assert user["name"] == "Prof. Arvind Kumar"
    assert is_admin_user() is False
    print(f"    [OK] Scholar Logged In: {user['name']} ({user['role']})")

    # Test Incorrect Password
    bad_pwd_res = login_user("scholar@delhi.ac.in", "wrongpassword")
    assert bad_pwd_res["success"] is False, "Incorrect password must be rejected"
    print(f"    [OK] Incorrect password rejected properly.")

    # Test Scholar Registration
    print("--- 2. Testing Scholar Registration ---")
    reg_res = register_user(
        name="Dr. Radhika Menon",
        email="radhika@heritage-res.org",
        password="securepassword2026",
        institution="National Museum Institute",
        role="Manuscript Conservator",
    )
    assert reg_res["success"] is True, "New scholar registration must succeed"
    new_user = get_current_user()
    assert new_user["name"] == "Dr. Radhika Menon"
    print(f"    [OK] New Scholar Registered: {new_user['name']}")

    # Test Logout
    logout_user()
    assert is_logged_in() is False
    assert get_current_user() is None
    print(f"    [OK] User Logged Out Successfully.")


if __name__ == "__main__":
    test_auth_pipeline()
    print("\n[SUCCESS] All Auth Module Tests Passed!")

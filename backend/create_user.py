"""
Create an application user.

Usage:

    python -m backend.create_user security_analyst SECURITY_ANALYST
    python -m backend.create_user auditor AUDITOR
"""

from __future__ import annotations

import getpass
import sys

from backend.app.services.users import create_user

ALLOWED_ROLES = {
    "SECURITY_ADMIN",
    "SECURITY_ANALYST",
    "AUDITOR",
}


def main() -> None:

    if len(sys.argv) != 3:
        print("Usage: python -m backend.create_user " "<username> <role>")
        sys.exit(1)

    username = sys.argv[1]
    role = sys.argv[2].upper()

    if role not in ALLOWED_ROLES:
        print(f"Invalid role: {role}")
        print("Allowed roles:")

        for allowed_role in sorted(ALLOWED_ROLES):
            print(f"  - {allowed_role}")

        sys.exit(1)

    password = getpass.getpass("Password: ")
    password_confirmation = getpass.getpass("Confirm password: ")

    if password != password_confirmation:
        print("Passwords do not match.")
        sys.exit(1)

    # bcrypt supports a maximum of 72 bytes.
    if len(password.encode("utf-8")) > 72:
        print(
            "Password is too long for bcrypt. " "Use a password of 72 bytes or fewer."
        )
        sys.exit(1)

    try:

        user = create_user(
            username=username,
            password=password,
            role=role,
        )

    except Exception as exc:

        print(f"Failed to create user: {exc}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("USER CREATED")
    print("=" * 60)
    print(f"Username : {user['username']}")
    print(f"Role     : {user['role']}")
    print(f"Active   : {user['is_active']}")
    print(f"User ID  : {user['user_id']}")


if __name__ == "__main__":
    main()

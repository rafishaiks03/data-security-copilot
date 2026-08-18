"""
Create the initial administrator account.
"""

from backend.app.services.users import create_user


def main() -> None:

    username = "admin"
    password = "admin123"

    user = create_user(
        username=username,
        password=password,
        role="ADMIN",
    )

    print()
    print("=" * 60)
    print("Administrator created successfully")
    print("=" * 60)
    print(f"User ID : {user['user_id']}")
    print(f"Username: {user['username']}")
    print(f"Role    : {user['role']}")
    print(f"Active  : {user['is_active']}")
    print("=" * 60)


if __name__ == "__main__":
    main()

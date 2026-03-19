"""
Simple auth — no DB check needed.
Admin: admin / admin123
Customer: any username / any password
"""
from backend.models.schemas import LoginRequest, LoginResponse

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def login(request: LoginRequest) -> LoginResponse:
    username = request.username.strip()
    password = request.password.strip()

    if not username:
        return LoginResponse(success=False, role="", username="", message="Username required")

    # Admin check
    if username.lower() == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return LoginResponse(
            success=True, role="admin",
            username=username,
            message=f"Welcome back, Admin!"
        )

    # Customer — any credentials work
    if len(username) >= 2:
        return LoginResponse(
            success=True, role="customer",
            username=username,
            message=f"Welcome, {username}!"
        )

    return LoginResponse(success=False, role="", username="", message="Username too short")

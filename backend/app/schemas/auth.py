"""
Pydantic schemas for authentication.
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """
    Login credentials.
    """

    username: str = Field(
        min_length=1,
        max_length=100,
    )

    password: str = Field(
        min_length=1,
        max_length=200,
    )


class TokenResponse(BaseModel):
    """
    JWT access token response.
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int

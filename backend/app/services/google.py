from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings


class GoogleService:
    """Service for Google OAuth integration"""

    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.base_url = "https://www.googleapis.com"
        self.auth_url = "https://accounts.google.com"

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> str:
        """Exchange authorization code for access token"""
        if not self.client_id or not self.client_secret:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/o/oauth2/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Failed to exchange code for token"
                )

            data = response.json()
            if "error" in data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Google error: {data.get('error_description', data['error'])}",
                )

            return data["access_token"]

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """Get user information from Google"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/oauth2/v2/userinfo",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Failed to get user info from Google"
                )

            return response.json()

    def get_oauth_url(self, redirect_uri: str, state: str | None = None) -> str:
        """Get Google OAuth URL"""
        if not self.client_id:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
        }

        if state:
            params["state"] = state

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}/o/oauth2/auth?{query_string}"

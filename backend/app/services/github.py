from typing import Any

import httpx
from fastapi import HTTPException

from app.core.config import settings


class GitHubService:
    """Service for GitHub OAuth and API integration"""

    def __init__(self):
        self.client_id = settings.GITHUB_CLIENT_ID
        self.client_secret = settings.GITHUB_CLIENT_SECRET
        self.base_url = "https://api.github.com"
        self.auth_url = "https://github.com/login/oauth"

    async def exchange_code_for_token(self, code: str) -> str:
        """Exchange authorization code for access token"""
        if not self.client_id or not self.client_secret:
            raise HTTPException(status_code=500, detail="GitHub OAuth not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/access_token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Failed to exchange code for token"
                )

            data = response.json()
            if "error" in data:
                raise HTTPException(
                    status_code=400, detail=f"GitHub error: {data['error_description']}"
                )

            return data["access_token"]

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        """Get user information from GitHub"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/user",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Failed to get user info from GitHub"
                )

            return response.json()

    async def get_user_repos(self, access_token: str) -> list:
        """Get user repositories from GitHub"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/user/repos",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                params={"sort": "updated", "per_page": 100},
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Failed to get repositories from GitHub"
                )

            return response.json()

    async def get_repo_issues(self, access_token: str, owner: str, repo: str) -> list:
        """Get repository issues from GitHub"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                params={"state": "all", "per_page": 100},
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, detail="Failed to get issues from GitHub"
                )

            return response.json()

    async def create_webhook(
        self, access_token: str, owner: str, repo: str, webhook_url: str, secret: str
    ) -> dict[str, Any]:
        """Create a webhook for repository events"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/repos/{owner}/{repo}/hooks",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                json={
                    "name": "web",
                    "active": True,
                    "events": ["issues", "issue_comment", "pull_request"],
                    "config": {
                        "url": webhook_url,
                        "content_type": "json",
                        "secret": secret,
                    },
                },
            )

            if response.status_code not in [200, 201]:
                raise HTTPException(status_code=400, detail="Failed to create webhook")

            return response.json()

    async def delete_webhook(
        self, access_token: str, owner: str, repo: str, hook_id: str
    ) -> bool:
        """Delete a webhook"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/repos/{owner}/{repo}/hooks/{hook_id}",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            return response.status_code == 204

    def get_oauth_url(self, state: str | None = None) -> str:
        """Get GitHub OAuth URL"""
        if not self.client_id:
            raise HTTPException(status_code=500, detail="GitHub OAuth not configured")

        params = {
            "client_id": self.client_id,
            "scope": "repo user",
        }

        if state:
            params["state"] = state

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}/authorize?{query_string}"

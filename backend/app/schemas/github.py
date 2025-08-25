from typing import Any

from pydantic import BaseModel


class GitHubAuthRequest(BaseModel):
    code: str
    state: str | None = None


class GitHubWebhookPayload(BaseModel):
    action: str | None = None
    issue: dict[str, Any] | None = None
    pull_request: dict[str, Any] | None = None
    comment: dict[str, Any] | None = None
    repository: dict[str, Any] | None = None
    sender: dict[str, Any] | None = None


class GitHubRepoInfo(BaseModel):
    id: str
    name: str
    full_name: str
    owner: str
    description: str | None = None
    private: bool
    html_url: str
    clone_url: str


class GitHubIssueInfo(BaseModel):
    id: str
    number: int
    title: str
    body: str | None = None
    state: str
    assignee: dict[str, Any] | None = None
    labels: list
    created_at: str
    updated_at: str
    closed_at: str | None = None

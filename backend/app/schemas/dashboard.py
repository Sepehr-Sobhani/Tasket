from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_projects: int
    unique_team_members: int
    active_projects: int

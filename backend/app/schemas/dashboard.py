from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_projects: int
    unique_team_members: int
    total_tasks: int
    active_projects: int 
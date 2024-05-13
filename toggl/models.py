from datetime import datetime, timedelta, timezone
import json
from typing import Optional
from pydantic import BaseModel, Field

with open("projects.json", "r") as f:
    project_objs: list = json.load(f)


class TimeEntry(BaseModel):
    at: str
    description: str
    duration: int
    id: int
    project_id: Optional[int]
    start: str
    stop: Optional[str]
    workspace_id: int
    tags: list[str]

    def __str__(self):
        if self.stop:
            return f"Time Entry({self.description}, project_id:{self.project_id}, from {self.start} to {self.stop})"
        else:
            return f"Time Entry({self.description}, project_id:{self.project_id}, started at {self.start})"

    def llm_repr(self):
        start = datetime.fromisoformat(self.start)
        start = start.astimezone(tz=timezone(timedelta(hours=2)))
        start = start.strftime("%Y-%m-%d %H:%M:%S")
        if self.stop:
            stop = datetime.fromisoformat(self.stop)
            stop = stop.astimezone(tz=timezone(timedelta(hours=2)))
            stop = stop.strftime("%Y-%m-%d %H:%M:%S")
            return f'(TogglDescription:"{self.description}", from {start} to {stop})'
        else:
            return f'(TogglDescripton:"{self.description}", started at {start})'


class StartTimeEntryArgs(BaseModel):
    title: str = Field(description="The title of the time-entry.")
    project_name: Optional[str] = Field(
        default=None, description="The name of the project the time-entry belongs to."
    )
    start: str = Field(
        default=datetime.now().isoformat(timespec="seconds", sep=" "),
        description="The start time of the time-entry.",
    )


class Project(BaseModel):
    active: bool
    actual_hours: Optional[int]
    actual_seconds: Optional[int]
    at: str
    color: str
    created_at: str
    id: int
    is_private: bool
    name: str
    start_date: str
    status: str
    workspace_id: int

    def __str__(self):
        return f'"{self.name}", ID:{self.id})'

    def llm_repr(self):
        return f'"{self.name}", ID:{self.id})'

    def get_priority(self):
        for project_obj in project_objs:
            if project_obj["id"] == self.id:
                return project_obj["priority"]
        return 0

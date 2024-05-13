import os
from pprint import pprint
from typing import Optional
import requests
from requests import status_codes
from base64 import b64encode
from dotenv import load_dotenv
from datetime import datetime, timezone
from .togglUtils import handleRequestErrors

from .models import TimeEntry, Project

load_dotenv()
toggl_api_key = os.environ.get("TOGGL_API_KEY")
default_workspace_id = os.environ.get("TOGGL_DEFAULT_WORKSPACE_ID")

assert toggl_api_key, "TOGGL_API_KEY environment variable not set"
assert default_workspace_id, "TOGGL_DEFAULT_WORKSPACE_ID environment variable not set"

base_url = "https://api.track.toggl.com/api/v9"
workspace_url = f"{base_url}/workspaces/{default_workspace_id}"
headers = {
    "content-type": "application/json",
    "Authorization": f"Basic {b64encode(f'{toggl_api_key}:api_token'.encode()).decode('ascii')}",
}


def get_current_time_entry() -> Optional[TimeEntry]:
    response = requests.get(f"{base_url}/me/time_entries/current", headers=headers)
    if response.ok:
        body = response.json()
        if not body:
            # No time entry in progress
            return None
        time_entry = TimeEntry(**body)
        return time_entry
    else:
        handleRequestErrors(response)


def get_time_entries() -> list[TimeEntry]:
    response = requests.get(
        f"{base_url}/me/time_entries",
        headers=headers,
    )
    if response.ok:
        time_entries = []
        for time_entry_obj in response.json():
            time_entry = TimeEntry(**time_entry_obj)
            time_entries.append(time_entry)
        return time_entries
    else:
        handleRequestErrors(response)


def start_time_entry(
    toggl_description: str,
    toggl_project_id: Optional[int] = None,
    # start: datetime = now,
):
    """Start a new time-entry."""
    payload = {
        "billable": False,
        "created_with": "Auto-Toggl",
        "duration": -1,
        "shared_with_user_ids": [],
        "tags": [],
        "workspace_id": int(default_workspace_id),
    }
    payload["description"] = toggl_description
    payload["start"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload["tags"] = ["Auto-Toggl"]
    if toggl_project_id:
        payload["pid"] = toggl_project_id
    else:
        if not toggl_description:
            return
    print(
        f"Starting time entry for {toggl_description} with project id {toggl_project_id}"
    )
    response = requests.post(
        f"{workspace_url}/time_entries", headers=headers, json=payload
    )
    if response.ok:
        new_time_entry = response.json()
        return TimeEntry(**new_time_entry)
    else:
        handleRequestErrors(response)


def stop_time_entry(time_entry_id: int):
    print(f"Stopping time entry {time_entry_id}")
    response = requests.patch(
        f"{workspace_url}/time_entries/{time_entry_id}/stop", headers=headers
    )
    if response.ok:
        return status_codes.codes.ok
    else:
        handleRequestErrors(response)


def stop_current_time_entry():
    """Stop the current time-entry in progress."""
    current = get_current_time_entry()
    if not current:
        return None
    return stop_time_entry(current.id)


def continue_current_time_entry():
    """Continue the current time-entry in progress."""
    return


def replace_current_time_entry(
    toggl_description: str, toggl_project_name: Optional[str] = None
):
    current = get_current_time_entry()
    if not current:
        return None
    stop_time_entry(current.id)
    return start_time_entry(toggl_description, toggl_project_name)


def get_all_projects():
    response = requests.get(f"{workspace_url}/projects", headers=headers)
    if response.ok:
        projects = []
        for project_obj in response.json():
            project = Project(**project_obj)
            projects.append(project)
        return projects
    else:
        handleRequestErrors(response)


def get_tracker_projects() -> list[Project]:
    response = requests.get(f"{workspace_url}/projects", headers=headers)
    if response.ok:
        projects = []
        for project_obj in response.json():
            project = Project(**project_obj)
            excluded_projects = [
                "Meal",
                "Bathroom",
                "Commute",
                "Family",
                "Sleep",
                "Barber",
                "Fitness",
                "Mindfulness",
            ]
            if project.status == "active" and project.name not in excluded_projects:
                projects.append(project)
    else:
        handleRequestErrors(response)
    return projects  # previous method should raise anyway


def get_project(project_id: int) -> Project:
    response = requests.get(f"{workspace_url}/projects/{project_id}", headers=headers)
    if response.ok:
        project_obj = response.json()
        project = Project(**project_obj)
        return project
    else:
        handleRequestErrors(response)


def delete_time_entry(time_entry_id: int):
    response = requests.delete(
        f"{workspace_url}/time_entries/{time_entry_id}", headers=headers
    )
    if response.ok:
        return status_codes.codes.ok
    else:
        handleRequestErrors(response)

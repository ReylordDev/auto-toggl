import os
from typing import Optional
import requests
from requests import status_codes
from base64 import b64encode
from dotenv import load_dotenv
from datetime import datetime, timezone
from .togglUtils import handleRequestErrors

from .models import TimeEntry, Project
from loguru import logger

load_dotenv()
toggl_api_key = os.environ.get("TOGGL_API_KEY")
default_workspace_id = os.environ.get("TOGGL_DEFAULT_WORKSPACE_ID")

assert toggl_api_key, "TOGGL_API_KEY environment variable not set"
assert default_workspace_id, "TOGGL_DEFAULT_WORKSPACE_ID environment variable not set"

DEFAULT_WORKSPACE_ID = default_workspace_id

base_url = "https://api.track.toggl.com/api/v9"
workspace_url = f"{base_url}/workspaces/{DEFAULT_WORKSPACE_ID}"
headers = {
    "Content-type": "application/json",
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


def get_time_entries(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> list[TimeEntry]:
    response = requests.get(
        f"{base_url}/me/time_entries",
        params={"start_date": start_date, "end_date": end_date}
        if start_date and end_date
        else {},
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
        return []


def start_time_entry(
    toggl_description: Optional[str] = None,
    toggl_project_id: Optional[int] = None,
    tags: Optional[list[str]] = ["Auto-Toggl"],
    # start: datetime = now,
):
    """Start a new time-entry."""
    if not toggl_description and not toggl_project_id:
        raise ValueError("Both description and project id cannot be None")
    payload = {
        "billable": False,
        "created_with": "Auto-Toggl",
        "duration": -1,
        "shared_with_user_ids": [],
        "workspace_id": int(DEFAULT_WORKSPACE_ID),
    }
    payload["description"] = toggl_description
    payload["start"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload["tags"] = tags
    if toggl_project_id:
        payload["pid"] = toggl_project_id
    else:
        if not toggl_description:
            return
    logger.info(
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
    logger.info(f"Stopping time entry {time_entry_id}")
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


def get_all_projects():
    response = requests.get(f"{workspace_url}/projects", headers=headers)
    if response.ok:
        projects: list[Project] = []
        for project_obj in response.json():
            project = Project(**project_obj)
            projects.append(project)
        return projects
    else:
        handleRequestErrors(response)
        return []


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


def get_project(project_id: int) -> Optional[Project]:
    if not project_id:
        return None
    response = requests.get(f"{workspace_url}/projects/{project_id}", headers=headers)
    if response.ok:
        project_obj = response.json()
        project = Project(**project_obj)
        return project
    else:
        handleRequestErrors(response)
        return None


def delete_time_entry(time_entry_id: int):
    response = requests.delete(
        f"{workspace_url}/time_entries/{time_entry_id}", headers=headers
    )
    if response.ok:
        return status_codes.codes.ok
    else:
        handleRequestErrors(response)


def update_time_entry(time_entry_id: int, update: dict):
    response = requests.put(
        f"{workspace_url}/time_entries/{time_entry_id}",
        headers=headers,
        json=update,
    )
    if response.ok:
        return status_codes.codes.ok
    else:
        handleRequestErrors(response)


def get_me():
    response = requests.get(f"{base_url}/me", headers=headers)
    if response.ok:
        return response.json()
    else:
        handleRequestErrors(response)

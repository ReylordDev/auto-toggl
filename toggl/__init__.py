from .tracker import get_tracker_projects
from .tracker import (
    get_current_time_entry,
    start_time_entry,
    stop_time_entry,
    get_project,
)


def get_projects():
    projects = get_tracker_projects()
    return projects

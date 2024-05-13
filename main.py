from windows import get_windows
from toggl import (
    get_projects,
    get_current_time_entry,
    start_time_entry,
    stop_time_entry,
    get_project,
)
from pprint import pprint
import time


def main():
    projects = get_projects()
    while True:
        current_time_entry = get_current_time_entry()
        windows = get_windows()
        max_prio = 0
        for i, window in enumerate(windows):
            if i <= 3:
                scaled_prio = window.get_priority() * 1.5
            elif 3 < i <= 5:
                scaled_prio = window.get_priority() * 1
            else:
                scaled_prio = window.get_priority() * 0.5
            # print(f"{i}: {window.get_priority()}, {scaled_prio}, {window.__repr__()}")
            if scaled_prio > max_prio:
                max_prio = scaled_prio
                max_prio_window = window
        new_project_id = max_prio_window.get_toggl_project_id()
        new_description = max_prio_window.get_toggl_description()
        print(f"Max priority window: {max_prio_window}, Priority: {max_prio}")
        project = next(
            (project for project in projects if project.id == new_project_id),
            None,
        )
        print(f"Project: {project.name if project else None}")
        print(f"Description: {new_description}")
        if current_time_entry:
            if current_time_entry.project_id == new_project_id:
                if current_time_entry.description == new_description:
                    pass
                else:
                    stop_time_entry(current_time_entry.id)
                    start_time_entry(
                        toggl_description=new_description,
                        toggl_project_id=new_project_id,
                    )
            else:
                if "Auto-Toggl" not in current_time_entry.tags:
                    current_project = get_project(current_time_entry.project_id)
                    print(f"Current project: {current_project.name}")
                    print(f"Current project priority: {current_project.get_priority()}")
                    print(f"Max priority: {max_prio}")
                    if current_project.get_priority() < max_prio:
                        stop_time_entry(current_time_entry.id)
                        start_time_entry(
                            toggl_description=new_description,
                            toggl_project_id=new_project_id,
                        )
                else:
                    stop_time_entry(current_time_entry.id)
                    start_time_entry(
                        toggl_description=new_description,
                        toggl_project_id=new_project_id,
                    )
        else:
            start_time_entry(
                toggl_description=new_description, toggl_project_id=new_project_id
            )
        print("-" * 80)
        time.sleep(30)


if __name__ == "__main__":
    main()

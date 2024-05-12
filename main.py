from windows import get_windows
from toggl import get_projects
from pprint import pprint
import time


def main():
    projects = get_projects()
    while True:
        windows = get_windows()
        max_prio = 0
        for i, window in enumerate(windows):
            if i <= 3:
                scaled_prio = window.get_priority() * 1.5
            elif 3 < i <= 5:
                scaled_prio = window.get_priority() * 1
            else:
                scaled_prio = window.get_priority() * 0.5
            print(f"{i}: {window.get_priority()}, {scaled_prio}")
            if scaled_prio > max_prio:
                max_prio = scaled_prio
                max_prio_window = window
        print(f"Max priority window: {max_prio_window}")
        print(f"Project ID: {max_prio_window.get_toggl_project_id()}")
        project = next(
            (
                project
                for project in projects
                if project.id == max_prio_window.get_toggl_project_id()
            ),
            None,
        )
        print(f"Project: {project.name if project else None}")
        print(f"Description: {max_prio_window.get_toggl_description()}")
        print("-" * 80)
        time.sleep(5)


if __name__ == "__main__":
    main()

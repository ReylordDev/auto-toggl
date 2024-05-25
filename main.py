from windows import get_windows
from toggl import (
    get_projects,
    get_current_time_entry,
    start_time_entry,
    stop_time_entry,
    get_project,
)
import time
import logging


def main():
    date = time.strftime("%Y-%m-%d")
    logging.basicConfig(
        filename=f"logs/{date}.log",
        level=logging.INFO,
        encoding="utf-8",
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger()
    projects = get_projects()
    print("Auto-Toggl started.")
    while True:
        logger.info("New Iteration")
        current_time_entry = get_current_time_entry()
        logger.info(f"Current time entry: {current_time_entry.__repr__()}")
        windows = get_windows()
        max_prio = 0
        logger.info("Scaled priorities:")
        for i, window in enumerate(windows):
            try:
                if i <= 3:
                    scaled_prio = window.get_priority() * 1.5
                elif 3 < i <= 5:
                    scaled_prio = window.get_priority() * 1
                else:
                    scaled_prio = window.get_priority() * 0.5

                logger.info(
                    f"{i}: Priority: {window.get_priority()} Scaled: {scaled_prio},\n{window.__repr__()}\n"
                )
                if scaled_prio > max_prio:
                    max_prio = scaled_prio
                    max_prio_window = window
            except Exception as e:
                logger.error(f"Error: {e}")
                continue
        logger.info(f"Max priority window: {max_prio_window.__repr__()}")
        logger.info(f"Max priority: {max_prio}")
        new_project_id = max_prio_window.get_toggl_project_id()
        new_description = max_prio_window.get_toggl_description()
        project = next(
            (project for project in projects if project.id == new_project_id),
            None,
        )
        logger.info(f"New Project: {project.name if project else None}")
        logger.info(f"New Description: {new_description}")
        # Careful, you are approach the indentation tree of doom.
        if current_time_entry:
            if current_time_entry.project_id == new_project_id:
                if current_time_entry.description == new_description:
                    logger.info("Continuing current time entry.")
                else:
                    logger.info("Same project, different description. Updating.")
                    stop_time_entry(current_time_entry.id)
                    start_time_entry(
                        toggl_description=new_description,
                        toggl_project_id=new_project_id,
                    )
            else:
                if "Auto-Toggl" not in current_time_entry.tags:
                    logger.info("Current time entry is manual.")
                    if not current_time_entry.project_id:
                        logger.info("Current project not found. Overriding.")
                        stop_time_entry(current_time_entry.id)
                        start_time_entry(
                            toggl_description=new_description,
                            toggl_project_id=new_project_id,
                        )
                    else:
                        if current_time_entry.project_id not in [
                            project.id for project in projects
                        ]:
                            logger.info("Foreign project found, no action taken.")
                            # We don't call continue becuase we want to call the divider and the sleep at the bottom.
                        else:
                            current_project = get_project(current_time_entry.project_id)
                            logger.info(f"Current project: {current_project.name}")
                            logger.info(
                                f"Current project priority: {current_project.get_priority()}"
                            )
                            if current_project.get_priority() < max_prio:
                                logger.info(
                                    "Current project priority is lower than new window priority."
                                )
                                stop_time_entry(current_time_entry.id)
                                start_time_entry(
                                    toggl_description=new_description,
                                    toggl_project_id=new_project_id,
                                )
                            else:
                                logger.info(
                                    "Current project priority is higher than new window priority."
                                )
                else:
                    logger.info("Current time entry is automatic.")
                    stop_time_entry(current_time_entry.id)
                    start_time_entry(
                        toggl_description=new_description,
                        toggl_project_id=new_project_id,
                    )
        else:
            logger.info("No current time entry, starting new time entry")
            start_time_entry(
                toggl_description=new_description, toggl_project_id=new_project_id
            )
        logger.info("-" * 80)
        time.sleep(30)


if __name__ == "__main__":
    main()

from typing import Optional
from toggl.models import Project, TimeEntry
from toggl.togglUtils import BadGateway, GatewayTimeout
from utils import internet
from windows import get_windows_by_z_index
from toggl import (
    get_current_time_entry,
    start_time_entry,
    stop_time_entry,
    get_project,
    get_tracker_projects,
)
import time
from loguru import logger
from win32gui import CreateWindowEx, WNDCLASS, RegisterClass, PumpWaitingMessages
from win32con import WS_EX_LEFT, WM_POWERBROADCAST, PBT_APMSUSPEND
from win32api import GetModuleHandle
import sys
from delete_botched_time_entries import delete_botched_time_entries
from stitch_time_entries import stitch_time_entries


date = time.strftime("%Y-%m-%d")
logger.add(f"logs/{date}.log", level="INFO")


def register_sleep_handler():
    """
    Registers a handler for the system sleep event. When the system goes to sleep, the program will exit.
    """

    # Message Processor for the AutoTogglSleepHandlerWnd
    def wndproc(hwnd, msg, wparam, lparam):
        logger.info(f"Message Received: {msg}")
        if msg == WM_POWERBROADCAST:
            logger.info("Message is a power broadcast.")
            if wparam == PBT_APMSUSPEND:
                logger.info("System is suspending.")
                logger.info("Exiting...")
                sys.exit(0)
            return 0
        return 0

    # Creating a hidden window to receive the messages
    hinst = GetModuleHandle(None)
    wndclass = WNDCLASS()
    wndclass.hInstance = hinst  # type: ignore
    wndclass.lpszClassName = "AutoTogglSleepHandler"  # type: ignore
    message_map = {WM_POWERBROADCAST: wndproc}  # Receive power broadcast messages
    wndclass.lpfnWndProc = message_map  # type: ignore

    myWindowClass = RegisterClass(wndclass)

    CreateWindowEx(
        WS_EX_LEFT,
        myWindowClass,  # type: ignore
        "AutoTogglSleepHandlerWnd",
        0,
        0,
        0,
        0,
        0,
        0,  # Important to set parent to 0
        None,
        hinst,
        None,
    )
    logger.info("Sleep handler registered.")


def handle_same_project(current_time_entry: TimeEntry, new_description: Optional[str]):
    if not new_description:
        logger.info("Same project, no new description. No action taken.")
    else:
        if current_time_entry.description == new_description:
            logger.info("Continuing current time entry.")
        else:
            logger.info("Same project, different description. Updating.")
            stop_time_entry(current_time_entry.id)
            start_time_entry(
                toggl_description=new_description,
                toggl_project_id=current_time_entry.project_id,
            )


def handle_no_current_entry(
    new_project_id: Optional[int], new_description: Optional[str]
):
    logger.info("No current time entry")
    if new_project_id is None and new_description is None:
        logger.info("No new project or description. No action taken.")
    else:
        logger.info("Starting new time entry.")
        start_time_entry(
            toggl_description=new_description,
            toggl_project_id=new_project_id,
        )


def handle_manual_entry(
    current_time_entry: TimeEntry,
    new_project_id: Optional[int],
    new_description: Optional[str],
    projects: list[Project],
    max_prio: float,
):
    if not current_time_entry.project_id:
        logger.info("Current project not found. Overriding.")
        stop_time_entry(current_time_entry.id)
        start_time_entry(
            toggl_description=new_description, toggl_project_id=new_project_id
        )
        return

    if current_time_entry.project_id not in [project.id for project in projects]:
        logger.info("Foreign project found, no action taken.")
        return

    current_project = get_project(current_time_entry.project_id)
    assert current_project, "Current project not found."
    logger.info(f"Current project: {current_project.name}")
    logger.info(f"Current project priority: {current_project.get_priority()}")

    if current_project.get_priority() < max_prio:
        logger.info("Current project priority is lower than new window priority.")
        stop_time_entry(current_time_entry.id)
        start_time_entry(
            toggl_description=new_description, toggl_project_id=new_project_id
        )
    else:
        logger.info("Current project priority is higher than new window priority.")


def handle_automatic_entry(
    current_time_entry: TimeEntry,
    new_project_id: Optional[int],
    new_description: Optional[str],
):
    logger.info("Current time entry is automatic.")
    logger.info("Stopping current time entry.")
    stop_time_entry(current_time_entry.id)
    if new_project_id is None and new_description is None:
        logger.info("No new project or description. No further action taken.")
    else:
        logger.info("Starting new time entry.")
        start_time_entry(
            toggl_description=new_description, toggl_project_id=new_project_id
        )


def handle_time_entry(
    current_time_entry: Optional[TimeEntry],
    new_project_id: Optional[int],
    new_description: Optional[str],
    projects: list[Project],
    max_prio: float,
):
    if not current_time_entry:
        return handle_no_current_entry(new_project_id, new_description)

    if current_time_entry.project_id == new_project_id:
        return handle_same_project(current_time_entry, new_description)

    if "Auto-Toggl" not in current_time_entry.tags:
        return handle_manual_entry(
            current_time_entry, new_project_id, new_description, projects, max_prio
        )

    return handle_automatic_entry(current_time_entry, new_project_id, new_description)


@logger.catch
def main():
    logger.info("-" * 80)
    logger.info("Auto-Toggl started.")
    register_sleep_handler()

    while not internet():
        logger.warning("No internet connection. Retrying in 10 seconds.")
        time.sleep(30)

    delete_botched_time_entries()
    stitch_time_entries()

    projects = get_tracker_projects()
    while True:
        try:
            logger.info("New Iteration")
            current_time_entry = get_current_time_entry()
            logger.info(f"Current time entry: {current_time_entry.__repr__()}")
            windows = get_windows_by_z_index()
            max_prio = 0
            for z_index, window in enumerate(windows):
                try:
                    scaled_prio = window.scale_priority(z_index)

                    logger.info(
                        f"Window: {window.__repr__()}, Scaled priority: {scaled_prio}"
                    )
                    if scaled_prio > max_prio:
                        max_prio = scaled_prio
                        max_prio_window = window
                except Exception as e:
                    logger.error(f"Error: {e}")
                    continue
            if not max_prio_window:
                logger.info("No window found.")
                time.sleep(1)
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

            handle_time_entry(
                current_time_entry, new_project_id, new_description, projects, max_prio
            )

            logger.info("-" * 80)
            for _ in range(30):
                PumpWaitingMessages()
                time.sleep(1)
        except BadGateway:
            logger.error("Bad Gateway. Retrying in 10 seconds.")
            time.sleep(10)
        except GatewayTimeout:
            logger.error("Gateway Timeout. Retrying in 10 seconds.")
            time.sleep(10)


if __name__ == "__main__":
    main()

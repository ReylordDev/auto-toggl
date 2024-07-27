from toggl import get_time_entries, update_time_entry, delete_time_entry
from loguru import logger
import datetime

STICHING_TIME_DELTA = datetime.timedelta(minutes=3)


def stitch_time_entries():
    """
    Stitch time entries together if they meet certain conditions.

    This function stitches consecutive time entries together if the following conditions are met:
    - The time difference between the stop time of the current entry and the start time of the next entry is less than 3 minutes.
    - The project ID and description of the current entry and the next entry are the same.
    """
    time_entries = get_time_entries()

    for i in range(1, len(time_entries)):
        time_entry = time_entries[i]
        next_time_entry = time_entries[i - 1]
        if not next_time_entry:
            continue
        if not time_entry.stop or not next_time_entry.stop:
            continue
        timedelta = datetime.datetime.fromisoformat(
            next_time_entry.start
        ) - datetime.datetime.fromisoformat(time_entry.stop)
        if (
            timedelta < STICHING_TIME_DELTA
            and time_entry.project_id == next_time_entry.project_id
            and time_entry.description == next_time_entry.description
        ):
            logger.debug(f"Stitching {time_entry.id} and {next_time_entry.id}")
            update_time_entry(time_entry.id, {"stop": next_time_entry.stop})
            delete_time_entry(next_time_entry.id)


if __name__ == "__main__":
    stitch_time_entries()

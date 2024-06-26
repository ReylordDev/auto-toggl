from toggl import get_time_entries, update_time_entry, delete_time_entry
import datetime


def stitch_time_entries():
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
            timedelta < datetime.timedelta(minutes=3)
            and time_entry.project_id == next_time_entry.project_id
            and time_entry.description == next_time_entry.description
        ):
            print(f"Stitching {time_entry.id} and {next_time_entry.id}")
            update_time_entry(time_entry.id, next_time_entry.stop)
            delete_time_entry(next_time_entry.id)


if __name__ == "__main__":
    stitch_time_entries()

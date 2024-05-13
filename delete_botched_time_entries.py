from toggl.tracker import get_time_entries, delete_time_entry

time_entries = get_time_entries()

for time_entry in time_entries:
    if 0 <= time_entry.duration < 60:
        delete_time_entry(time_entry.id)

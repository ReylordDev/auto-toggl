from datetime import date
import tkinter as tk
from typing import List, Optional

from toggl import (
    get_all_projects,
    stop_time_entry,
    start_time_entry,
    get_current_time_entry,
)
from toggl.models import Project, TimeEntry
from loguru import logger

from toggl.tracker import get_time_entries

logger.add("logs/mini-player.log", level="INFO")

ENTRY_REFRESH_INTERVAL = 5000  # 5 seconds
DISPLAY_REFRESH_INTERVAL = 1000  # 1 second
FONT_FAMILY = "Segoe UI Semilight"
BG_COLOR = "#191919"


def get_all_entries():
    today = date.today()

    start = today.replace(month=today.month - 1)
    end = today

    entries = get_time_entries(
        start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d")
    )

    start = today.replace(month=today.month - 2)
    end = today.replace(month=today.month - 1)

    entries += get_time_entries(
        start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d")
    )

    start = today.replace(month=today.month - 3)
    end = today.replace(month=today.month - 2)

    entries += get_time_entries(
        start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d")
    )

    logger.info(f"Found {len(entries)} entries")
    return entries


class TimeTrackerMiniPlayer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Time Tracker")
        self.w = 400
        self.h = 60
        self.x = 3000
        self.y = 0
        self.geometry("%dx%d+%d+%d" % (self.w, self.h, self.x, self.y))
        self.attributes("-topmost", True)
        self.overrideredirect(True)  # This hides the title bar

        self.current_entry: Optional[TimeEntry] = None
        self.projects: List[Project] = get_all_projects()
        self.unique_names = []
        self.entries = get_all_entries()
        for entry in self.entries:
            if not entry.description:
                continue
            if entry.project_id:
                project = next(
                    (p for p in self.projects if p.id == entry.project_id), None
                )
            else:
                project = None
            if (entry.description, project) not in self.unique_names:
                self.unique_names.append((entry.description, project))

        self.create_widgets()
        self.update_current_entry()
        self.update_display()

    def create_widgets(self):
        self.description_var = tk.StringVar()
        self.description_var.trace_add("write", self.on_description_update)
        self.project_var = tk.StringVar()
        self.time_var = tk.StringVar()

        self.label_frame = tk.Frame(self, bg=BG_COLOR, bd=0, relief="flat", width=0)
        self.label_frame.pack(side="left", expand=True, fill="both")

        # Description display
        self.description_display = tk.Entry(
            self.label_frame,
            textvariable=self.description_var,
            background=BG_COLOR,
            readonlybackground=BG_COLOR,
            foreground="white",
            insertbackground="white",
            font=(FONT_FAMILY, 16),
            border=0,
            width=0,
            state="readonly",
        )

        # Description entry
        self.description_entry = tk.Entry(
            self.label_frame,
            textvariable=self.description_var,
            background=BG_COLOR,
            readonlybackground=BG_COLOR,
            foreground="white",
            insertbackground="white",
            font=(FONT_FAMILY, 20),
            border=0,
            width=0,
            takefocus=0,
        )
        self.description_entry.pack(side="top", fill="both", expand=True)

        # Project display
        self.project_display = tk.Entry(
            self.label_frame,
            textvariable=self.project_var,
            background=BG_COLOR,
            readonlybackground=BG_COLOR,
            foreground="white",
            insertbackground="white",
            insertofftime=0,
            font=(FONT_FAMILY, 14),
            border=0,
            width=0,
            state="readonly",
        )

        # Start/Stop button
        self.toggle_button = tk.Button(
            self,
            text="Start",
            command=self.toggle_timer,
            bg="#bc5ab1",
            fg="white",
            font=(FONT_FAMILY, 20),
            relief="flat",
            width=4,
            cursor="hand2",
        )
        self.toggle_button.pack(side="right", fill="y", expand=False)

        # Time display
        self.time_label = tk.Label(
            self,
            textvariable=self.time_var,
            bg=BG_COLOR,
            fg="white",
            font=(FONT_FAMILY, 20),
            padx=10,
        )
        self.time_label.pack(side="right", fill="y", expand=False)

        # Hint Dropdown Window
        self.hint_window = tk.Toplevel(
            self.label_frame, bg=BG_COLOR, bd=0, relief="flat"
        )
        self.hint_window.overrideredirect(True)
        self.hint_window.geometry(f"{self.w}x{5}+{self.x}+{self.y + self.h}")
        self.hint_window.withdraw()

        # Hint List
        self.hint_list = tk.Listbox(
            self.hint_window,
            bg=BG_COLOR,
            fg="white",
            font=(FONT_FAMILY, 14),
            border=0,
            selectmode="single",
        )

        # Bind right-click event
        self.bind("<Button-3>", self.show_context_menu)

    def update_current_entry(self):
        previous_entry = self.current_entry
        self.current_entry = get_current_time_entry()
        logger.debug(f"Current entry: {self.current_entry.__repr__()}")
        logger.debug(f"Previous entry: {previous_entry.__repr__()}")
        if self.current_entry:
            # Update window with current entry details
            self.description_entry.pack_forget()
            self.description_display.pack(side="top", fill="x", padx=5)
            self.project_display.pack(side="bottom", fill="x", expand=True, padx=10)
            self.description_var.set(self.current_entry.description or "")
            project = next(
                (p for p in self.projects if p.id == self.current_entry.project_id),
                None,
            )
            if project:
                self.project_display.configure(foreground=project.color)
                self.project_var.set(f"• {project.name}")
            self.toggle_button.config(text="Stop", bg=BG_COLOR)
        else:
            if previous_entry:
                logger.info("Clearing window")
                # Clear window
                self.description_var.set("")
                self.description_display.pack_forget()
                self.description_entry.pack(side="top", fill="both", expand=True)
                self.project_var.set("")
                self.project_display.pack_forget()
                self.toggle_button.config(text="Start", bg="#bc5ab1")
        self.after(
            ENTRY_REFRESH_INTERVAL, self.update_current_entry
        )  # Update every 5 seconds

    def update_display(self):
        if self.current_entry:
            duration = self.current_entry.get_duration()
            self.time_var.set(str(duration)[:-7])
        else:
            self.time_var.set("00:00")
        self.after(
            DISPLAY_REFRESH_INTERVAL, self.update_display
        )  # Update display every second

    def toggle_timer(self):
        if self.current_entry:
            logger.info(f"Stopping time entry {self.current_entry.id}")
            stop_time_entry(self.current_entry.id)
        else:
            text = self.description_var.get()
            text_split = text.split(" • ")
            description = text_split[0]
            project_name = text_split[1] if len(text_split) > 1 else None
            logger.debug(f"Description: {description}")
            logger.debug(f"Project: {project_name}")
            project = next((p for p in self.projects if p.name == project_name), None)
            if description and project:
                logger.info(
                    f"Starting time entry for {description} with project {project.name}"
                )
                start_time_entry(description, project.id)
            elif description:
                logger.info(f"Starting time entry for {description}")
                start_time_entry(description)
        self.update_current_entry()

    def on_description_update(self, var, index, mode):
        if self.current_entry:
            return
        self.hint_list.delete(0, "end")
        self.hint_window.attributes("-topmost", True)
        text = self.description_var.get()
        if text == "" or len(text) == 1:
            self.hint_list.pack_forget()
            self.hint_window.withdraw()
            return
        logger.debug("Deiconifying hint window")
        self.hint_window.deiconify()
        self.hint_list.pack(side="bottom", fill="both", padx=5, pady=5, expand=True)
        self.hint_window.attributes("-topmost", True)
        description_hints = []
        for name, project in self.unique_names:
            if text.lower() in name.lower():
                if project:
                    description_hints.append(f"{name} • {project.name}")
                else:
                    description_hints.append(name)
        # project_hints = [
        #     project.name
        #     for project in self.projects
        #     if text.lower() in project.name.lower()
        # ]
        for hint in description_hints:
            self.hint_list.insert("end", hint)
        # for hint in project_hints:
        #     self.hint_list.insert("end", hint)
        font_size = int(self.hint_list.config()["font"][-1].split(" ")[-1])  # type: ignore
        logger.debug(f"Font size: {font_size}")
        self.hint_window.geometry(
            f"{self.winfo_width()}x{self.hint_list.size() * font_size * 2 + 10}+{self.winfo_x()}+{self.winfo_y() + self.winfo_height()}"
        )
        logger.debug(f"Hint window geometry: {self.hint_window.geometry()}")
        logger.debug(f"Description Hints: {description_hints}")
        # logger.debug(f"Project Hints: {project_hints}")
        # self.hint_list.bind("<<ListboxSelect>>", self.on_hint_select)
        self.bind("<Tab>", self.on_hint_tab)
        self.bind("<Return>", self.on_hint_confirm)
        self.hint_list.bind("<Double-Button-1>", self.on_hint_confirm)
        self.hint_list.configure(cursor="hand2")

    def on_hint_tab(self, event):
        cur = self.hint_list.curselection()
        if not cur:
            self.hint_list.selection_set(0)
        else:
            next_index = (cur[0] + 1) % self.hint_list.size()
            logger.debug(f"Next selection, index: {next_index}")
            self.hint_list.selection_clear(cur)
            self.hint_list.selection_set(next_index)

    def on_hint_confirm(self, event):
        selected = self.hint_list.get(self.hint_list.curselection())
        logger.debug(f"Selected: {selected}")
        self.description_var.set(selected)
        self.description_entry.icursor(tk.END)
        self.hint_window.withdraw()
        # maybe start timer automatically here

    def show_context_menu(self, event):
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_checkbutton(
            label="Disable Always on Top", command=self.toggle_always_on_top
        )
        context_menu.add_checkbutton(
            label="Override redirect", command=self.toggle_override_redirect
        )
        context_menu.add_separator()
        context_menu.add_command(label="Exit", command=self.quit)
        context_menu.tk_popup(event.x_root, event.y_root)

    def toggle_always_on_top(self):
        current_state = self.attributes("-topmost")
        self.attributes("-topmost", not current_state)

    def toggle_override_redirect(self):
        current_state = self.overrideredirect()
        self.overrideredirect(not current_state)


def start_mini_player():
    app = TimeTrackerMiniPlayer()
    app.mainloop()


if __name__ == "__main__":
    start_mini_player()

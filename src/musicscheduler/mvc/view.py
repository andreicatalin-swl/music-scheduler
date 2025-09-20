import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, ClassVar
from PIL import Image, ImageTk
from musicscheduler.utils.logger import get_logger
from logging import INFO, DEBUG

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

class View(tk.Tk):
    _WINDOW_TITLE: ClassVar[str] = 'Music Scheduler'
    _WINDOW_SIZE: ClassVar[str] = '800x600'
    _RESIZABLE_WINDOW_WIDTH: ClassVar[bool] = False
    _RESIZABLE_WINDOW_HEIGHT: ClassVar[bool] = False

    _BG: ClassVar[str] = '#121212'
    _CARD_BG: ClassVar[str] = '#1E1E1E'    
    _FG: ClassVar[str] = '#E0E0E0'

    _PURPLE: ClassVar[str] = '#6C4CFF'

    _INACTIVE_STATUS_COLOR: ClassVar[str] = '#f23030'
    _ACTIVE_STATUS_COLOR: ClassVar[str] = '#55a433'
    _INACTIVE_STATUS_STRING: ClassVar[str] = 'INACTIVE'
    _ACTIVE_STATUS_STRING: ClassVar[str] = 'ACTIVE'

    _SHUFFLE_COLOR: ClassVar[str] = '#808080'
    _SHUFFLE_OFF_STRING: ClassVar[str] = 'SHUFFLE OFF'
    _SHUFFLE_ON_STRING: ClassVar[str] = 'SHUFFLE ON'

    _PLAYER_LABEL_STRING: ClassVar[str] = 'Start/Stop Player'
    _PLAYLIST_DIRECTORY_LABEL_STRING: ClassVar[str] = 'Change Playlist Directory'
    _SCHEDULER_DIRECTORY_LABEL_STRING: ClassVar[str] = 'Change Intervals Directory'
    _SHUFFLE_LABEL_STRING: ClassVar[str] = 'Toggle Shuffle'

    _SCHEDULER_DIRECTORY_SELECTED_STRING: ClassVar[str] = 'Selected Intervals - '
    _PLAYLIST_DIRECTORY_SELECTED_STRING: ClassVar[str] = 'Selected Playlist - '

    _ERROR_WINDOW_TITLE: ClassVar[str] = 'Error'
    _ERROR_WINDOW_SIZE: ClassVar[str] = '300x150'
    

    def __init__(self) -> None:
        super().__init__()

        # Window setup
        self.title(self._WINDOW_TITLE)
        self.geometry(self._WINDOW_SIZE)
        self.resizable(self._RESIZABLE_WINDOW_HEIGHT, self._RESIZABLE_WINDOW_HEIGHT)
        self.configure(bg=self._BG)
        
        # Build UI
        self._build_ui()

        # Update clock
        self._update_clock()

    def run_on_ui_thread(self, function: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        if not callable(function):
            message = f'Cannot add task: {function} is not a callable.'
            LOGGER.warning(message)
        else:
            # Try running function on UI thread
            try:
                self.after(0, lambda: function(*args, **kwargs))
            except Exception as e:
                message = f'Task {function} failed: \'{e}\'.'
                LOGGER.warning(message)

    def _build_ui(self):
        # Top title, status, shuffle
        top_frame = tk.Frame(self, bg=self._BG)
        top_frame.pack(fill="x", padx=24, pady=(18,12))

        self.title_label = tk.Label(top_frame, text='🎵 Music Scheduler', font=('Inter', 20, 'bold'), bg=self._BG, fg=self._FG)
        self.title_label.pack(side='left', anchor='nw')

        self.time_label = tk.Label(top_frame, text='', font=('Inter', 14), bg=self._BG, fg=self._FG)
        self.time_label.pack(side='right', anchor='ne')

        self.status_frame = tk.Frame(self, bg=self._BG)
        self.status_frame.pack(fill='x', padx=24, pady=(0,8))

        self.status_chip = tk.Label(self.status_frame, text='', font=('Inter', 10, 'bold'), bg=self._INACTIVE_STATUS_COLOR, fg='white', padx=8, pady=4, width=12)
        self.status_chip.pack(side='left', padx=(0, 8))

        self.shuffle_status_chip = tk.Label(self.status_frame, text='', font=('Inter', 10, 'bold'), bg=self._SHUFFLE_COLOR, fg='white', padx=8, pady=4, width=12)
        self.shuffle_status_chip.pack(side='left')

        # Main grid (2x2)
        self.grid_frame = tk.Frame(self, bg=self._BG)
        self.grid_frame.pack(fill='both', expand=True, padx=24, pady=12)

        size = (32, 32)
        self.player_icon = self._load_image('play-solid-full.png', size)
        self.directory_icon = self._load_image('folder-solid-full.png', size)
        self.shuffle_icon = self._load_image('shuffle-solid-full.png', size)

        self.player_label = self._make_card_button(self.grid_frame, self._PLAYER_LABEL_STRING, 0, 0, self.player_icon)
        self.playlist_directory_label = self._make_card_button(self.grid_frame, self._PLAYLIST_DIRECTORY_LABEL_STRING, 0, 1, self.directory_icon)
        self.scheduler_directory_label = self._make_card_button(self.grid_frame, self._SCHEDULER_DIRECTORY_LABEL_STRING, 1, 0, self.directory_icon)
        self.shuffle_label = self._make_card_button(self.grid_frame, self._SHUFFLE_LABEL_STRING, 1, 1, self.shuffle_icon)

        for r in range(2):
            self.grid_frame.rowconfigure(r, weight=1, pad=8)
        for c in range(2):
            self.grid_frame.columnconfigure(c, weight=1, pad=8)

        # Bottom mini-strip
        self.bottom_frame = tk.Frame(self, bg=self._CARD_BG)
        self.bottom_frame.pack(fill='x', padx=24, pady=(0,24))
        self.bottom_frame.configure(height=50)
        self.bottom_frame.pack_propagate(False)

        self.playlist_label = tk.Label(self.bottom_frame, text='', font=('Inter', 12), bg=self._CARD_BG, fg=self._FG, anchor='w')
        self.playlist_label.pack(side='left', fill='both', padx=12)

        self.intervals_label_bottom = tk.Label(self.bottom_frame, text='', font=('Inter', 12), bg=self._CARD_BG, fg=self._FG, anchor='e')
        self.intervals_label_bottom.pack(side='right', fill='both', padx=12)

    def _update_clock(self) -> None:
        now = datetime.now().strftime('%H:%M')
        self.time_label.config(text=now)
        self.time_label.after(1000, self._update_clock)

    def _make_card_button(self, parent: tk.Widget, text: str, row: int, col: int, image: ImageTk.PhotoImage) -> tk.Label:
        card = tk.Frame(parent, bg=self._CARD_BG, bd=0, relief='flat')
        card.grid(row=row, column=col, sticky='nsew', padx=8, pady=8)

        lbl = tk.Label(card, text=text, image=image, font=('Inter', 13), bg=self._CARD_BG, fg=self._FG, compound='top', anchor='center')
        lbl.pack(expand=True, fill='both', pady=(16,16))

        return lbl
    
    def show_error(self, message: str) -> None:
        # Check if an error window is already open
        if hasattr(self, '_error_window') and self._error_window.winfo_exists():
            self._error_window.children['!label'].config(text=message)
            self._error_window.lift()
            return

        # Create new error window
        self._error_window = tk.Toplevel(self)
        self._error_window.title(self._ERROR_WINDOW_TITLE)
        self._error_window.geometry(self._ERROR_WINDOW_SIZE)
        self._error_window.configure(bg=self._BG)

        error_label = tk.Label(self._error_window, text=message, font=('Inter', 12), bg=self._BG, fg='red', wraplength=280)
        error_label.pack(expand=True, fill='both', padx=12, pady=12)

        ok_button = ttk.Button(self._error_window, text="OK", command=self._close_error_window)
        ok_button.pack(pady=(0, 12))

        self._error_window.protocol("WM_DELETE_WINDOW", self._close_error_window)

    def _close_error_window(self):
        if hasattr(self, '_error_window') and self._error_window.winfo_exists():
            self._error_window.destroy()
        if hasattr(self, '_error_window'):
            del self._error_window

    @staticmethod
    def _get_resource_path(relative_path: str) -> str:
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, relative_path)
        package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        return os.path.join(package_root, relative_path)

    @staticmethod
    def _load_image(file_name: str, size: tuple[int, int]) -> ImageTk.PhotoImage:
        path = View._get_resource_path(os.path.join('assets', file_name))
        img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    
    def toggle_activation(self, activate: bool) -> None:
        if activate:
            self.status_chip.config(text=self._ACTIVE_STATUS_STRING, bg=self._ACTIVE_STATUS_COLOR)
        else:
            self.status_chip.config(text=self._INACTIVE_STATUS_STRING, bg=self._INACTIVE_STATUS_COLOR)

    def toggle_playlist_shuffle(self, shuffle: bool) -> None:
        if shuffle:
            self.shuffle_status_chip.config(text=self._SHUFFLE_ON_STRING)
        else:
            self.shuffle_status_chip.config(text=self._SHUFFLE_OFF_STRING)

    def set_scheduler_directory(self, directory: str) -> None:
        folder_name = os.path.basename(directory.rstrip("/\\"))
        self.intervals_label_bottom.config(text=self._SCHEDULER_DIRECTORY_SELECTED_STRING + folder_name)

    def set_playlist_directory(self, directory: str) -> None:
        folder_name = os.path.basename(directory.rstrip("/\\"))
        self.playlist_label.config(text=self._PLAYLIST_DIRECTORY_SELECTED_STRING + folder_name)

def main() -> None:
    pass

if __name__ == '__main__':
    main()

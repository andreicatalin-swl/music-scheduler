import tkinter as tk
from tkinter import filedialog
from musicscheduler.mvc.model import Model
from musicscheduler.mvc.view import View
from musicscheduler.utils.cache import Cache
from musicscheduler.utils.logger import get_logger
from logging import INFO, DEBUG

LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL = INFO
LOGGING_FILE_HANDLER_THRESHOLD_LEVEL = DEBUG
LOGGER = get_logger(__name__, LOGGING_CONSOLE_HANDLER_THRESHOLD_LEVEL, LOGGING_FILE_HANDLER_THRESHOLD_LEVEL)

class Controller:
    def __init__(self):
        self._model = Model()
        self._view = View()
        self._cache = Cache()

        # TODO: Load playlist shuffle from cache

        # Set on click listeners
        function = self._view.player_label.bind
        args = ('<Button-1>', self._on_player_label_click)
        self._view.run_on_ui_thread(function, *args)

        function = self._view.scheduler_directory_label.bind
        args = ('<Button-1>', self._on_scheduler_directory_label_click)
        self._view.run_on_ui_thread(function, *args)

        function = self._view.playlist_directory_label.bind
        args = ('<Button-1>', self._on_playlist_directory_label_click)
        self._view.run_on_ui_thread(function, *args)

        function = self._view.shuffle_label.bind
        args = ('<Button-1>', self._on_shuffle_label_click)
        self._view.run_on_ui_thread(function, *args)

        # Define on failure callback
        def on_failure(e):
            message = f'Function execution failed: \'{e}\'.'
            LOGGER.warning(message)

            function = self._view.show_error
            args = (message, )
            # Show error in view
            self._view.run_on_ui_thread(function, *args)
        # Define on success callback
        def on_success(is_active):
            function = self._view.toggle_activation
            args = (is_active, )
            self._view.run_on_ui_thread(function, *args)
        
        self._model.get_is_active(on_success, on_failure)

        # Define on failure callback
        def on_failure(e):
            message = f'Function execution failed: \'{e}\'.'
            LOGGER.warning(message)

            function = self._view.show_error
            args = (message, )
            # Show error in view
            self._view.run_on_ui_thread(function, *args)
        # Define on success callback
        def on_success(directory):
            function = self._view.set_scheduler_directory
            args = (directory, )
            self._view.run_on_ui_thread(function, *args)

            # Load from cache
            if 'scheduler_directory' in self._cache:
                directory = self._cache['scheduler_directory']
                self.set_scheduler_directory(directory)
        
        self._model.get_scheduler_directory(on_success, on_failure)

        # Define on failure callback
        def on_failure(e):
            message = f'Function execution failed: \'{e}\'.'
            LOGGER.warning(message)

            function = self._view.show_error
            args = (message, )
            # Show error in view
            self._view.run_on_ui_thread(function, *args)
        # Define on success callback
        def on_success(directory):
            function = self._view.set_playlist_directory
            args = (directory, )
            self._view.run_on_ui_thread(function, *args)

            # Load from cache
            if 'playlist_directory' in self._cache:
                directory = self._cache['playlist_directory']
                self.set_playlist_directory(directory)
        
        self._model.get_playlist_directory(on_success, on_failure)

        # Define on failure callback
        def on_failure(e):
            message = f'Function execution failed: \'{e}\'.'
            LOGGER.warning(message)

            function = self._view.show_error
            args = (message, )
            # Show error in view
            self._view.run_on_ui_thread(function, *args)
        # Define on success callback
        def on_success(shuffle):
            function = self._view.toggle_playlist_shuffle
            args = (shuffle, )
            self._view.run_on_ui_thread(function, *args)

            # Load from cache
            if 'playlist_shuffle' in self._cache:
                shuffle = self._cache['playlist_shuffle']
                self.set_playlist_shuffle(shuffle)
        
        self._model.get_is_playlist_shuffle(on_success, on_failure)

        # Run view (on current thread)
        self._view.mainloop()

    def _on_player_label_click(self, event: tk.Event) -> None:
        self.toggle_activation()

    def _on_scheduler_directory_label_click(self, event: tk.Event) -> None:
        directory = filedialog.askopenfilename(title='Select afile', filetypes=[("Text files", "*.txt")])
        if directory:
            self.set_scheduler_directory(directory)

    def _on_playlist_directory_label_click(self, event: tk.Event) -> None:
        directory = filedialog.askdirectory(title='Select a folder')
        if directory:
            self.set_playlist_directory(directory)

    def _on_shuffle_label_click(self, event: tk.Event) -> None:
        self.toggle_playlist_shuffle()

    def toggle_activation(self) -> None:
        # Define on failure callback
        def on_failure(e):
            message = f'Function execution failed: \'{e}\'.'
            LOGGER.warning(message)

            function = self._view.show_error
            args = (message, )
            # Show error in view
            self._view.run_on_ui_thread(function, *args)
        # Define on success callback
        def on_success():
            pass     
        
        self._model.toggle_activation(on_success, on_failure)

        # Define on success callback to reflect possible changes on UI, even if previous task fails
        def on_success_show(is_active):
            function = self._view.toggle_activation
            args = (is_active, )
            self._view.run_on_ui_thread(function, *args)
        
        self._model.get_is_active(on_success_show, on_failure)

    def set_scheduler_directory(self, directory: str) -> None:
        # Define on failure callback
        def on_failure(e):
            message = f'Function execution failed: \'{e}\'.'
            LOGGER.warning(message)

            function = self._view.show_error
            args = (message, )
            # Show error in view
            self._view.run_on_ui_thread(function, *args)
        # Define on success callback
        def on_success():
            pass

        self._model.set_scheduler_directory(directory, on_success, on_failure)

        # Define on success callback to reflect possible changes on UI, even if previous task fails
        def on_success_show(directory):
            function = self._view.set_scheduler_directory
            args = (directory, )
            self._view.run_on_ui_thread(function, *args)

        self._model.get_scheduler_directory(on_success_show, on_failure)

    def set_playlist_directory(self, directory: str) -> None:
        # Define on failure callback
        def on_failure(e):
            message = f'Function execution failed: \'{e}\'.'
            LOGGER.warning(message)

            function = self._view.show_error
            args = (message, )
            # Show error in view
            self._view.run_on_ui_thread(function, *args)
        # Define on success callback
        def on_success():
            pass
        
        self._model.set_playlist_directory(directory, on_success, on_failure)

        # Define on success callback to reflect possible changes on UI, even if previous task fails
        def on_success_show(directory):
            function = self._view.set_playlist_directory
            args = (directory, )
            self._view.run_on_ui_thread(function, *args)

        self._model.get_playlist_directory(on_success_show, on_failure)

    def toggle_playlist_shuffle(self) -> None:
        # Define on failure callback
        def on_failure(e):
            message = f'Function execution failed: \'{e}\'.'
            LOGGER.warning(message)

            function = self._view.show_error
            args = (message, )
            # Show error in view
            self._view.run_on_ui_thread(function, *args)
        # Define on success callback
        def on_success():
            pass
    
        self._model.toggle_playlist_shuffle(on_success, on_failure)

        # Define on success callback to reflect possible changes on UI, even if previous task fails
        def on_success_show(shuffle):
            function = self._view.toggle_playlist_shuffle
            args = (shuffle, )
            self._view.run_on_ui_thread(function, *args)

        self._model.get_is_playlist_shuffle(on_success_show, on_failure)

    def set_playlist_shuffle(self, shuffle: bool) -> None:
        # Define on failure callback
        def on_failure(e):
            message = f'Function execution failed: \'{e}\'.'
            LOGGER.warning(message)

            function = self._view.show_error
            args = (message, )
            # Show error in view
            self._view.run_on_ui_thread(function, *args)
        # Define on success callback
        def on_success():
            pass
    
        self._model.set_playlist_shuffle(shuffle, on_success, on_failure)

        # Define on success callback to reflect possible changes on UI, even if previous task fails
        def on_success_show(shuffle):
            function = self._view.toggle_playlist_shuffle
            args = (shuffle, )
            self._view.run_on_ui_thread(function, *args)

        self._model.get_is_playlist_shuffle(on_success_show, on_failure)

def main() -> None:
    pass

if __name__ == '__main__':
    main()

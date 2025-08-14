import sys
from guizero import App, TextBox
from tkinter.font import Font
from threading import Event
from importlib.resources import files

from .settings import Settings

MACOS = True if sys.platform == "darwin" else False
MIN_TEXT = 6
MAX_TEXT = 150
RESIZE_DELAY = 300

class Note:
    def __init__(self, text=None):
        
        self._resize_triggered = Event()

        self._app = App(
            "Always Note",
            height=100, width=500
        )

        self._app.icon = str(files('always_note').joinpath('note.gif'))

        self._settings = Settings(self)
        if text is not None: self._settings.text = text
        self._app.width = self._settings.width
        self._app.height = self._settings.height

        self._text = TextBox(
            self._app, 
            multiline=True, 
            width="fill", height="fill",    
            text=self._settings.text, 
            command=self._text_updated
        )
        
        # Setup events
        self._text.when_right_button_released = self._open_settings
        if MACOS:
            self._text.events.set_event("<macos-2-finger-press>", "<ButtonPress-2>", self._open_settings)
        self._app.when_resized = self._app_resized
        self._app.when_closed = self.close

    def _app_resized(self):
        self._settings.width = self._app.width
        self._settings.height = self._app.height
        self._trigger_resize()

    def _text_updated(self):
        # update the text setting, strip \n
        self._settings.text = self._text.value[:-1]
        self._trigger_resize()

    def _trigger_resize(self):
        # trigger a resize
        if self._resize_triggered.is_set():
            self._app.cancel(self._resize_text)
        self._app.after(RESIZE_DELAY, self._resize_text)
        self._resize_triggered.set()

    def _resize_text(self):
        self._resize_triggered.clear()

        font = Font(
            family=self._text.font, 
            size=self._text.text_size, 
            weight="normal"
        )

        # find the longest line
        lines = self._text.value.split("\n")
        longest_line = max(lines, key=len)

        # find the font size that will fit
        for i in range(MIN_TEXT, MAX_TEXT, 2):
            font.configure(size=i)
            width = font.measure(longest_line)
            height = font.metrics("linespace") * (len(lines) - 1)
            if width >= self._app.width or height >= self._app.height:
                break
        
        self._text.text_size = i - 5

    def _set_on_top(self, on_top):
        self._app.tk.attributes(
            '-topmost', 
            on_top
        )

    def _open_settings(self):
        self._set_on_top(False)
        self._settings.open()

    def _update_font_settings(self):
        self._text.bg = self._settings.bg_color
        self._text.text_color = self._settings.text_color
        self._text.font = self._settings.font
        self._resize_text()

    def _update_settings(self):
        self._update_font_settings()
        self._set_on_top(self._settings.on_top)

    def _show_title_bar(self):
        # disable the events
        self._app.events.set_event("<when_loses_focus>", "<FocusOut>", None)
        self._app.events.set_event("<when_get_focus>", "<FocusIn>", None)
        # show the title bar
        self._app.tk.overrideredirect(False)
        # re-enable the events after a delay
        self._app.tk.after(
            100, 
            lambda: self._app.events.set_event("<when_get_focus>", "<FocusIn>", None)
        )
        self._app.tk.after(
            100, 
            lambda: self._app.events.set_event("<when_loses_focus>", "<FocusOut>", self._hide_title_bar)
        )

    def _hide_title_bar(self):
        # disable the events
        self._app.events.set_event("<when_loses_focus>", "<FocusOut>", None)
        self._app.events.set_event("<when_get_focus>", "<FocusIn>", None)
        # hide the title bar
        self._app.tk.overrideredirect(True)
        # re-enable the events after a delay
        self._app.tk.after(
            100, 
            lambda: self._app.events.set_event("<when_get_focus>", "<FocusIn>", self._show_title_bar)
        )
        self._app.tk.after(
            100, 
            lambda: self._app.events.set_event("<when_loses_focus>", "<FocusOut>", None)
        )

    def display(self):
        if not MACOS:
            self._hide_title_bar()
        self._update_settings()
        self._resize_text()
        self._app.display()

    def close(self):
        self._settings.close()
        self._app.destroy()

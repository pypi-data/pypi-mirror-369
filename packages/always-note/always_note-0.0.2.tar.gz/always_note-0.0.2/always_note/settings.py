from os import path
import json
from guizero import Window, Box, Text, CheckBox, Combo
from tkinter import font
from importlib.resources import files

SETTINGS_PATH = path.join(".",".always-note-settings")
DEFAULT_SETTINGS = {
    "on_top": True,
    "bg_color": "white",
    "text_color": "black",
    "font": "Courier New",
    "text": "Write here!",
    "width": 500,
    "height": 100
}

class Settings:
    def __init__(self, note):
        self._load()

        self._note = note
        self._window = Window (
            self._note._app, 
            "Settings",
            layout="grid",
            visible=False,
            width=300, height=200
        )
        self._window.hide()
        self._window.icon = str(files('always_note').joinpath('settings.gif'))
        self._window.when_closed = self.close

        Text(self._window, "Always on top?", grid=[0, 0], align="right")
        def update_on_top():
            self._data["on_top"] = self._on_top.value
        self._on_top = CheckBox(
            self._window,
            grid=[1, 0],
            align="left",
            command=update_on_top
        )

        Text(self._window, "Font", grid=[0, 1], align="right")
        def update_font():
            self._data["font"] = self._font.value
            self._note._update_font_settings()
        self._font = Combo(
            self._window,
            grid=[1, 1],
            align="left",
            options=font.families(),
            command=update_font
            )

        Text(self._window, "Background", grid=[0, 2], align="right")
        self._bg_color = Box(
            self._window,
            grid=[1, 2],
            align="left",
            height=25,
            width=50,
            border=True
            )
        def update_bg_color():
            color = self._window.select_color()
            self._bg_color.bg = color
            self._data["bg_color"] = color
            self._note._update_font_settings()
        self._bg_color.when_clicked = update_bg_color

        Text(self._window, "Text color", grid=[0, 3], align="right")
        self._text_color = Box(
            self._window,
            grid=[1, 3],
            align="left",
            height=25,
            width=50,
            border=True
            )
        def update_text_color():
            color = self._window.select_color()
            self._text_color.bg = color
            self._data["text_color"] = color
            self._note._update_font_settings()
        self._text_color.when_clicked = update_text_color

    def _load(self):
        try:
            with open(SETTINGS_PATH, "r") as f:
                self._data = json.load(f)
        except FileNotFoundError:
            self._data = DEFAULT_SETTINGS

    def save(self):
        with open(SETTINGS_PATH, "w") as f:
            json.dump(self._data, f)
        
    @property
    def on_top(self):
        return self._data["on_top"]

    @property
    def bg_color(self):
        return self._data["bg_color"]

    @property
    def text_color(self):
        return self._data["text_color"]
    
    @property
    def font(self):
        return self._data["font"]
    
    @property
    def text(self):
        return self._data["text"]
    
    @text.setter
    def text(self, value):
        self._data["text"] = value

    @property
    def width(self):
        return self._data["width"]
    
    @width.setter
    def width(self, value):
        self._data["width"] = value

    @property
    def height(self):
        return self._data["height"]
    
    @height.setter
    def height(self, value):
        self._data["height"] = value

    def open(self):
        # update gui values
        self._font.value = self._data["font"]
        self._on_top.value = self._data["on_top"]
        self._bg_color.bg = self._data["bg_color"]
        self._text_color.bg = self._data["text_color"]

        self._window.show(wait=True)
        self._window.tk.attributes(
            '-topmost',
            True
        )
        
    def close(self):
        self._note._update_settings()
        self.save()
        self._window.hide()
        # self._note._app.show()

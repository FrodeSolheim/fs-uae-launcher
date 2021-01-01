from fsui import (
    Color,
    Dialog,
    Panel,
    TextArea,
    VerticalLayout,
    Font,
    get_window,
)
from launcher.context import get_launcher_theme
from .titlebar import TitleBar

"""
TODO: Make text area scrollbar look nice when text is overflowing.
TODO: Support for opening centered on coordinates given to constructor.
"""


class ExceptionDialog(Dialog):
    def __init__(self, parent, *, exception, backtrace, recoverable=False):
        self.theme = get_launcher_theme(self)
        window_parent = None
        if recoverable:
            title = "Recoverable Alert"
        else:
            title = "Software Failure"
        minimizable = False
        maximizable = False
        super().__init__(window_parent, title, border=False)
        self.layout = VerticalLayout()

        if recoverable:
            text_color = Color(0xFFAA22)
            # background_color = Color(0x111111)
            title_foreground_color = Color(0x000000)
            title_background_color = Color(0xFFAA22)
        else:
            text_color = Color(0xFF2222)
            title_foreground_color = Color(0x000000)
            title_background_color = Color(0xFF2222)
        background_color = Color(0x181818)

        self.set_background_color(background_color)

        if not self.theme.titlebar_system():
            self.__titlebar = TitleBar(
                self,
                title=title,
                minimizable=minimizable,
                maximizable=maximizable,
                # foreground_color=Color(0xFFFFFF),
                # background_color=Color(0x282828),
                foreground_color=title_foreground_color,
                background_color=title_background_color,
                foreground_inactive_color=Color(0xCCCCCC),
                background_inactive_color=Color(0x333333),
            )
            self.layout.add(self.__titlebar, fill=True)

        self.errorpanel = ExceptionPanel(
            self, title, exception, background_color, text_color
        )
        self.layout.add(self.errorpanel, fill=True, expand=True)

        # FIXME: For frozen version, we might want to clean up the file
        # references, so absolute paths from the development host is removed.
        text = f"{exception}\n\n{backtrace}"

        self.textarea = TextArea(
            self,
            text=text,
            read_only=True,
            border=False,
            text_color=Color(0xFFFFFF),
            background_color=background_color,
            padding=20,
        )
        self.textarea.set_min_size((640, 320))
        # FIXME: Include a suitable fixed-with font with the launcher and use
        # that? This font might not be available.
        self.textarea.set_font(Font("Courier New", 14))
        self.textarea.scroll_to_start()
        self.layout.add(self.textarea, fill=True, expand=True)

        # Hmm, FIXME: the timer started by the exception panel continues after
        # the dialog has been closed. Hmm, even continues if the parent dialog
        # is destroyed??

        # self.setAttribute(Qt.WA_DeleteOnClose)

    def __del__(self):
        # print("-" * 79)
        print("ExceptionDialog.__del__")
        # print("-" * 79)


class ExceptionPanel(Panel):
    def __init__(
        self, parent, title, exception, background_color, foreground_color
    ):
        super().__init__(parent)
        self.title = title
        self.bgcolor = background_color
        self.fgcolor = foreground_color

        self.font = Font("Saira Semi Condensed", 20, weight="Medium")
        self.exceptionname = type(exception).__name__
        self.blinkstate = True

        self.border = 6
        self.padding = 20
        self.innerheight = 80
        self.set_min_height(self.padding + self.border * 2 + self.innerheight)
        # FIXME: Create fsui API
        # self.startTimer(1000)
        # print("-----------\Exception panel\n")
        self.start_timer(1000)

    def on_left_down(self):
        get_window(self).close()

    def on_paint(self):
        dc = self.create_dc()
        ww, _ = self.size()
        rect_h = self.border * 2 + self.innerheight
        x = self.padding
        y = self.padding
        border = self.border
        if self.blinkstate:
            dc.draw_rectangle(x, y, ww - 2 * x, rect_h, self.fgcolor)
            dc.draw_rectangle(
                x + border,
                y + border,
                ww - 2 * x - 2 * border,
                rect_h - 2 * border,
                self.bgcolor,
            )
        dc.set_font(self.font)
        dc.set_text_color(self.fgcolor)
        text = f"{self.title}.  Press left mouse button to continue."
        tw, _ = dc.measure_text(text)
        dc.draw_text(text, (ww - tw) / 2, self.padding + self.border + 10)
        text = f"Guru Meditation #{self.exceptionname}"
        tw, _ = dc.measure_text(text)
        dc.draw_text(text, (ww - tw) / 2, self.padding + self.border + 36)

    def on_timer(self):
        self.blinkstate = not self.blinkstate
        self.refresh()

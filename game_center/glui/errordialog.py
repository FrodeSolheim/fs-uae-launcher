import sys
import time
from game_center.resources import resources
from game_center.glui.opengl import *
from game_center.glui.dialog import Dialog
from game_center.glui.render import Render
from game_center.glui.state import State


MAX_LINE = 30


def show_exception():
    import traceback
    backtrace = traceback.format_exc()
    State.dialog = ErrorDialog(sys.exc_info()[1], backtrace)
    show_error_state = {"stop": False}
    while not show_error_state["stop"]:
        def input_func(button):
            if button == "BACK":
                show_error_state["stop"] = True
        # FIXME
        from game_center.glui.window import main_loop_iteration
        if main_loop_iteration(input_func=input_func):
            break
    State.dialog.destroy()
    State.dialog = None


class ErrorDialog(Dialog):

    def __init__(self, message, backtrace=None):
        Dialog.__init__(self)
        self.width = 16 / 9 * 2
        self.height = 2.0
        self.message = message
        self.backtrace = backtrace
        self.splitted = self.backtrace.split("\n")
        if not self.splitted[-1]:
            self.splitted = self.splitted[:-1]

        self.background_color = (0.0, 0.0, 0.0, 1.0)
        liberation_mono_bold = resources.resource_filename(
            "LiberationMono-Regular.ttf")
        self.detail_font = pygame.font.Font(
            liberation_mono_bold, int(0.021 * Render.display_height))
        self.guru_font = pygame.font.Font(
            liberation_mono_bold, int(0.03 * Render.display_height))
        self.start_time = time.time()

    def render_content(self):
        Render.dirty = True

        # #x1 = -16 / 9 + 0.1
        # x1 = 0.1
        # #x2 = 16 / 9 - 0.1
        # x2 = self.width - 0.1
        # #y1 = 0.7
        # #y2 = 0.9
        # y1 = 1.6
        # y2 = 1.9
        x1 = 0
        x2 = self.width
        y1 = 1.7
        y2 = 2.0
        w = 0.03

        # t = (pygame.time.get_ticks() - self.start_time) // 1000
        alert_color = (1.0, 0.8, 0.0)
        t = int((time.time() - self.start_time * 1.6))
        if t % 2 == 0:
            glBegin(GL_QUADS)
            glColor3f(*alert_color)
            glVertex2f(x1, y1)
            glVertex2f(x2, y1)
            glVertex2f(x2, y2)
            glVertex2f(x1, y2)
            glColor3f(0.0, 0.0, 0.0)
            glVertex2f(x1 + w, y1 + w)
            glVertex2f(x2 - w, y1 + w)
            glVertex2f(x2 - w, y2 - w)
            glVertex2f(x1 + w, y2 - w)
            glEnd()

        text = "Software Failure.  Press BACKSPACE or back button to continue."
        Render.text(text, self.guru_font, 0.2, 1.85, color=alert_color)
        text = self.splitted[-1]
        text = "Guru Meditation #{0}".format(text)
        Render.text(text, self.guru_font, 0.2, 1.77, color=alert_color)

        x = 0.2
        y = 0.15

        tw, th = Render.measure_text("M", self.detail_font)
        y += th
        lines = []
        max_line_size = 129
        for line in self.splitted:
            line = line.rstrip()
            while len(line) > max_line_size:
                lines.append(line[:max_line_size])
                line = line[max_line_size:]
            lines.append(line)

        for i, line in enumerate(reversed(lines)):
            if i == MAX_LINE:
                break
            s = (MAX_LINE - i) / MAX_LINE
            tw, th = Render.text(
                line, self.detail_font, x, y, color=(s, s, s, 1.0))
            y += th

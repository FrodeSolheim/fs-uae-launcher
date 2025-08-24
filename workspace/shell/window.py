import threading
import traceback

import time

import workspace.sys
from workspace import ui


COLOR = (0x44, 0x44, 0x44)


class ShellWindow(ui.Window):
    def __init__(self, parent, argv=None):
        super().__init__(
            parent, "Shell", menu=True, maximizable=False, color=COLOR
        )
        if argv is None or len(argv) == 0:
            argv = ["CLI"]

        col = ui.Column()
        self.add(col)
        # col.add(ui.TitleSeparator(self))
        self.canvas = ShellWidget(self, argv=argv)
        self.set_background_color(ui.Color(*COLOR))
        col.add(self.canvas, left=12, top=6, right=12, bottom=6)

        self.closed.connect(self.__on_closed)

    def __on_closed(self):
        self.canvas.terminate_process()


class ShellWidget(ui.Canvas):
    output = ui.Signal()
    exited = ui.Signal()

    def __init__(self, parent, *, argv, columns=80, rows=24):
        super().__init__(parent)
        self.font = ui.Font("Roboto Mono", 14)
        self.set_background_color(ui.Color(*COLOR))
        self.text_color = ui.Color(0xFF, 0xFF, 0xFF)

        self.input_thread = None
        self.output_thread = None
        self.output.connect(self.__on_output)

        self._completed = False
        self.exited.connect(self.__on_exited)

        self.line_buffer = []
        self.lines = []
        # for _ in range(25):
        self._new_line()
        self.cx = 0
        self.cy = 0

        # self.execute(["version"])
        # self.execute(["python", "-i"])
        self.process = None
        self.execute(argv)

        # FIXME: Using Qt directly
        from fsui.qt import Qt, QPainter, QPixmap

        self._widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        painter = QPainter()
        pixmap = QPixmap(100, 100)
        painter.begin(pixmap)
        painter.setFont(self.font.qfont())
        size = painter.boundingRect(
            0, 0, 10000, 1000, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, " " * columns
        )
        painter.end()
        print(size)
        self.line_width = size.width()
        self.line_height = size.height()

        self.set_min_size((self.line_width, self.line_height * rows))

    def execute(self, args):
        self.process = workspace.sys.workspace_exec(args)
        print(self.process)
        self.input_thread = InputThread(self, self.process)
        self.input_thread.start()
        self.output_thread = OutputThread(self, self.process)
        self.output_thread.start()

    def terminate_process(self):
        self.input_thread.stop()
        self.output_thread.stop()
        self.process.kill()

    def _new_line(self):
        self.lines = self.lines[-24:]
        self.lines.append([" "] * 80)
        self.cx = 0
        self.cy = len(self.lines) - 1

    def __on_output(self):
        print("on_output")
        # This runs in the main thread
        data = self.output_thread.data()
        print(data)
        for byte in data:
            self._print_byte(byte)

    def __on_exited(self):
        self._complete()

    def _complete(self):
        if not self._completed:
            self._print_text("\n[Process completed]")
            self.input_thread.stop()
            self.output_thread.stop()
            self._completed = True

    def _print_text(self, text):
        for char in text:
            self._print_char(char)

    def _print_byte(self, byte):
        # FIXME: UTF-8...
        char = byte.decode("ISO-8859-1")
        self._print_char(char)

    def _print_char(self, char):
        if char == "\n":
            self._new_line()
            return
        if char == "\r":
            self.cx = 0
            return
        # print(self.cy, self.cx)
        self.lines[self.cy][self.cx] = char
        # line = self.lines[-1]
        self.cx += 1
        if self.cx == 80:
            # self.cy += 1
            # self.cx = 0

            # if self.cy == 25:
            #    self.lines = self.lines[:24]

            self._new_line()

        # if len(line) < 80:
        #     self.lines[-1] = line + char
        # else:
        #      line = char
        #      self.lines.append(line)
        #      if len(self.lines) > 25:
        #         self.lines = self.lines[-25:]
        self.refresh()

    def _erase_char(self):
        # FIXME: TODO: multi-line erase..
        if self.cx > 0:
            self.cx -= 1
            self.lines[self.cy][self.cx] = " "
        self.refresh()

    def on_paint(self):
        painter = ui.Painter(self)
        painter.set_font(self.font)
        if hasattr(self, "text_color"):
            painter.set_text_color(self.text_color)
        # lines = self.buffer()
        x, y = 0, 0
        for line_data in self.lines:
            line = "".join(line_data)
            # tw, th = painter.measure_text(line)
            painter.draw_text(line, x, y)
            # y += th
            y += self.line_height

    def on_key_press(self, event):
        print("on_key_press", event)
        if self._completed:
            print("process is completed, ignoring")
            return
        # FIXME: using a QKeyEvent directly
        from fsui.qt import QKeyEvent

        assert isinstance(event, QKeyEvent)
        char = event.text()
        print(repr(char))
        if not char:
            print("char was", repr(char))
            return
        if char == "\x08":
            if len(self.line_buffer) > 0:
                self.line_buffer = self.line_buffer[:-1]
                self._erase_char()
            return
        if char == "\x04":
            self.input_thread.add_byte(b"\x04")
            # FIXME: Close stdin if/when you type Ctrl+D?
            # self._p.stdin.close()
            return
        if char == "\r":
            # Qt peculiarity...
            char = "\n"
            self.line_buffer.append(char)
            self._new_line()
            bytes = []
            for char in self.line_buffer:
                bytes.append(char.encode("ISO-8859-1"))
            self.input_thread.add_bytes(bytes)
            self.line_buffer.clear()
            return
        else:
            self.line_buffer.append(char)
            self._print_char(char)
        # byte = char.encode("ISO-8859-1")
        # self.input_thread.add_byte(byte)


class OutputThread(threading.Thread):
    def __init__(self, widget, p):
        super().__init__()
        self._widget = widget
        self._p = p
        self._data = []
        self._available = False
        self._lock = threading.Lock()
        self.stop_flag = False

    def data(self):
        with self._lock:
            data = self._data
            self._data = []
            self._available = False
            return data

    def run(self):
        print("OutputThread.run")
        try:
            self._run()
        except Exception:
            traceback.print_exc()
        self._widget = None

    def stop(self):
        self.stop_flag = True
        self._widget = None

    def _run(self):
        while True:
            byte = self._p.stdout.read(1)
            if not byte:
                print("no more data, ending output thread")
                if self._widget is not None:
                    self._widget.exited.emit()
                return
            with self._lock:
                self._data.append(byte)
                if not self._available:
                    self._available = True
                    print("emit time")
                    if self._widget is not None:
                        self._widget.output.emit()


class InputThread(threading.Thread):
    """Handles data sent to child process"""

    def __init__(self, widget, p):
        super().__init__()
        self._widget = widget
        self._p = p
        self._data = []
        # self._available = False
        self._lock = threading.Lock()
        self.stop_flag = False

    def add_byte(self, byte):
        with self._lock:
            self._data.append(byte)

    def add_bytes(self, bytes):
        with self._lock:
            self._data.extend(bytes)

    def run(self):
        print("InputThread.run")
        try:
            self._run()
        except Exception:
            traceback.print_exc()
        self._widget = None

    def stop(self):
        self.stop_flag = True
        self._widget = None

    def _run(self):
        while not self.stop_flag:
            # FIXME: conditions instead
            time.sleep(0.01)
            with self._lock:
                if len(self._data) == 0:
                    continue
                data = b"".join(self._data)
                self._data = []
            print("writing", data)
            self._p.stdin.write(data)
            self._p.stdin.flush()

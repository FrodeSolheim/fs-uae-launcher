from fsui import Button, Color, get_mouse_position, HorizontalLayout, Panel


class TitleBar(Panel):
    def __init__(self, parent):
        super().__init__(parent, paintable=True)
        self.set_min_height(40)
        self.set_background_color(Color(0xFF, 0xFF, 0xFF))

        self.menu_button = Button(self, "=")
        self.minimize_button = Button(self, "_")
        self.minimize_button.activated.connect(self.on_minimize_button)
        self.maximize_button = Button(self, "^")
        self.maximize_button.activated.connect(self.on_maximize_button)
        self.close_button = Button(self, "X")
        self.close_button.activated.connect(self.on_close_button)

        self.layout = HorizontalLayout()
        self.layout.add(self.menu_button, fill=True)
        self.layout.add_spacer(0, expand=True)
        self.layout.add(self.minimize_button, fill=True)
        self.layout.add(self.maximize_button, fill=True)
        self.layout.add(self.close_button, fill=True)

        self.window_pos = (-1, -1)
        self.mouse_pos = (-1, -1)

    def on_menu_button(self):
        pass

    def on_minimize_button(self):
        self.parent().minimize()

    def on_maximize_button(self):
        self.parent().maximize(not self.parent().is_maximized())

    def on_close_button(self):
        self.parent().close()

    def on_left_dclick(self):
        self.on_maximize_button()

    def on_left_down(self):
        self.window_pos = self.parent().get_position()
        self.mouse_pos = get_mouse_position()

    def on_mouse_motion(self):
        mouse_pos = get_mouse_position()
        window_pos = (
            self.window_pos[0] + mouse_pos[0] - self.mouse_pos[0],
            self.window_pos[1] + mouse_pos[1] - self.mouse_pos[1],
        )
        self.parent().set_position(window_pos)

    # def on_left_up(self):
    #     pass

    def on_paint(self):
        dc = self.create_dc()
        if self.close_button is not None:
            x_offset = self.close_button.width() + 20
        else:
            x_offset = 20
        # print(self.parent())
        # text = self.parent().title()
        text = "FIXME"
        _, th = dc.measure_text(text)
        dc.draw_text(text, x_offset, (self.height() - th) // 2)

import fsui
from fsbc.application import app
from fsgamesys.ogd.client import OGDClient

# from workspace.shell import SimpleApplication
from launcher.res import gettext
from launcher.ui.widgets import CloseButton
from workspace.ui.theme import WorkspaceTheme


class LoginWindow(fsui.Window):
    @classmethod
    def open(cls, parent=None):
        return fsui.open_window_instance(cls, parent)

    def __init__(self, parent=None):
        print("LoginWindow, parent =", parent)
        super().__init__(parent, gettext("Log In to Your OpenRetro Account"))
        self.set_icon(fsui.Icon("password", "pkg:workspace"))
        self.theme = WorkspaceTheme.instance()
        self.layout = fsui.VerticalLayout()

        self.layout.set_padding(20, 20, 20, 20)

        heading_layout = fsui.HorizontalLayout()
        self.layout.add(heading_layout)
        heading_layout.add(
            fsui.ImageView(self, fsui.Image("workspace:res/48/password.png"))
        )
        heading_layout.add_spacer(20)
        heading_layout_2 = fsui.VerticalLayout()
        heading_layout.add(
            heading_layout_2, expand=True, fill=False, valign=0.5
        )
        heading_layout_2.add(
            fsui.HeadingLabel(
                self, gettext("Log In to Your OpenRetro Account")
            )
        )
        heading_layout_2.add_spacer(2)
        heading_layout_2.add(
            fsui.Label(
                self,
                gettext(
                    "Logging in will enable the online game database "
                    "and more"
                ),
            )
        )

        self.username_field = fsui.TextField(
            self, app.settings["database_email"].strip()
        )
        self.password_field = fsui.PasswordField(self)
        if self.username_field.get_text():
            self.password_field.focus()

        self.layout.add_spacer(20)
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        label = fsui.Label(self, gettext("E-mail:"))
        label.set_min_width(100)
        hori_layout.add(label)
        hori_layout.add_spacer(20)
        # self.username_field.select_all()
        self.username_field.changed.connect(self.on_text_field_changed)
        self.username_field.activated.connect(self.on_username_activated)
        hori_layout.add(self.username_field, expand=True)

        self.layout.add_spacer(10)
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        label = fsui.Label(self, gettext("Password:"))
        label.set_min_width(100)
        hori_layout.add(label)
        hori_layout.add_spacer(20)
        self.password_field.changed.connect(self.on_text_field_changed)
        self.password_field.activated.connect(self.on_password_activated)
        hori_layout.add(self.password_field, expand=True)

        self.layout.add_spacer(20)
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        label = fsui.Label(self, gettext("Don't have an account already?"))
        hori_layout.add(label)
        hori_layout.add_spacer(20)
        label = fsui.URLLabel(
            self,
            gettext("Create an account now"),
            "https://openretro.org/user/register?referrer=fs-uae-launcher",
        )
        hori_layout.add(label, expand=True)

        self.layout.add_spacer(6)
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        label = fsui.Label(self, gettext("Forgot your password?"))
        hori_layout.add(label)
        hori_layout.add_spacer(20)
        self.reset_label = fsui.URLLabel(
            self,
            gettext("Reset password via e-mail"),
            "https://openretro.org/user/reset?referrer=fs-uae-launcher",
        )
        hori_layout.add(self.reset_label, expand=True)

        self.layout.add_spacer(20)
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        self.created_label = fsui.Label(self, "")
        hori_layout.add(self.created_label, expand=True)
        hori_layout.add_spacer(20)

        self.login_button = fsui.Button(self, gettext("Log In"))
        self.login_button.set_enabled(False)
        self.login_button.activated.connect(self.on_login_activated)
        hori_layout.add(self.login_button)

        if self.window().theme.has_close_buttons:
            self.close_button = CloseButton(self)
            hori_layout.add(self.close_button, fill=True, margin_left=10)

        self.set_size(self.layout.get_min_size())
        self.center_on_parent()

        if len(self.username_field.text()) == 0:
            self.username_field.focus()
        else:
            self.password_field.focus()

    def __del__(self):
        print("LoginWindow.__del__")

    def on_text_field_changed(self):
        email = self.username_field.get_text().strip()
        password = self.password_field.get_text().strip()
        self.login_button.set_enabled(bool(email) and bool(password))
        self.reset_label.set_url(
            "https://openretro.org/user/reset?referrer=fs-uae-launcher"
            "&email={0}".format(email)
        )

    def on_username_activated(self):
        if self.username_field.get_text().strip():
            self.password_field.focus()

    def on_password_activated(self):
        self.on_login_activated()

    def on_login_activated(self):
        email = self.username_field.get_text().strip()
        password = self.password_field.get_text().strip()
        if not email or not password:
            return
        self.username_field.set_enabled(False)
        self.password_field.set_enabled(False)
        self.login_button.set_enabled(False)

        task = OGDClient().login_task(email, password)
        # task.progressed.connect(self.progress)
        task.succeeded.connect(self.on_success)
        # task.failed.connect(fsui.error_function(gettext("Login Failed")))
        task.failed.connect(self.on_failure)
        task.start()

    def on_success(self):
        # center = self.get_window_center()
        # fsui.call_after(start_refresh_task, center)
        # shell_open("Workspace:Tools/Refresh", center=self.get_window_center())

        # RefreshWindow.open(self.parent())
        wsopen("SYS:Tools/DatabaseUpdater")

        self.close()

    def on_failure(self, message):
        fsui.show_error(message, parent=self.get_window())
        self.username_field.set_enabled()
        self.password_field.set_enabled()
        self.login_button.set_enabled()
        self.password_field.select_all()
        self.password_field.focus()

from fsgs.ogd.client import OGDClient
import fsui
from fsbc.Application import app
from fs_uae_workspace.shell import SimpleApplication, shell_open
from fs_uae_launcher.res import gettext


class LoginWindow(fsui.Dialog):

    def __init__(self):
        super().__init__(None, gettext("Log In to Your OAGD.net Account"))
        self.set_icon(fsui.Icon("password", "pkg:fs_uae_workspace"))

        self.layout = fsui.VerticalLayout()
        self.layout.set_padding(20, 20, 20, 20)

        heading_layout = fsui.HorizontalLayout()
        self.layout.add(heading_layout)
        heading_layout.add(fsui.ImageView(
            self, fsui.Image("fs_uae_workspace:res/48/password.png")))
        heading_layout.add_spacer(20)
        heading_layout_2 = fsui.VerticalLayout()
        heading_layout.add(
            heading_layout_2, expand=True, fill=False, valign=0.5)
        heading_layout_2.add(fsui.HeadingLabel(
            self, gettext("Log In to Your OAGD.net Account")))
        heading_layout_2.add_spacer(2)
        heading_layout_2.add(fsui.Label(
            self, gettext("Logging in will enable the online game database "
                          "and more")))

        self.layout.add_spacer(20)
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        label = fsui.Label(self, gettext("E-mail:"))
        label.set_min_width(100)
        hori_layout.add(label)
        hori_layout.add_spacer(20)
        self.username_field = fsui.TextField(
            self, app.settings["database_email"])
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
        self.password_field = fsui.PasswordField(self)
        if self.username_field.get_text():
            self.password_field.focus()
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
            self, gettext("Create an account now"),
            "http://oagd.net/user/register?referrer=fs-uae-launcher")
        hori_layout.add(label, expand=True)

        self.layout.add_spacer(6)
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        label = fsui.Label(self,
                           gettext("Forgot your password?"))
        hori_layout.add(label)
        hori_layout.add_spacer(20)
        self.reset_label = fsui.URLLabel(
            self, gettext("Reset password via e-mail"),
            "http://oagd.net/user/reset?referrer=fs-uae-launcher")
        hori_layout.add(self.reset_label, expand=True)

        self.layout.add_spacer(20)
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        self.created_label = fsui.Label(self, "")
        hori_layout.add(self.created_label, expand=True)
        hori_layout.add_spacer(20)
        self.login_button = fsui.Button(self, gettext("Log In"))
        self.login_button.disable()
        self.login_button.activated.connect(self.on_login_activated)
        hori_layout.add(self.login_button)

        self.set_size(self.layout.get_min_size())
        self.center_on_parent()

    def __del__(self):
        print("LoginWindow.__del__")

    def on_text_field_changed(self):
        email = self.username_field.get_text().strip()
        password = self.password_field.get_text().strip()
        self.login_button.enable(bool(email) and bool(password))
        self.reset_label.set_url(
            "http://oagd.net/user/reset?referrer=fs-uae-launcher"
            "&email={0}".format(email))

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
        self.username_field.disable()
        self.password_field.disable()
        self.login_button.disable()

        task = OGDClient().login_task(email, password)
        # task.progressed.connect(self.progress)
        task.succeeded.connect(self.on_success)
        # task.failed.connect(fsui.error_function(gettext("Login Failed")))
        task.failed.connect(self.on_failure)
        task.start()

    def on_success(self):
        shell_open("Workspace:Tools/Refresh", center=self.get_window_center())
        self.close()

    def on_failure(self, message):
        fsui.show_error(message, parent=self.get_window())
        self.username_field.enable()
        self.password_field.enable()
        self.login_button.enable()
        self.password_field.select_all()
        self.password_field.focus()

    # def on_progress(self):
    #    print("on_progress")

    # def on_success(self):
    #     self.close()

application = SimpleApplication(LoginWindow)

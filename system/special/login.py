import fsui
from fsbc.application import app
from fsgamesys.ogd.client import OGDClient
from fswidgets.parentstack import ParentStack
from launcher.fswidgets2.button import Button
from launcher.fswidgets2.flexcontainer import (
    FlexContainer,
    VerticalFlexContainer,
)
from launcher.fswidgets2.imageview import ImageView
from launcher.fswidgets2.label import Label
from launcher.fswidgets2.spacer import Spacer
from launcher.fswidgets2.texfield import TextField
from launcher.fswidgets2.urllabel import UrlLabel
from launcher.fswidgets2.window import Window

# from workspace.shell import SimpleApplication
from launcher.res import gettext
from launcher.ui.widgets import CloseButton
from system.classes.windowcache import WindowCache
from workspace.ui.theme import WorkspaceTheme


def wsopen(window=None, **kwargs):
    WindowCache.open(LoginWindow, center_on_window=window)


# FIXME: UrlLabels should be focusable and "clickable" with keyboard

from fsui import Color, Panel


class WidgetSizeSpinner(Panel):
    def __init__(self, visible: bool = True) -> None:
        parent = ParentStack.top()
        super().__init__(parent)
        parent.layout.add(self)
        self.set_background_color(Color.from_hex("#ff0000"))
        # FIXME
        self.set_min_height(30)
        self.set_min_width(30)
        if not visible:
            self.set_visible(False)


class LoginWindow(Window):
    def __init__(self):
        super().__init__(title=gettext("OpenRetro Login"), maximizable=False)
        # return
        self.set_icon(fsui.Icon("password", "pkg:workspace"))
        # self.theme = WorkspaceTheme.instance()

        with FlexContainer(
            parent=self,
            style={
                "backgroundColor": "#bbbbbb",
                "gap": 20,
                # "marginLeft": 10,
                # "marginRight": 10,
                # "marginTop": 10,
                "padding": 20,
                "paddingBottom": 10,
            },
        ):
            with VerticalFlexContainer(style={"flexGrow": 1, "gap": 5}):
                Label(
                    gettext("Log in to your OpenRetro.org account"),
                    style={"fontWeight": "bold"},
                )
                Label(
                    gettext(
                        "Logging in will enable the online game database "
                        "and more"
                    )
                )
            ImageView(fsui.Image("workspace:/data/48/password.png"))

        with VerticalFlexContainer(
            parent=self,
            style={
                "backgroundColor": "#bbbbbb",
                "gap": 10,
                # "marginLeft": 10,
                # "marginRight": 10,
                # "padding": 10,
                "padding": 20,
                "paddingBottom": 10,
                "paddingTop": 10,
            },
        ):
            labelStyle = {"width": 140}
            with FlexContainer():
                Label(gettext("E-mail:"), style=labelStyle)
                self.username_field = TextField(
                    app.settings["database_email"].strip(),
                    style={"flexGrow": 1},
                )
            with FlexContainer():
                Label(gettext("Password:"), style=labelStyle)
                self.password_field = TextField(
                    type="password", style={"flexGrow": 1}
                )

        # with VerticalFlexContainer(
        #     parent=self,
        #     style={
        #         "backgroundColor": "#ff0000",
        #         "gap": 10,
        #         "padding": 20,
        #         "paddingTop": 0,
        #     },
        # ):
        #     with FlexContainer(style={"gap": 10}):
        #         Label(gettext("Don't have an account already?"))
        #         UrlLabel(
        #             gettext("Create an account now"),
        #             "https://openretro.org/user/register?r=fs-uae-launcher",
        #         )
        #     with FlexContainer(style={"gap": 10}):
        #         Label(gettext("Forgot your password?"))
        #         UrlLabel(
        #             gettext("Reset password via e-mail"),
        #             "https://openretro.org/user/reset?r=fs-uae-launcher",
        #         )

        with FlexContainer(
            parent=self,
            style={
                "backgroundColor": "#bbbbbb",
                "gap": 10,
                # "marginLeft": 10,
                # "marginRight": 10,
                # "padding": 10,
                "padding": 20,
                "paddingBottom": 10,
                "paddingTop": 10,
            },
        ):
            with VerticalFlexContainer(style={"gap": 10}):
                Label(gettext("Don't have an account already?"))
                Label(gettext("Forgot your password?"))
            with VerticalFlexContainer(style={"gap": 10}):
                UrlLabel(
                    gettext("Create an account on openretro.org"),
                    "https://openretro.org/user/register?r=fs-uae-launcher",
                )
                self.reset_label = UrlLabel(
                    gettext("Reset password via e-mail"),
                    "https://openretro.org/user/reset?r=fs-uae-launcher",
                )

        with FlexContainer(
            parent=self,
            style={
                "backgroundColor": "#bbbbbb",
                "gap": 10,
                # "marginBottom": 10,
                # "marginLeft": 10,
                # "marginRight": 10,
                # "padding": 10,
                "padding": 20,
                "paddingTop": 10,
            },
        ):
            Spacer(style={"flexGrow": 1})
            # FIXME: Set visible via stylesheet instead?
            self.spinner = WidgetSizeSpinner(visible=False)
            self.login_button = Button(gettext("Log in"))

        self.username_field.changed.connect(self.on_text_field_changed)
        self.username_field.activated.connect(self.on_username_activated)
        self.password_field.changed.connect(self.on_text_field_changed)
        self.password_field.activated.connect(self.on_password_activated)
        self.login_button.set_enabled(False)
        self.login_button.activated.connect(self.on_login_activated)
        if len(self.username_field.text()) == 0:
            self.username_field.focus()
        else:
            self.password_field.focus()
        # self.spinner.set_visible(False)

    def __del__(self):
        print("LoginWindow.__del__")

    def on_text_field_changed(self):
        print("on_text_field_changed")
        email = self.username_field.get_text().strip()
        password = self.password_field.get_text().strip()
        self.login_button.set_enabled(bool(email) and bool(password))
        self.reset_label.set_url(
            "https://openretro.org/user/reset?r=fs-uae-launcher"
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
        self.spinner.set_visible(True)

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
        self.spinner.set_visible(False)

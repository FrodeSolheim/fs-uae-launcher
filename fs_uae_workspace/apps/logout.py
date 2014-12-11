from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsgs.ogd.client import OGDClient
import fsui
from fsbc.Application import app
from fs_uae_workspace.shell import SimpleApplication
from fs_uae_launcher.res import gettext


class LogoutWindow(fsui.Dialog):

    def __init__(self):
        super().__init__(None, gettext("Log Out from Your OAGD.net Account"))
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
            self, gettext("Log Out from Your OAGD.net Account")))
        heading_layout_2.add_spacer(2)
        heading_layout_2.add(fsui.Label(
            self, gettext("While logged out you will not get "
                          "database updates")))

        self.layout.add_spacer(20)
        hori_layout = fsui.HorizontalLayout()
        self.layout.add(hori_layout, fill=True)
        self.created_label = fsui.Label(self, "")
        hori_layout.add(self.created_label, expand=True)
        hori_layout.add_spacer(20)
        self.logout_button = fsui.Button(self, gettext("Log Out"))
        # self.logout_button.disable()
        self.logout_button.activated.connect(self.on_logout_activated)
        hori_layout.add(self.logout_button)

        self.set_size(self.layout.get_min_size())
        self.center_on_parent()

    def __del__(self):
        print("LogoutWindow.__del__")

    def on_logout_activated(self):
        auth_token = app.settings["database_auth"]
        if auth_token:
            task = OGDClient().logout_task(auth_token)
            # task.progressed.connect(self.progress)
            task.succeeded.connect(self.close)
            # task.failed.connect(fsui.error_function(gettext("Login Failed")))
            task.failed.connect(self.on_failure)
            task.start()
        else:
            # this is not a normal case, no auth token stored, but clear
            # all auth-related settings just in case
            app.settings["database_auth"] = ""
            app.settings["database_username"] = ""
            # app.settings["database_email"] = ""
            app.settings["database_password"] = ""
            self.on_close()

    def on_failure(self, message):
        fsui.show_error(message, parent=self.get_window())

    # def on_progress(self):
    #    print("on_progress")

    # def on_success(self):
    #     app.settings["database_auth"] = ""
    #     app.settings["database_username"] = ""
    #     app.settings["database_email"] = ""
    #     app.settings["database_password"] = ""
    #     self.close()

application = SimpleApplication(LogoutWindow)

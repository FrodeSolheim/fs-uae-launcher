# from fsui import Button, HorizontalLayout, Label, Panel, Color
# from launcher.i18n import gettext
# from system.classes.configdispatch import ConfigDispatch


# class Launcher2RunningPanel(Panel):
#     def __init__(self, parent):
#         super().__init__(parent)
#         horilayout = HorizontalLayout()
#         self.layout.add(
#             horilayout,
#             fill=True,
#             expand=True,
#             margin_top=10,
#             margin_right=10,
#             margin_bottom=10,
#         )
#         self.set_background_color(Color(0xC0C0C0))
#         self.statuslabel = Label(self, "Idle")
#         horilayout.add(
#             self.statuslabel, fill=True, expand=True, margin_left=10
#         )
#         self.cancelbutton = Button(self, gettext("Cancel"))
#         self.cancelbutton.activated.connect(self.__on_cancel)
#         horilayout.add(self.cancelbutton, fill=True, margin_left=10)

#         ConfigDispatch(
#             self,
#             {
#                 "__progress": self.__on_progress_config,
#                 "__running": self.__on_running_config,
#             },
#         )

#     def __on_cancel(self):
#         pass

#     def __on_progress_config(self, event):
#         self.statuslabel.set_text(event.value)

#     def __on_running_config(self, event):
#         isrunning = bool(event.value)
#         self.cancelbutton.set_enabled(isrunning)

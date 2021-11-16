from fsui import Button, HorizontalLayout, Label, TextField, VerticalLayout
from fswidgets.widget import Widget
from launcher.i18n import gettext
from system.classes.window import Window

# TODO: Make escape key close the dialog


class ExecuteDialog(Window):
    def __init__(self, parent: Widget):
        super().__init__(
            parent,
            title=gettext("Execute a file"),
            maximizable=False,
            minimizable=False,
            escape=True,
        )
        vertlayout = VerticalLayout(20)
        self.layout.add(vertlayout, fill=True, expand=True)
        vertlayout.add(
            Label(self, gettext("Enter command and its arguments:"))
        )

        horilayout = HorizontalLayout()
        vertlayout.add(horilayout, fill=True, margin_top=10)
        horilayout.add(Label(self, gettext("Command:")), fill=True)
        self.textfield = TextField(self)
        self.textfield.set_min_width(300)
        self.textfield.activated.connect(self.__on_execute)
        horilayout.add(self.textfield, expand=True, fill=True, margin_left=10)

        # Creating execute button first, so it will become default for when
        # the user presses return in the text field. This only applies when
        # this dialog is implemented as an actual Dialog though.
        self.executebutton = Button(self, gettext("Execute"))
        self.executebutton.activated.connect(self.__on_execute)
        self.cancelbutton = Button(self, gettext("Cancel"))
        self.cancelbutton.activated.connect(self.__on_cancel)

        horilayout = HorizontalLayout()
        vertlayout.add(horilayout, fill=True, margin_top=20)
        horilayout.add_spacer(0, expand=True)
        horilayout.add(self.cancelbutton, margin_left=10)
        horilayout.add(self.executebutton, margin_left=10)
        self._command = ""

    def command(self):
        return self._command

    def __on_cancel(self):
        # self.end_modal(False)
        self.close()

    def __on_execute(self):
        self._command = self.textfield.text().strip()
        self.close()
        # self.end_modal(True)

        from system.wsopen import wsopen

        command = self.command()
        if ":" not in command:
            print("FIXME: Hack, prefixing command with C: for now")
            command = "C:" + command
        wsopen(command)

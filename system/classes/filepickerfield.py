# FIXME: Can use virtual panel / group
from fsui import HorizontalLayout, Signal, TextField, get_window
from fswidgets.panel import Panel
from fswidgets.widget import Widget
from launcher.i18n import gettext
from launcher.ui.IconButton import IconButton
from launcher.ui.LauncherFilePicker import LauncherFilePicker


class FilePickerField(Panel):
    changed = Signal()

    def __init__(self, parent: Widget, *, path: str, placeholder: str = ""):
        super().__init__(parent)
        self.layout = HorizontalLayout()

        self.text_field = TextField(
            self, text=path, placeholder=placeholder, clearbutton=True
        )
        self.text_field.changed.connect(self.__on_text_field_changed)
        self.layout.add(self.text_field, expand=True)

        self.browse_button = IconButton(self, "browse_folder_16.png")
        self.browse_button.set_tooltip(gettext("Browse for File"))
        self.browse_button.activated.connect(self.__on_browse_button)
        # FIXME: Scale 5 here
        self.layout.add(self.browse_button, fill=True, margin_left=5)

    def path(self):
        return self.text_field.text()

    def __on_text_field_changed(self):
        self.changed.emit()

    def __on_browse_button(self):
        # FIXME: Show file picker dialog
        # dialog = FileDialog()
        # dialog.show()

        # FIXME: Choose initial directory based on directory of existing path,
        # if any

        dialog = LauncherFilePicker(
            get_window(self),
            # FIXME
            gettext("Select file"),
            # FIXME
            "floppy",
        )
        if not dialog.show_modal():
            print("dialog.show returned false")
            return
        print("dialog.show returned true")
        path = dialog.get_path()
        self.text_field.set_text(path)

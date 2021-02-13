import fsui

from ...i18n import gettext
from .ImportDialog import ImportDialog


class ImportGroup(fsui.Group):
    AMIGA_FOREVER = 1

    def __init__(self, parent, import_type=0):
        fsui.Group.__init__(self, parent)
        self.type = import_type
        self.path = ""

        self.layout = fsui.VerticalLayout()
        if self.type == self.AMIGA_FOREVER:
            title = gettext("Import From Amiga Forever CD/DVD")
        else:
            title = gettext("Import Kickstarts and ROMs")
        label = fsui.HeadingLabel(self, title)
        self.layout.add(label, margin_bottom=10)

        icon_layout = fsui.HorizontalLayout()
        self.layout.add(icon_layout, fill=True)
        icon_layout.add_spacer(20)
        if self.type == self.AMIGA_FOREVER:
            image = fsui.Image("launcher:res/amiga_forever_group.png")
        else:
            image = fsui.Image("launcher:res/kickstart.png")
        self.image_view = fsui.ImageView(self, image)
        icon_layout.add(self.image_view, valign=0.0, margin_right=10)

        vert_layout = fsui.VerticalLayout()
        icon_layout.add(vert_layout, fill=True, expand=True)

        if self.type == self.AMIGA_FOREVER:
            text = gettext(
                "If you own Amiga Forever, select the drive/folder "
                'and click "{0}"'
            ).format(gettext("Import"))
        else:
            text = gettext(
                "Select a folder containing Amiga kickstart files "
                'and click "{0}"'
            ).format(gettext("Import"))
        label = fsui.Label(self, text)
        vert_layout.add(label, margin_bottom=10)

        hori_layout = fsui.HorizontalLayout()
        vert_layout.add(hori_layout, fill=True, margin=0)
        self.text_field = fsui.TextField(self, "", read_only=True)
        hori_layout.add(self.text_field, expand=True)
        self.browse_button = fsui.Button(self, gettext("Browse"))
        self.browse_button.activated.connect(self.on_browse)
        hori_layout.add(self.browse_button, margin_left=10)
        self.import_button = fsui.Button(self, gettext("Import"))
        self.import_button.activated.connect(self.on_import)
        self.import_button.set_enabled(False)
        hori_layout.add(self.import_button, margin_left=10)

    def set_path(self, path):
        self.path = path
        self.text_field.set_text(path)
        self.import_button.set_enabled()

    def on_browse(self):
        path = fsui.pick_directory(
            self.get_window(), gettext("Select Source Directory")
        )
        if path:
            self.set_path(path)

    def on_import(self):
        dialog = ImportDialog(self.get_window(), self.path, self.type)
        # dialog.show_modal()
        # dialog.destroy()
        dialog.show()
        # Signal.broadcast("scan_done")

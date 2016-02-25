import workspace
import workspace.ui
from workspace.util.help_button import HelpButton
from workspace.util.browse_button import BrowseButton


# FIXME: Extract ADF files as well


class ArchiveExtractorApplication(workspace.ui.Application):
    def __init__(self):
        super().__init__("archive_extractor")
        self.window = ArchiveExtractorWindow(self)
        self.window.show()

    def arguments(self, args):
        print("Archive Extractor player got args", args)
        self.window.set_playlist(args)


class ArchiveExtractorWindow(workspace.ui.Window):
    def __init__(self, parent):
        super().__init__(
            parent, "Archive Extractor", maximizable=False, menu=True)
        self.create_menu()
        col = workspace.ui.Column(self)
        col.add_spacer(540, 0)

        self.source_area = SourceArea(self)
        col.add(self.source_area)
        col.add(workspace.ui.TitleSeparator(self))

        # row = workspace.gui.Row()
        # col.add(row, margin=20)
        #
        # self.image_view = workspace.gui.ImageView(self, workspace.gui.Image(
        #     workspace.Stream(__name__, "data/package-x-generic.png")))
        # row.add(self.image_view, top=-10, bottom=-10, right=10)
        #
        # col2 = workspace.gui.Column()
        # row.add(col2, expand=True, fill=False, top=0)
        #
        # self.module_label = workspace.gui.Label(
        #     self, "No archive loaded", font="16px Medium Roboto")
        # col2.add(self.module_label)
        #
        # col.spacer(2)
        #
        # self.format_row = workspace.gui.Row()
        # col2.add(self.format_row)
        #
        # self.format_label = workspace.gui.Label(self, "SOURCE ARCHIVE")
        # # font = self.format_label.get_font()
        # # font.adjust_size(-1)
        # font = workspace.gui.Font("Roboto", 12)
        # self.format_label.set_font(font)
        # self.format_label.set_text_color(workspace.gui.Color(0x80, 0x80, 0x80))
        # self.format_row.add(self.format_label, expand=True)
        # # self.play_button = workspace.gui.Button(self, "Song")
        # # row.add(self.play_button)
        #
        # self.format_label_2 = workspace.gui.Label(self, "ZIP")
        # self.format_label_2.set_font(font)
        # self.format_label_2.set_text_color(workspace.gui.Color(0x80, 0x80, 0x80))
        # self.format_row.add(self.format_label_2, right=20)

        row = col.row(margin=20, bottom=10)
        row.add(workspace.ui.Label(self, "Destination folder" + ":"))
        row.expand()
        self.items_label = workspace.ui.Label(self, "4 root items will be created")
        row.add(self.items_label)

        row = col.row(margin=20, top=0)
        self.dir_field = workspace.ui.TextField(self, "Ram:Temp4")
        row.add(self.dir_field, expand=True)
        self.browse_button = BrowseButton(self)
        row.add(self.browse_button, left=10)

        row = col.row(margin=20, top=0)
        # FIXME
        import fsui
        row.add(workspace.ui.Label(self, "Character set:"))
        self.charset_choice = fsui.Choice(
            self, ["ISO-8859-1", "UTF-8", "CP437"])
        row.add(self.charset_choice, left=10)
        row.expand()
        row.add(workspace.ui.Label(self, "Create .uaem metadata:"))
        self.meta_choice = fsui.Choice(
            self, ["When needed", "Always", "Never"])
        row.add(self.meta_choice, left=10)
        # self.meta_checkbox = fsui.CheckBox(
        #     self, "Create .uaem files when needed", True)
        # row.add(self.meta_checkbox, left=20)

        # row = workspace.gui.Row()
        # col.add(row, margin=20)
        #
        # self.image_view = workspace.gui.ImageView(self, workspace.gui.Image(
        #     workspace.Stream(__name__, "data/folder.png")))
        # row.add(self.image_view, right=10)
        #
        # col2 = workspace.gui.Column()
        # row.add(col2, expand=True, fill=False, top=0)
        #
        # self.module_label = workspace.gui.Label(
        #     self, "No destination selected", font="16px Medium Roboto")
        # col2.add(self.module_label)

        row = workspace.ui.Row()
        # FIXME
        row.add_spacer(0, 32)
        col.add(row, margin=20)

        button = HelpButton(self, "")
        row.add(button)

        button = workspace.ui.Button(self, "Extract")
        row.expand()
        row.add(button)

    def create_menu(self):
        menu = workspace.ui.Menu(self)
        menu.add_item("Load File", self.on_settings)
        menu.add_separator()
        menu.add_item("Settings", self.on_settings)
        menu.add_item("Reset to Defaults", self.on_settings)
        menu.add_separator()
        menu.add_item("About", self.on_about)
        self.set_menu(menu)

    def on_about(self):
        print("on_about")

    def on_settings(self):
        print("on_settings")


class SourceArea(workspace.ui.TitlePanel):
    def __init__(self, parent):
        super().__init__(parent)
        row = workspace.ui.Row(self, padding=20)

        self.image_view = workspace.ui.ImageView(self, workspace.ui.Image(
            workspace.Stream(__name__, "data/48/zip-file.png")))
        row.add(self.image_view, top=-10, bottom=-10, right=10)

        col = workspace.ui.Column()
        row.add(col, expand=True, fill=False, top=0)

        self.source_label = workspace.ui.Label(
            self, "No archive loaded", font="16px Medium Roboto")
        col.add(self.source_label)

        col.spacer(2)
        self.format_row = workspace.ui.Row()
        col.add(self.format_row)

        # self.format_label = workspace.gui.Label(self, "ZIP ARCHIVE")
        self.format_label = workspace.ui.Label(
            self, "DROP FILE HERE TO LOAD")
        font = workspace.ui.Font("Roboto", 12)
        self.format_label.set_font(font)
        self.format_label.set_text_color(workspace.ui.Color(0x80, 0x80, 0x80))
        self.format_row.add(self.format_label, expand=True)
        # self.format_label_2 = workspace.gui.Label(self, "ISO-8859-1")
        # self.format_label_2.set_font(font)
        # self.format_label_2.set_text_color(workspace.gui.Color(0x80, 0x80, 0x80))
        # self.format_row.add(self.format_label_2)

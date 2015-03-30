from fsbc.task import Task
import fsui as fsui
from fsui.extra.taskdialog import TaskDialog
from ...I18N import gettext
from fsui.extra.iconheader import IconHeader
from fsgs.context import fsgs
from fsgs.Database import Database
from fsgs.FileDatabase import FileDatabase
from fsgs.LockerDatabase import LockerDatabase
from fsgs.ogd.client import OGDClient


class MaintenanceSettingsPage(fsui.Panel):

    def __init__(self, parent):
        fsui.Panel.__init__(self, parent)
        self.layout = fsui.VerticalLayout()
        # self.layout.set_padding(20, 20, 20, 20)

        self.icon_header = IconHeader(
            self, fsui.Icon("maintenance", "pkg:fs_uae_workspace"),
            gettext("Maintenance"),
            gettext("Miscellaneous functions to optimize {name}").format(
                name="FS-UAE Launcher"))
        self.layout.add(self.icon_header, fill=True, margin_bottom=20)

        # label = fsui.HeadingLabel(self, gettext("Defragment Databases"))
        # self.layout.add(label, fill=True, margin_top=20)

        # hori_layout = fsui.HorizontalLayout()
        # self.layout.add(hori_layout, fill=True, margin_top=10)
        # label = fsui.Label(self, gettext(
        #     "Defragmenting the databases will improve performance"))
        # hori_layout.add(label, expand=True)

        label = fsui.MultiLineLabel(self, gettext(
            "Defragmenting the databases will improve performance "
            "by ensuring that tables and indices are stored contiguously "
            "on disk. It will also reclaim some storage space."), 640)
        self.layout.add(label, fill=True, margin_top=20)

        button = fsui.Button(self, gettext("Defragment Databases"))
        button.activated.connect(self.on_defragment_button)
        # hori_layout.add(button, margin_left=20)
        self.layout.add(button, margin_top=20)

    def on_defragment_button(self):
        TaskDialog(self.get_window(), DefragmentDatabasesTask()).show()


class DefragmentDatabasesTask(Task):

    def __init__(self):
        Task.__init__(self, gettext("Defragment Databases"))

    def run(self):
        self.defragment(FileDatabase.get_instance(), "Files.sqlite")
        self.stop_check()
        self.defragment(LockerDatabase.instance(), "Locker.sqlite")
        self.stop_check()
        self.defragment(fsgs.get_game_database(),
                        OGDClient.get_server() + ".sqlite")
        self.stop_check()
        self.defragment(Database.get_instance(), "Database.sqlite")

    def defragment(self, database, name):
        self.set_progress(gettext("Defragmenting {name}").format(name=name))
        with database:
            cursor = database.cursor()
            cursor.execute("VACUUM")

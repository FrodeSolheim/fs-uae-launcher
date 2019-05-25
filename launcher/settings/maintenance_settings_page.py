from fsbc.task import Task
from fsgs.Database import Database
from fsgs.filedatabase import FileDatabase
from fsgs.LockerDatabase import LockerDatabase
from fsgs.context import fsgs
from launcher.i18n import gettext


# class MaintenanceSettingsPage(SettingsPage):
#
#     def __init__(self, parent):
#         super().__init__(parent)
#         icon = fsui.Icon("maintenance", "pkg:workspace")
#         title = gettext("Maintenance")
#         subtitle = gettext("Miscellaneous functions to optimize {name}").format(
#                            name="FS-UAE Launcher")
#         self.add_header(icon, title, subtitle)
#
#         label = fsui.MultiLineLabel(self, gettext(
#             "Defragmenting the databases will improve performance "
#             "by ensuring that tables and indices are stored contiguously "
#             "on disk. It will also reclaim some storage space."), 640)
#         self.layout.add(label, fill=True, margin_top=20)
#
#         button = fsui.Button(self, gettext("Defragment Databases"))
#         button.activated.connect(self.on_defragment_button)
#         self.layout.add(button, margin_top=20)
#
#     def on_defragment_button(self):
#         TaskDialog(self.get_window(), DefragmentDatabasesTask()).show()


class DefragmentDatabasesTask(Task):
    def __init__(self):
        Task.__init__(self, gettext("Defragment Databases"))

    def run(self):
        self.defragment(FileDatabase.get_instance(), "Files.sqlite")
        self.stop_check()
        self.defragment(LockerDatabase.instance(), "Locker.sqlite")
        self.stop_check()
        self.defragment(fsgs.get_game_database(), "Amiga.sqlite")
        self.stop_check()
        self.defragment(Database.get_instance(), "Database.sqlite")

    def defragment(self, database, name):
        self.set_progress(gettext("Defragmenting {name}").format(name=name))
        with database:
            cursor = database.cursor()
            cursor.execute("VACUUM")

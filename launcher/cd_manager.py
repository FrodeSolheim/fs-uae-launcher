from fsbc.paths import Paths
from fsgs.FSGSDirectories import FSGSDirectories
from fsgs.amiga.amiga import Amiga
from launcher.i18n import gettext
from launcher.launcher_config import LauncherConfig
from launcher.ui.LauncherFilePicker import LauncherFilePicker


class CDManager:
    @classmethod
    def clear_all(cls):
        for i in range(1):
            cls.eject(i)
        cls.clear_cdrom_list()

    @classmethod
    def eject(cls, drive):
        values = [("cdrom_drive_{0}".format(drive), ""),
                  ("x_cdrom_drive_{0}_sha1".format(drive), "")]
        LauncherConfig.set_multiple(values)

    @classmethod
    def clear_cdrom_list(cls):
        values = []
        for i in range(Amiga.MAX_CDROM_IMAGES):
            values.append(("cdrom_image_{0}".format(i), ""))
            values.append(("x_cdrom_image_{0}_sha1".format(i), ""))
        LauncherConfig.set_multiple(values)

    @classmethod
    def multi_select(cls, parent=None):
        default_dir = FSGSDirectories.get_cdroms_dir()
        dialog = LauncherFilePicker(
            parent, gettext("Select Multiple CD-ROMs"), "cd", multiple=True)

        if not dialog.show_modal():
            return
        paths = dialog.get_paths()
        paths.sort()

        # checksum_tool = ChecksumTool(parent)
        for i, path in enumerate(paths):
            # sha1 = checksum_tool.checksum(path)
            sha1 = ""
            print("FIXME: not calculating CD checksum just yet")
            path = Paths.contract_path(path, default_dir)

            if i < 1:
                LauncherConfig.set_multiple([
                    ("cdrom_drive_{0}".format(i), path),
                    ("x_cdrom_drive_{0}_sha1".format(i), sha1)
                ])
            LauncherConfig.set_multiple([
                ("cdrom_image_{0}".format(i), path),
                ("x_cdrom_image_{0}_sha1".format(i), sha1)
            ])

        # blank the rest of the drives
        for i in range(len(paths), 1):
            LauncherConfig.set_multiple([
                ("cdrom_drive_{0}".format(i), ""),
                ("x_cdrom_drive_{0}_sha1".format(i), "")
            ])

            # Config.set("x_cdrom_drive_{0}_sha1".format(i), "")
            # Config.set("x_cdrom_drive_{0}_name".format(i), "")
        # blank the rest of the image list
        for i in range(len(paths), Amiga.MAX_CDROM_IMAGES):
            LauncherConfig.set_multiple([
                ("cdrom_image_{0}".format(i), ""),
                ("x_cdrom_image_{0}_sha1".format(i), "")
            ])

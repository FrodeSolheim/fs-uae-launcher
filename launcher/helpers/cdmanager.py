from fsbc.paths import Paths
from fsgamesys.amiga.amiga import Amiga
from fsgamesys.FSGSDirectories import FSGSDirectories
from launcher.i18n import gettext
from launcher.ui.LauncherFilePicker import LauncherFilePicker


class CDManager:
    @classmethod
    def clear_all(cls, *, config):
        for i in range(1):
            cls.eject(i, config=config)
        cls.clear_cdrom_list(config=config)

    @classmethod
    def eject(cls, drive, *, config):
        values = [
            ("cdrom_drive_{0}".format(drive), ""),
            ("x_cdrom_drive_{0}_sha1".format(drive), ""),
        ]
        config.set_multiple(values)

    @classmethod
    def clear_cdrom_list(cls, *, config):
        values = []
        for i in range(Amiga.MAX_CDROM_IMAGES):
            values.append(("cdrom_image_{0}".format(i), ""))
            values.append(("x_cdrom_image_{0}_sha1".format(i), ""))
        config.set_multiple(values)

    @classmethod
    def multi_select(cls, parent=None, *, config):
        default_dir = FSGSDirectories.get_cdroms_dir()
        dialog = LauncherFilePicker(
            parent, gettext("Select multiple CD-ROMs"), "cd", multiple=True
        )

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
                config.set_multiple(
                    [
                        ("cdrom_drive_{0}".format(i), path),
                        ("x_cdrom_drive_{0}_sha1".format(i), sha1),
                    ]
                )
            config.set_multiple(
                [
                    ("cdrom_image_{0}".format(i), path),
                    ("x_cdrom_image_{0}_sha1".format(i), sha1),
                ]
            )

        # blank the rest of the drives
        for i in range(len(paths), 1):
            config.set_multiple(
                [
                    ("cdrom_drive_{0}".format(i), ""),
                    ("x_cdrom_drive_{0}_sha1".format(i), ""),
                ]
            )

            # Config.set("x_cdrom_drive_{0}_sha1".format(i), "")
            # Config.set("x_cdrom_drive_{0}_name".format(i), "")
        # blank the rest of the image list
        for i in range(len(paths), Amiga.MAX_CDROM_IMAGES):
            config.set_multiple(
                [
                    ("cdrom_image_{0}".format(i), ""),
                    ("x_cdrom_image_{0}_sha1".format(i), ""),
                ]
            )

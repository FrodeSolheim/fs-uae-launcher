import os
import shutil

from fsbc.fs import get_data_dir
from fsgs.FSGSDirectories import FSGSDirectories


class ApplicationMixin(object):
    def get_settings_path(self):
        settings_ini = os.path.join(
            FSGSDirectories.get_data_dir(), "Settings.ini"
        )
        if not os.path.exists(settings_ini):
            migrate_list = [
                os.path.join(
                    FSGSDirectories.get_data_dir(), "FS-UAE Launcher.ini"
                )
            ]
            portable_ini = os.path.join(
                FSGSDirectories.get_base_dir(), "Portable.ini"
            )
            if not os.path.exists(portable_ini):
                # not portable, can migrate settings from old
                # launcher.settings file
                migrate_list.append(
                    os.path.join(get_data_dir(), "fs-uae", "launcher.settings")
                )
            # move the highest-priority settings file if present
            for migrate in migrate_list:
                if os.path.exists(migrate):
                    shutil.move(migrate, settings_ini)
                    break
            # remove all old settings files
            for migrate in migrate_list:
                if os.path.exists(migrate):
                    os.remove(migrate)

        return settings_ini

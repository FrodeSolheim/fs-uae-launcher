from fsgamesys.amiga.harddrives import prepare_amiga_hard_drives
from fsgamesys.amiga.roms import prepare_amiga_roms
from fsgamesys.amiga.types import ConfigType
from fsgamesys.files.installablefiles import InstallableFiles


def prepare_amiga(config: ConfigType) -> InstallableFiles:
    files: InstallableFiles = {}
    # print(Config(config).run_dir())
    prepare_amiga_roms(config, files)
    prepare_amiga_hard_drives(config, files)
    # print(files)
    return files

from fsgamesys.amiga.harddrives import prepare_amiga_hard_drives
from fsgamesys.amiga.roms import prepareAmigaRoms
from fsgamesys.amiga.types import ConfigType
from fsgamesys.files.installablefiles import InstallableFiles


def prepare_amiga(config: ConfigType) -> InstallableFiles:
    files: InstallableFiles = {}
    # print(Config(config).run_dir())
    prepareAmigaRoms(config, files)
    prepare_amiga_hard_drives(config, files)
    # print(files)
    return files

from fsgamesys.amiga.harddrives import prepare_amiga_hard_drives
from fsgamesys.amiga.roms import prepare_amiga_roms
from fsgamesys.amiga.types import ConfigType, FilesType


def prepare_amiga(config: ConfigType) -> FilesType:
    files: FilesType = {}
    # print(Config(config).run_dir())
    prepare_amiga_roms(config, files)
    prepare_amiga_hard_drives(config, files)
    # print(files)
    return files

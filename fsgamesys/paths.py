from fsgamesys.FSGSDirectories import FSGSDirectories


def fsgs_data_dir() -> str:
    return FSGSDirectories.get_data_dir()

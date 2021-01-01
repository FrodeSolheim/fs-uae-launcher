import sys

import fsboot
import workspace.ui


class RunApplication(workspace.ui.Application):
    """An application for browsing the virtual file hierarchy."""

    def __init__(self):
        super().__init__("Run")

    def init(self, args):
        pass


def app_main():
    fsboot.set("fws", "1")
    # Calculate base dir before we start messing with sys.argv[0]
    fsboot.base_dir()

    app = RunApplication()
    import workspace.shell

    if len(sys.argv) == 1:
        workspace.shell.workspace_open("SYS:System/FileManager", ["VOLUMES:"])
    else:
        workspace.shell.workspace_open(sys.argv[1], sys.argv[2:])
    app.run()

    from fsbc.application import Application

    Application.wait_for_threads()

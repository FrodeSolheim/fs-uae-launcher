import os
import fsui
import workspace.path


class Image(fsui.Image):

    def __init__(self, path):
        if hasattr(path, "read"):
            # Stream
            pass
        elif os.path.isfile(path):
            # Native path
            pass
        else:
            path = workspace.path.host(path)
        super().__init__(path)

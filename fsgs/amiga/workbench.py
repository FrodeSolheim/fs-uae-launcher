import os
import hashlib
import traceback
from fsgs.amiga.adf import ADFFile
from .workbench_data import wb_204_startup_sequence, wb_204_files
from .workbench_data import wb_204_floppies
from .workbench_data import wb_300_startup_sequence, wb_300_files
from .workbench_data import wb_300_floppies


class WorkbenchExtractor(object):

    def __init__(self, fsgs):
        self.fsgs = fsgs
        self.cached_adf = None
        self.cached_adf_sha1 = None

    def install_version(self, version, dest_dir):
        if version == "2.04":
            startup_sequence = wb_204_startup_sequence
            files = wb_204_files
            floppies = wb_204_floppies
        elif version == "3.0":
            startup_sequence = wb_300_startup_sequence
            files = wb_300_files
            floppies = wb_300_floppies
        else:
            raise Exception("Unsupported WB version")

        for name, sha1 in files.items():
            name = name.rstrip("/")
            dest_path = os.path.join(dest_dir, name)
            if not sha1:
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                continue
            self.copy_workbench_file(name, sha1, dest_path, floppies)
        with open(os.path.join(dest_dir, "S", "Startup-Sequence"), "wb") as f:
            f.write(startup_sequence.replace("\r\n", "\n").encode("ISO-8859-1"))

    def copy_workbench_file(self, name, sha1, dest_path, floppies):
        print("copying workbench file", name)
        if not os.path.exists(os.path.dirname(dest_path)):
            os.makedirs(os.path.dirname(dest_path))
        # for floppy_sha1, name in workbench_file_map[sha1]:

        if self.cached_adf is not None:
            # using a cached/in-memory ADF object is very efficient here
            # compared to parsing the ADF from scratch for every file
            if self.cached_adf_sha1 in floppies:
                result = self.extract_workbench_file(self.cached_adf,
                                                     name, dest_path)
                assert result == sha1
                return

        for floppy_sha1 in floppies:
            path = self.fsgs.file.find_by_sha1(floppy_sha1)
            if path:
                try:
                    input_stream = self.fsgs.file.open(path)
                except Exception:
                    traceback.print_exc()
                else:
                    wb_data = input_stream.read()
                    adf = ADFFile(wb_data)
                    self.cached_adf = adf
                    self.cached_adf_sha1 = floppy_sha1
                    result = self.extract_workbench_file(adf, name, dest_path)
                    assert result == sha1
                    return
        else:
            raise Exception("Could not find workbench file {0}".format(sha1))

    def extract_workbench_file(self, adf, name, dest):
        input_stream = adf.open(name, "r")
        data = input_stream.read()
        with open(dest, "wb") as f:
            f.write(data)
        return hashlib.sha1(data).hexdigest()

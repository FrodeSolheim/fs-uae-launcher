import json

from fsgamesys.options.option import Option


class Config:
    def __init__(self, config):
        self._config = config
        # self.run_dir = ""
        # self.unsafe_save_states = ""
        # self.save_states = ""

    def amiga_model(self):
        return self._config.get("amiga_model", "A500").upper()

    def file_list(self):
        return json.loads(self._config["file_list"])

    def hard_drive_n(self, n: int):
        return self._config["hard_drive_" + str(n)]

    def hd_startup(self):
        return self._config["hd_startup"]

    def hd_requirements(self):
        values = []
        for value in self._config["hd_requirements"].split(","):
            values.append(value.strip())
        return values

    def hdinst_args(self):
        return self._config["x_hdinst_args"]

    def run_dir(self):
        return self._config["run_dir"]

    def set_hard_drive_n(self, n, path):
        self._config["hard_drive_" + str(n)] = path
        print("set hard_drive_" + str(n), path)

    def set_save_states(self, allow_save_states):
        self._config[Option.SAVE_STATES] = "1" if allow_save_states else "0"

    def set_whdload_quit_key(self, value):
        self._config[Option.WHDLOAD_QUIT_KEY] = value

    def unsafe_save_states(self):
        return self._config[Option.UNSAFE_SAVE_STATES] == "1"

    def whdload_args(self):
        return self._config[Option.X_WHDLOAD_ARGS].strip()

    def whdload_version(self):
        return self._config.get("x_whdload_version", "")

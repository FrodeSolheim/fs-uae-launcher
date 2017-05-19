import json
from collections import defaultdict

from fsgs.network import openretro_url_prefix


class SimpleLoader:
    def __init__(self, fsgs):
        self.fsgs = fsgs
        self.config = {}

    def get_config(self):
        return self.config.copy()

    def load_files(self, values):
        file_list = json.loads(values["file_list"])
        if len(file_list) == 0:
            self.config["x_variant_error"] = "Variant has empty file list"
        elif len(file_list) > 1:
            self.config["x_variant_error"] = "Unsupported multi-file variant"

        self.config["cartridge_slot"] = "sha1://{0}/{1}".format(
            file_list[0]["sha1"], file_list[0]["name"])

        self.config["cue_sheets"] = values["cue_sheets"]


    def load_extra(self, values):
        pass

    def load_basic(self, values):
        self.config["command"] = values["command"]
        self.config["game_name"] = values["game_name"]
        self.config["variant_name"] = values["variant_name"]
        self.config["model"] = values["model"]
        self.config["platform"] = values["platform"]
        self.config["protection"] = values["protection"]
        self.config["viewport"] = values["viewport"]
        self.config["video_standard"] = values["video_standard"]

    def load_info(self, values):
        self.config["languages"] = values["languages"]
        self.config["players"] = values["players"]
        self.config["year"] = values["year"]
        self.config["publisher"] = values["publisher"]
        self.config["developer"] = values["developer"]

        self.config["x_game_notice"] = values["game_notice"]
        self.config["x_variant_notice"] = values["variant_notice"]
        self.config["x_variant_warning"] = values["variant_warning"]
        self.config["x_variant_error"] = values["variant_error"]

        self.config["database_url"] = "{0}/game/{1}".format(
            openretro_url_prefix(), values["parent_uuid"])
        for key in ["mobygames_url"]:
            self.config[key] = values[key]

        for key in ["download_file", "download_page", "download_terms",
                    "download_notice"]:
            if key in values:
                self.config[key] = values[key]

    def load_images(self, values):
        for key in ["front_sha1", "screen1_sha1", "screen2_sha1",
                    "screen3_sha1", "screen4_sha1", "screen5_sha1",
                    "title_sha1"]:
            self.config[key] = values[key]

    def load_values(self, key_values):
        # print(key_values)
        values = defaultdict(str)
        values.update(key_values)

        self.load_basic(values)
        self.load_extra(values)
        self.load_info(values)
        self.load_images(values)
        self.load_files(values)

        return self.get_config()

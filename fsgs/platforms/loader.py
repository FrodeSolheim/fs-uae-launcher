from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import six
from collections import defaultdict
from fsgs.ogd.client import OGDClient


class SimpleLoader:

    def __init__(self, fsgs):
        self.fsgs = fsgs
        self.config = {}

    def get_config(self):
        return self.config.copy()

    def load_files(self, values):
        file_list = json.loads(values["file_list"])
        assert len(file_list) == 1
        self.config["cartridge"] = "sha1://{0}/{1}".format(
            file_list[0]["sha1"], file_list[0]["name"])

    def load_extra(self, values):
        pass

    def load_basic(self, values):
        for key in ["command"]:
            if key in values:
                self.config[key] = values[key]

        self.config["platform"] = values["platform"]
        self.config["model"] = values["model"]

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

        self.config["database_url"] = "http://{0}/game/{1}".format(
            OGDClient.get_server(), values["parent_uuid"])
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
        values = defaultdict(six.text_type)
        values.update(key_values)

        self.load_basic(values)
        self.load_files(values)
        self.load_extra(values)
        self.load_info(values)
        self.load_images(values)

        return self.get_config()

import os

from fsgs.filedatabase import FileDatabase
from fsgs.util.gamenameutil import GameNameUtil

from .i18n import gettext


class ConfigurationScanner:
    def __init__(self, paths=None, on_status=None, stop_check=None):
        if paths is None:
            paths = []
        self.paths = paths
        self.on_status = on_status
        self._stop_check = stop_check
        self.scan_count = 0

    def stop_check(self):
        if self._stop_check:
            return self._stop_check()

    def set_status(self, title, status):
        if self.on_status:
            self.on_status((title, status))

    def scan_fs_uae_files(self, database):
        cursor = database.cursor()
        cursor.execute("SELECT id, path FROM game WHERE path IS NOT NULL")
        config_path_ids = {}
        for row in cursor:
            config_path_ids[database.decode_path(row[1])] = row[0]

        file_database = FileDatabase.get_instance()
        configurations = file_database.find_files(ext=".fs-uae")
        for c in configurations:
            if self.stop_check():
                break
            # name = os.path.basename(c["path"])
            # name = c["name"]
            # name = name[:-7]
            # search = name.lower()
            path = c["path"]
            name = os.path.basename(path)
            name, ext = os.path.splitext(name)
            sort_key = name.lower()
            # search = self.create_configuration_search(name)
            name = self.create_configuration_name(name)

            game_id = database.add_configuration(
                path=path, name=name, sort_key=sort_key
            )
            database.update_game_search_terms(
                game_id, self.create_search_terms(name)
            )

            print(config_path_ids)
            try:
                del config_path_ids[path]
            except KeyError:
                pass

                # FIXME: try splitting name into name, variant pair, and
                # actually add game_variant for config files as well, where
                # possible

        for id in config_path_ids.values():
            database.delete_game(id=id)

    def scan(self, database):
        self.set_status(
            gettext("Scanning configurations"), gettext("Please wait...")
        )

        self.set_status(
            gettext("Scanning configurations"),
            gettext("Scanning .fs-uae files..."),
        )
        self.scan_fs_uae_files(database)

        if self.stop_check():
            # aborted
            # database.rollback()
            return

            # database.remove_unscanned_configurations(self.scan_version)
            # print("remove unscanned games")
            # self.set_status(_("Scanning configurations"),
            #                 _("Purging old entries..."))
            # database.remove_unscanned_games_new(self.scan_version)
            # print("remove unscanned configurations")
            # database.remove_unscanned_configurations(self.scan_version)

            # self.set_status(_("Scanning configurations"), _("Committing
            # data..."))
            # database.commit()

    # @classmethod
    # def create_configuration_search(cls, name):
    #     return name.lower()

    @classmethod
    def create_search_terms(cls, name):
        search_terms = set()
        game_name = name.split("(", 1)[0]
        search_terms.update(GameNameUtil.extract_index_terms(game_name))
        return search_terms

    @classmethod
    def create_configuration_name(cls, name):
        if "(" in name:
            primary, secondary = name.split("(", 1)
            secondary = secondary.replace(", ", " \u00b7 ")
            # name = primary.rstrip() + " \u2013 " + secondary.lstrip()
            name = primary.rstrip() + "\n" + secondary.lstrip()
            if name[-1] == ")":
                name = name[:-1]
            name = name.replace(") (", " \u00b7 ")
            name = name.replace(")(", " \u00b7 ")
        return name

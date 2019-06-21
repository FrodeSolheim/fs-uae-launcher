import os
import shutil
import tempfile
import threading
import time
import traceback
import weakref
from fsbc.paths import Paths
from fsbc.util import unused
from fsgs.archive import Archive
from fsgs.BaseContext import BaseContext
from fsgs.Database import Database
from fsgs.filedatabase import FileDatabase
from fsgs.GameDatabase import GameDatabase, IncompleteGameException
from fsgs.LockerDatabase import LockerDatabase
from fsgs.download import Downloader, offline_mode
from fsgs.network import is_http_url
from fsgs.ogd.locker import is_locker_enabled, open_locker_uri
from fsgs.plugins.pluginmanager import PluginManager


class NotFoundError(RuntimeError):
    pass


class File(object):
    def __init__(self, path):
        self.path = path


class FileContext(BaseContext):
    def __init__(self, main_context):
        BaseContext.__init__(self, main_context)

    def find_by_sha1(self, sha1):
        # FIXME: check_sha1 should check with PluginManager directly?
        database = FileDatabase.instance()
        result = database.find_file(sha1=sha1)["path"]
        if not result:
            path = Downloader.get_cache_path(sha1)
            if os.path.exists(path):
                result = path
        #    result = self.context.get_game_database().find_file_by_sha1(sha1)
        # print("find by sha1", sha1, "in file database - result", result)
        if not result and is_locker_enabled() and not offline_mode():
            database = LockerDatabase.instance()
            if database.check_sha1(sha1):
                result = "locker://" + sha1
            # print("find by sha1", sha1, "in locker database - result",
            # result)
        return result

    def check_sha1(self, sha1):
        # FIXME: check_sha1 should check with PluginManager directly?
        database = FileDatabase.instance()
        result = database.check_sha1(sha1)
        if not result and is_locker_enabled():
            database = LockerDatabase.instance()
            result = database.check_sha1(sha1)
            # print("check sha1", sha1, "in locker database - result", result)
        # if not result:
        #     result = self.context.get_game_database().find_file_by_sha1(sha1)
        return result

    def get_license_code_for_url(self, url):
        return self.context.get_game_database().get_license_code_for_url(url)

    # FIXME: better name
    def convert_uri(self, uri, prefer_path=False):
        if uri.startswith("sha1://"):
            return self.open_sha1_uri(uri)
        elif uri.startswith("db://"):
            # old name for sha1://
            return self.open_sha1_uri(uri)
        elif is_http_url(uri):
            return self.open_url(uri)
        elif uri.startswith("locker://"):
            return open_locker_uri(uri)
        else:
            if uri.startswith("$"):
                uri = Paths.expand_path(uri)
            if prefer_path and os.path.exists(uri):
                # return helper object so isinstance does not match with str
                return File(uri)
            return Archive(uri).open(uri)

    def open(self, uri, prefer_path=False):
        print("[FILES] Open", uri)
        while isinstance(uri, str):
            uri = self.convert_uri(uri, prefer_path=prefer_path)
        if prefer_path and isinstance(uri, File):
            # is a path
            return uri.path
        elif hasattr(uri, "read"):
            # is a file object
            return uri
        elif uri is None:
            # file was not found
            return None
        raise Exception("unexpected result in fsgs.file.open")

    def open_sha1_uri(self, uri):
        sha1 = uri.split("/")[2]
        assert len(sha1) == 40
        return self.find_by_sha1(sha1)

    def open_url(self, url):
        original_url = url
        hash_part = ""
        parts = url.split("#", 1)
        if len(parts) > 1:
            url = parts[0]
            hash_part = "#" + parts[1]
        if not Downloader.cache_file_from_url(url, download=False):
            license_code = self.get_license_code_for_url(original_url)
            license_status = {"accepted": False, "done": False}

            def show_license_code():
                try:
                    try:
                        license_status["accepted"] = self.show_license_code(
                            license_code
                        )
                    except Exception:
                        traceback.print_exc()
                finally:
                    license_status["done"] = True

            if license_code:
                print("URL", url, "has license code", license_code)
                # FIXME: remove direct dependency on fsui
                import fsui as fsui

                fsui.call_after(show_license_code)
                while not license_status["done"]:
                    time.sleep(0.1)
                if not license_status["accepted"]:
                    # FIXME: custom exception here
                    raise Exception(
                        'Usage terms "{0}" was not '
                        "accepted".format(license_code)
                    )
        path = Downloader.cache_file_from_url(url)
        return path + hash_part

    def show_license_code(self, license_code):
        if license_code == "BTTR":
            license_text = (
                "Files for this game are provided by back2roots.org.\n\n"
                "By using back2roots.org or any of their services you "
                "agree to their Acceptable Usage Policy:\n\n"
                "http://www.back2roots.org/About/Project/Policy/"
            )
        else:
            license_text = license_code
        return self.on_show_license_information(license_text)

    def on_show_license_information(self, license_text):
        unused(license_text)
        print("*** on_show_license_information not implemented ***")
        raise Exception("on_show_license_information not implemented")

    def copy_game_file(self, src, dst):
        try:
            return self._copy_game_file(src, dst)
        except NotFoundError as e:
            if self.context.config.get("download_file"):
                # we should be able to find all missing files after we have
                # downloaded and extracted this archive
                self.download_game_file_archive(
                    self.context.config.get("download_file")
                )
                # now try to re-open the file (should be found in the cache
                return self._copy_game_file(src, dst)
            raise e

    def _copy_game_file(self, src, dst):
        ifs = self.open(src, prefer_path=True)
        if not ifs:
            raise NotFoundError("Could not find file for {0}".format(src))

        if os.path.exists(dst):
            print("removing existing file", dst)
            os.remove(dst)

        if isinstance(ifs, str):
            # we got a direct path
            try:
                os.link(ifs, dst)
                return
            except Exception:
                # couldn't link file, normal on non-unix systems and also
                # if the files are on different file systems
                pass
            shutil.copyfile(ifs, dst)
        else:
            dst_partial = dst + ".partial"
            with open(dst_partial, "wb") as ofs:
                # ifs_sha1 = hashlib.sha1()
                while True:
                    # noinspection PyUnresolvedReferences
                    data = ifs.read()
                    if not data:
                        break
                    # ifs_sha1.update(data)
                    ofs.write(data)
            print("rename file from", dst_partial, "to", dst)
            os.rename(dst_partial, dst)

    def download_game_file_archive(self, url):
        print("\ndownload_game_file_archive", url)
        archive_path = Downloader.cache_file_from_url(url)
        archive = Archive(archive_path)
        archive_files = archive.list_files()
        print(archive_files)
        for name in archive_files:
            print(name)
            ifs = archive.open(name)
            data = ifs.read()
            Downloader.cache_data(data)
        if len(archive_files) == 0:
            # might not be an archive then
            with open(archive_path, "rb") as f:
                data = f.read()
            Downloader.cache_data(data)
        # the downloaded archive is no longer needed, now that we have
        # extracted all the files
        os.remove(archive_path)
        print("\n")


class FSGameSystemContext(object):
    def __init__(self):
        self._amiga = None
        self._config = None
        self._settings = None
        self._signal = None
        self._netplay = None
        self._game = None
        self._plugins = None
        # self._variant = None
        self.file = FileContext(self)
        self.thread_local = threading.local()

    @property
    def amiga(self):
        if self._amiga is None:
            from .amiga.amigacontext import AmigaContext

            self._amiga = AmigaContext(self)
        return self._amiga

    @property
    def config(self):
        if self._config is None:
            from .Config import Config

            self._config = Config(self)
        return self._config

    @property
    def settings(self):
        if self._settings is None:
            from fsbc.settings import Settings

            self._settings = Settings.instance()
        return self._settings

    @property
    def game(self):
        if self._game is None:
            self._game = GameContext(self)
        return self._game

    @property
    def plugins(self):
        if self._plugins is None:
            self._plugins = PluginsContext(self)
        return self._plugins

    # @property
    # def variant(self):
    #     if self._variant is None:
    #         self._variant = VariantContext(self)
    #     return self._variant

    @property
    def signal(self):
        if self._signal is None:
            from .SignalContext import SignalContext

            self._signal = SignalContext(self)
            # self._signal = Signal()
        return self._signal

    @property
    def netplay(self):
        if self._netplay is None:
            from .netplay.NetplayContext import NetplayContext

            self._netplay = NetplayContext(self)
        return self._netplay

    def database(self):
        return Database.instance()

    def get_game_database(self):
        return self.game_database("Amiga")

    def game_database(self, database_name):
        attr_name = "game_database_" + database_name.replace("/", "_")
        if not hasattr(self.thread_local, attr_name):
            # FIXME
            from fsgs.FSGSDirectories import FSGSDirectories

            # FIXME
            # path = os.path.join(
            #     FSGSDirectories.get_cache_dir(), "openretro.org")
            path = os.path.join(
                FSGSDirectories.databases_dir(), database_name + ".sqlite"
            )
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            # path = os.path.join(path, short_platform_id + ".sqlite")
            database = GameDatabase(path)
            setattr(self.thread_local, attr_name, database)
        return getattr(self.thread_local, attr_name)

    @property
    def cache_dir(self):
        # FIXME: remove dependency
        from fsgs.FSGSDirectories import FSGSDirectories

        return FSGSDirectories.get_cache_dir()

    # def temp_dir(self, suffix):
    #     return TemporaryDirectory(suffix)

    # def temp_file(self, suffix):
    #     return TemporaryFile(suffix)

    def load_game_by_uuid(self, game_uuid):
        if self.load_game_variant(game_uuid):
            return True
        variant_uuid = self.find_preferred_game_variant(game_uuid)
        return self.load_game_variant(variant_uuid)

    # noinspection PyMethodMayBeStatic
    def find_preferred_game_variant(self, game_uuid):
        print("find_preferred_game_variant game_uuid =", game_uuid)
        return self.get_ordered_game_variants(game_uuid)[0]["uuid"]

    # noinspection PyMethodMayBeStatic
    def get_ordered_game_variants(self, game_uuid):
        print("get_ordered_game_variants game_uuid =", game_uuid)
        from .Database import Database

        database = Database.instance()
        variants = database.find_game_variants_new(game_uuid=game_uuid)
        print(variants)
        # ordered_list = []
        # FIXME: Merge code with VariantsBrowser.py
        sortable_items = []
        for i, variant in enumerate(variants):
            game_database = self.game_database(variant["database"])
            variant["like_rating"], variant[
                "work_rating"
            ] = game_database.get_ratings_for_game(variant["uuid"])
            variant[
                "personal_rating"
            ], ignored = database.get_ratings_for_game(variant["uuid"])
            # variant_uuid = variant["uuid"]

            name = variant["name"]
            # FIXME: name replacement needed any more?
            name = name.replace("\n", " (")
            name = name.replace(" \u00b7 ", ", ")
            name += ")"

            if variant["published"] == 0:
                primary_sort = 1
                variant["name"] = "[UNPUBLISHED] " + variant["name"]
            else:
                primary_sort = 0
            sort_key = (
                primary_sort,
                1000000 - variant["like_rating"],
                1000000 - variant["work_rating"],
                name,
            )
            sortable_items.append((sort_key, i, variant))
        ordered_list = [x[2] for x in sorted(sortable_items)]
        print("ordered variant list:")
        for variant in ordered_list:
            print("-", variant["name"])
        # item.configurations = [x[1] for x in ordered_list]
        select_index = None
        if select_index is None:
            # default index selection
            for i, variant in enumerate(ordered_list):
                if variant["personal_rating"] == 5:
                    select_index = i
                    break
            else:
                for i, variant in enumerate(ordered_list):
                    if variant["have"] >= 3:
                        select_index = i
                        break
                else:
                    for i, variant in enumerate(ordered_list):
                        if variant["have"] >= 1:
                            select_index = i
                            break
                    else:
                        if len(ordered_list) > 0:
                            select_index = 0
        # return ordered_list[select_index]["uuid"]
        if select_index and select_index > 0:
            ordered_list.insert(0, ordered_list.pop(select_index))
        return ordered_list

    def load_game_variant(self, variant_uuid):
        # game_database = fsgs.get_game_database()
        # values = game_database.get_game_values_for_uuid(variant_uuid)

        from .Database import Database

        database = Database.instance()
        try:
            database_name = database.find_game_database_for_game_variant(
                variant_uuid
            )
        except LookupError:
            return False

        try:
            values = self.game.set_from_variant_uuid(
                database_name, variant_uuid
            )
        except KeyError:
            # It is possible that the variant is found without game entry,
            # which raises a KeyError.
            return False
        if not values:
            return False

        # print("")
        # for key in sorted(values.keys()):
        #     print(" * {0} = {1}".format(key, values[key]))
        # print("")

        from fsgs.platform import PlatformHandler

        platform_handler = PlatformHandler.create(self.game.platform.id)
        loader = platform_handler.get_loader(self)
        self.config.load(loader.load_values(values))
        return True

    def run_game(self):
        from fsgs.platform import PlatformHandler

        platform_handler = PlatformHandler.create(self.game.platform.id)
        runner = platform_handler.get_runner(self)

        from fsgs.input.enumeratehelper import EnumerateHelper

        device_helper = EnumerateHelper()
        device_helper.default_port_selection(runner.ports, runner.options)

        runner.prepare()
        process = runner.run()
        process.wait()
        runner.finish()


# class TemporaryDirectory(object):
#
#     def __init__(self, suffix):
#         self.path = tempfile.mkdtemp(suffix="-fsgs-" + suffix)
#
#     def __del__(self):
#         self.delete()
#
#     def delete(self):
#         if os.environ.get("FSGS_CLEANUP", "") == "0":
#             print("NOTICE: keeping temp files around...")
#             return
#         if self.path:
#             shutil.rmtree(self.path)
#             self.path = ""


# class TemporaryFile(object):
#
#     def __init__(self, suffix):
#         # self.path = tempfile.mkstemp(suffix=suffix)
#         self.dir_path = tempfile.mkdtemp(suffix="-fsgs-" + suffix)
#         self.path = os.path.join(self.dir_path, suffix)
#
#     def __del__(self):
#         self.delete()
#
#     def delete(self):
#         if os.environ.get("FSGS_CLEANUP", "") == "0":
#             print("NOTICE: keeping temp files around...")
#             return
#         if self.path:
#             os.unlink(self.path)
#             self.path = ""
#         if self.dir_path:
#             shutil.rmtree(self.dir_path)
#             self.dir_path = ""


class GameContext(object):
    def __init__(self, context):
        self._context = weakref.ref(context)
        # FIXME: REMOVE? use config[game_name] instead?
        self.name = ""
        # FIXME: REMOVE? use config[game_uuid] instead?
        self.uuid = ""
        self.variant = VariantContext()
        self.platform = GamePlatform()

    @property
    def fsgs(self):
        return self._context()

    def get_game_values_for_id(self, game_database, id):
        doc = game_database.get_game_values(id)
        return self._fix_with_game_values_from_parent_database(doc)

    def get_game_values_for_uuid(self, game_database, uuid):
        doc = game_database.get_game_values_for_uuid(uuid)
        return self._fix_with_game_values_from_parent_database(doc)

    def _fix_with_game_values_from_parent_database(self, doc):
        parent_database_name = doc.get("parent_database", "")
        if parent_database_name:
            parent_database = self.fsgs.game_database(parent_database_name)
            try:
                parent_doc = parent_database.get_game_values(
                    game_uuid=doc.get("parent_uuid", "")
                )
            except LookupError:
                raise IncompleteGameException(
                    "Could not find parent {0} of game {1}".format(
                        doc.get("parent_uuid", ""), doc.get("game_uuid")
                    )
                )
            parent_doc.update(doc)
            doc = parent_doc
        return doc

    def set_from_variant_uuid(self, database_name, variant_uuid):
        print("set_from_variant_uuid", database_name, variant_uuid)
        game_database = self.fsgs.game_database(database_name)
        doc = self.get_game_values_for_uuid(game_database, variant_uuid)

        if not doc.get("_type", "") == "2":
            return {}
        print("")
        for key in sorted(doc.keys()):
            print(" * {0} = {1}".format(key, doc[key]))
        print("")

        platform_id = doc["platform"]
        self.platform.id = platform_id

        self.uuid = doc["game_uuid"]
        self.name = doc["game_name"]
        self.variant.uuid = variant_uuid
        self.variant.name = doc["variant_name"]
        return doc


class PluginsContext(object):
    def __init__(self, context):
        self._context = weakref.ref(context)

    def find_resource(self, name):
        return PluginManager.instance().find_resource(name)

    def find_executable(self, name):
        return PluginManager.instance().find_executable(name)


class GamePlatform(object):
    def __init__(self):
        self._id = ""

    def get_id(self):
        return self._id

    def set_id(self, id):
        self._id = id.lower()

    id = property(get_id, set_id)

    @property
    def name(self):
        from .platform import PlatformHandler

        return PlatformHandler.get_platform_name(self._id)
        # if self._id == "atari-7800":
        #     return "Atari 7800"
        # if self._id == "amiga":
        #     return "Amiga"
        # if self._id == "cdtv":
        #     return "CDTV"
        # if self._id == "cd32":
        #     return "CD32"
        # raise Exception("Unrecognized platform ({0})".format(self._id))


class VariantContext(object):
    def __init__(self):
        self.name = ""
        self.uuid = ""

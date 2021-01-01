import os

from fsbc.util import is_uuid
from fsgs.directories import saves_directory
from fsgs.options.constants2 import CONFIG_NAME__, VARIANT_UUID__


def save_dir_for_config(config, *, saves_dir=None):
    if saves_dir is None:
        saves_dir = saves_directory()
    variant_uuid = config.get(VARIANT_UUID__, "")
    if variant_uuid:
        return save_dir_for_variant_uuid(variant_uuid, saves_dir=saves_dir)
    config_name = config.get(CONFIG_NAME__, "")
    save_dir_for_config_name(config_name, saves_dir=saves_dir)


def find_existing_save_dir_for_config(config):
    # FIXME:
    raise NotImplementedError()


def move_save_dir(old_save_dir, new_save_dir):
    assert os.path.exists(old_save_dir)
    assert not os.path.exists(new_save_dir)
    # FIXME: Move directory
    # FIXME: Update save database? (Maybe external to this function)
    # FIXME: Remove empty old intermediate directories?
    raise NotImplementedError()


_ALPHANUM = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHANUM = set(_ALPHANUM)
ALLOWED_CHARS = set(_ALPHANUM + "._-()[]")


def save_dir_name_from_config_name(config_name):
    name = "".join([(x if x in ALLOWED_CHARS else "_") for x in config_name])
    # Directory names are not allowed to end with space and Windows.
    if name and name[-1] == ".":
        name = name[:-1]
    return name


def save_dir_for_config_name(config_name, *, saves_dir):
    assert config_name
    save_dir_name = save_dir_name_from_config_name(config_name)
    assert save_dir_name
    letter_dir = "_"
    # for letter in save_dir_name:
    if True:
        letter = save_dir_name[0]
        if letter in ALPHANUM:
            letter_dir = letter.upper()
            # break
    save_dir = os.path.join(saves_dir, letter_dir, save_dir_name)
    return save_dir


def save_dir_for_variant_uuid(variant_uuid, *, saves_dir):
    saves_dir = saves_directory()
    assert is_uuid(variant_uuid)
    save_dir = os.path.join(
        saves_dir, variant_uuid[0], variant_uuid[1:3], variant_uuid
    )
    return save_dir

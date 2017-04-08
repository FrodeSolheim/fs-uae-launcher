from collections import namedtuple
from fsgs.platforms import PLATFORM_AMIGA

KnownFile = namedtuple("KnownFile", ["sha1", "platform", "name"])
KnownFileMod = namedtuple("KnownFileMod", ["sha1", "mod"])

ACTION_REPLAY_MK_II_2_14_ROM = KnownFile(
    "255d6df63a4eab0a838eb1a16a267b0959dff634", PLATFORM_AMIGA,
    "Action Replay Mk II v2.14.rom")
ACTION_REPLAY_MK_II_2_14_MOD_ROM = KnownFile(
    "14b1f5a69efb6f4e2331970e6ca0f33c0f04ac91", PLATFORM_AMIGA,
    "Action Replay Mk II v2.14 (Mod).rom")
# noinspection SpellCheckingInspection
ACTION_REPLAY_MK_III_3_17_ROM = KnownFile(
    "5d4987c2e3ffea8b1b02e31430ef190f2db76542", PLATFORM_AMIGA,
    "Action Replay Mk III v3.17.rom")
ACTION_REPLAY_MK_III_3_17_MOD_ROM = KnownFile(
    "0439d6ccc2a0e5c2e83fcf2389dc4d4a440a4c62", PLATFORM_AMIGA,
    "Action Replay Mk III v3.17 (Mod).rom")

# known_files = [
#     ACTION_REPLAY_MK_III_3_17_ROM
# ]

# noinspection SpellCheckingInspection
# known_file_mods = {
#     ACTION_REPLAY_MK_III_3_17_MOD_ROM.sha1: KnownFileMod(
#         ACTION_REPLAY_MK_III_3_17_ROM.sha1, "zero-initial-4-bytes"),
# }

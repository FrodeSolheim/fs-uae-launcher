from fsgamesys.FSGameSystemContext import FSGameSystemContext
from fsgamesys.gamedb.constants import DATABASE_AMIGA


def game_database_dumper_main():
    fsgs = FSGameSystemContext()
    game_database = fsgs.game_database(DATABASE_AMIGA)
    # cursor = game_database.cursor()
    # cursor.execute("")
    for uuid in game_database.get_all_uuids():
        values = game_database.get_game_values_for_uuid(uuid, recursive=False)
        for key in sorted(values.keys()):
            print("{} = {}".format(key, values[key]))

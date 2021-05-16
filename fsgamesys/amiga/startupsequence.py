from typing import List


def prepare_startup_sequence(command: str, *, setpatch: bool = False) -> bytes:
    # FIXME: semi-colon is used in WHDLoad CONFIG options...
    command = "\n".join([x.strip() for x in command.split(";")])
    # startup_sequence = os.path.join(s_dir, "Startup-Sequence")
    data: List[bytes] = []
    if True:
        # if not os.path.exists(startup_sequence):
        # with open(startup_sequence, "wb") as f:

        # FIXME: setpatch...
        # if setpatch is not None:
        #     if setpatch:
        #         data.append(
        #             setpatch_found_sequence.replace("\r\n", "\n").encode(
        #                 "ISO-8859-1"
        #             )
        #         )
        #     else:
        #         data.append(
        #             setpatch_not_found_sequence.replace("\r\n", "\n").encode(
        #                 "ISO-8859-1"
        #             )
        #         )
        data.append(
            setpatch_sequence.replace("\r\n", "\n").encode("ISO-8859-1")
        )
        data.append(command.replace("\r\n", "\n").encode("ISO-8859-1"))

    # The User-Startup file is useful if the user has provided a base WHDLoad
    # directory with an existing startup-sequence
    # user_startup = os.path.join(s_dir, "User-Startup")
    # with open(user_startup, "ab") as f:
    #     data.append.write(command.replace("\r\n", "\n").encode("ISO-8859-1"))
    return b"".join(data)


setpatch_found_sequence = """\
C:SetPatch >NIL:
"""

setpatch_not_found_sequence = """\
echo ""
echo "WARNING: SetPatch v39.6 not found - THE GAME MIGHT FAIL!"
echo "(The Launcher can install this file from a scanned Workbench 3.0 disk)"
"""

# "Make sure a WB 3.0 "
# echo "disk is scanned in FS-UAE Launcher"
# echo "and the file will automatically be copied from the disk."

setpatch_sequence = f"""\
If Exists C:SetPatch
{setpatch_found_sequence}
Else
{setpatch_not_found_sequence}
Endif
"""

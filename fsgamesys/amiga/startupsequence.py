import os


def prepare_startup_sequence(command, *, setpatch=None) -> bytes:
    # FIXME: semi-colon is used in WHDLoad CONFIG options...
    command = "\n".join([x.strip() for x in command.split(";")])
    # startup_sequence = os.path.join(s_dir, "Startup-Sequence")
    data = []
    if True:
        # if not os.path.exists(startup_sequence):
        # with open(startup_sequence, "wb") as f:

        # FIXME: setpatch...
        if setpatch is not None:
            if setpatch:
                data.append(
                    setpatch_found_sequence.replace("\r\n", "\n").encode(
                        "ISO-8859-1"
                    )
                )
            else:
                data.append(
                    setpatch_not_found_sequence.replace("\r\n", "\n").encode(
                        "ISO-8859-1"
                    )
                )
        data.append(command.replace("\r\n", "\n").encode("ISO-8859-1"))

    # The User-Startup file is useful if the user has provided a base WHDLoad
    # directory with an existing startup-sequence
    # user_startup = os.path.join(s_dir, "User-Startup")
    # with open(user_startup, "ab") as f:
    #     data.append.write(command.replace("\r\n", "\n").encode("ISO-8859-1"))
    return b"".join(data)


setpatch_found_sequence = """
C:SetPatch
"""

setpatch_not_found_sequence = """
echo "Warning: SetPatch (39.6) not found."
echo "Make sure a WB 3.0 disk is scanned in FS-UAE Launcher"
echo "and the file will automatically be copied from the disk."
EndIF
"""

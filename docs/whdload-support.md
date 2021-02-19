# WHDLoad support

[WHDLoad](http://whdload.de/) is a sofware solution used to (primarily)
allow floppy-based games to be installed to an Amiga hard drive and run
from Workbench. Custom WHDLoad "slaves" are written for each game, which
patches the game to work on modern HD-based Amigas.

Since WHDLoad is a pure Amiga-side program, it will, like any other Amiga
software, run just fine in the emulated Amiga environment provided by FS-UAE.
See the official WHLoad documentation for information about how to use WHDLoad
in the classical sense.

This document describes how FS-UAE Launcher supports using WHDLoad to
make it easy and convient to launch individual WHDLoad-based games. These
convenience features are provided by **FS-UAE Launcher** (and Arcade), not
FS-UAE itself.

## WHDLoad game archives

A WHDLoad game archive is an archive (`.zip` or `.lha`) containing a single
WHDLoad-installed game.

Please note that the archives available from [whdload.de](http://whdload.de/)
are _installers_, not game archives. In order to create a game archive you
run to run the WHDLoad installer for a game, and then create a `.zip` or
`.lha` archive containing the destination directory where you installed the
game.

## Loading a WHDLoad game archive

In FS-UAE Launcher, if you insert a `.zip` or `.lha` file into the primary
hard drive slot, the Launcher will check if the archive is a WHDLoad game
archive. If it is, it will try to extract WHDLoad arguments from the archive
and automatically set some options suitable for running the game (A1200
model, 8 MB fast RAM).

## WHDLoad variants in the game database

The online game database contains information about (most) available
WHDLoad games. In order for these to appear in FS-UAE Launcher, you need
to have the game files on your computer, and indexed by the file scanner
in the Launcher.

**Note:** The individual game files needed for a particular WHDLoad game
install do not have to be contained one and the same archive. Also, the name
of the archive(s) containing the files do not matter. The Launcher will find
each individual required file based on checksums, and create a temporary
HD suitable for running the game. Any custom configuration needed for the
game will be retrieved from the game database.

## Running a WHDLoad game archive directly

You can run fs-uae-launcher with the path to a WHDLoad game archive.
The Launcher will then try to automatically create a config suited to run
the game, and start it.

2.9.4dev+: If you are using the online game database, FS-UAE Launcher will
try to match the archive with a variant from the game database, and use the
configuration from the database. If you want to prevent this, you can add the
`--no-auto-detect-game` parameter.

You can disable the progress dialog opened by FS-UAE Launcher by including
the `--no-gui` parameter.

FIXME: Write about launching games using game / variant UUIDs.

## Automatic hard drive creation

The Launcher will when you launch a WHDLoad game automatically assemble a 
bootable hard drive, install the `WHDLoad` executable itself along with
support files, the game files, and a Startup-Sequence auto-booting into the
game. But it also needs some files which you must provide:

- SetPatch
- Kickstarts

## SetPatch

In order to make all WHDLoad games work reliably, the `SetPatch` program must
be installed onto this hard drive. The Launcher will try to find a specific
version of SetPatch (SHA-1: `4d4aae988310b07726329e436b2250c0f769ddff`) to
make sure that all users of the online game database has the exact same
experience, and also to make these games compatible with net play.

It will try to lookup this file in the Launcher file database directly, or if
not found, it will try to find it in one of the following ADF files:

SHA-1: `08c4afde7a67e6aaee1f07af96e95e9bed897947`, known as:
- Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
  (Disk 2 of 6)(Workbench)[m4].adf

SHA-1: `0e7f30223af254df0e2b91ea409f35c56d6164a6`, known as:
- Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
  (Disk 2 of 6)(Workbench)[m3].adf

SHA-1: `4f4770caae5950eca4a2720e0424df052ced6a32`, known as:
- Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
  (Disk 2 of 6)(Workbench)[m5].adf

SHA-1: `53086c3e44ec2d34e60ab65af71fb11941f4e0af`, known as:
- Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
  (Disk 2 of 6)(Workbench)[m].adf

SHA-1: `65ab988e597b456ac40320f88a502fc016d590aa`, known as:
- Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
  (Disk 2 of 6)(Workbench)[a].adf

SHA-1: `9496daa66e6b2f4ddde4fa2580bb3983a25e3cd2`, known as:
- Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
  (Disk 2 of 6)(Workbench)[m bamcopy].adf

SHA-1: `cf2f24cf5f5065479476a38ec8f1016b1f746884`, known as:
- Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
  (Disk 2 of 6)(Workbench)[m2].adf

SHA-1: `e663c92a9c88fa38d02bbb299bea8ce70c56b417`, known as:
- Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
  (Disk 2 of 6)(Workbench)[!].adf

If you do not have any of these disks, a compatible disk can be found in
Amiga Forever (at least the Plus edition).

## Kickstarts

Many WHDLoad games needs kickstart ROM images installed on the hard drive.
The WHDLoad support in FS-UAE Launcher does not know which kickstart a
specific game requires, so it installs all of them. The following kickstart
ROM images must be present in your file database:

SHA-1: `11f9e62cf299f72184835b7b2a70a16333fc0d88`, known as:
- Kickstart v1.2 r33.180 (1986-10)(Commodore)(A500-A1000-A2000)[!].rom
- kick33180.A500

SHA-1: `891e9a547772fe0c6c19b610baf8bc4ea7fcb785`, known as:
- Kickstart v1.3 r34.005 (1987-12)(Commodore)(A500-A1000-A2000-CDTV)[!].rom
- kick34005.A500

SHA-1: `e21545723fe8374e91342617604f1b3d703094f1`, known as:
- Kickstart v3.1 r40.068 (1993-12)(Commodore)(A1200)[!].rom
- kick40068.A1200

SHA-1: `5fe04842d04a489720f0f4bb0e46948199406f49`, known as:
- Kickstart v3.1 r40.068 (1993-12)(Commodore)(A4000)[!].rom
- kick40068.A4000

If you do not have these kickstart ROM files, then you get these as part of
Amiga Forever (at least the Plus edition).

## Saving games

- WHDLoad quit key
- State dir name
- Unsafe save states

## Related options

- [whdload_quit_key](options/whdload-quit-key.md)
- [whdload_preload](options/whdload-preload.md)
- [whdload_splash_delay](options/whdload-splash-delay.md)
- [x_whdload_args](options/x_whdload-args.md)
- [x_whdload_version](options/x_whdload-version.md)

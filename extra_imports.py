# this is a quick hack tp fix problems with some modules not being imported
# by py2exe / py2app otherwise

import fs_uae_workspace.apps.adf_creator_app
import fs_uae_workspace.apps.clock_app
import fs_uae_workspace.apps.hdf_creator_app
import fs_uae_workspace.apps.joystick_config_app
import fs_uae_workspace.apps.launcher_app
import fs_uae_workspace.apps.locker_uploader
import fs_uae_workspace.apps.login
import fs_uae_workspace.apps.logout
import fs_uae_workspace.apps.refresh

import fs_uae_workspace.prefs.audio
import fs_uae_workspace.prefs.experimental_features
import fs_uae_workspace.prefs.filter
import fs_uae_workspace.prefs.game_database
import fs_uae_workspace.prefs.joystick
import fs_uae_workspace.prefs.keyboard
import fs_uae_workspace.prefs.language
import fs_uae_workspace.prefs.mouse
import fs_uae_workspace.prefs.netplay
# import fs_uae_workspace.prefs.opengl
import fs_uae_workspace.prefs.scan
import fs_uae_workspace.prefs.video

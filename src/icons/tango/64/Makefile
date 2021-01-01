data = ../../../../data
glowicon = ../../glowicon.sh

icons = ${data}/Icons
system = ${icons}/System
prefs = ${system}/Prefs
tools = ${system}/Tools
utilities = ${system}/Utilities

all: tools
	mkdir -p ${icons}

	${glowicon} --base ${icons}/AmigaForever.png \
		drive-harddisk-4.svg \
		../../amigaforever/volumeoverlays/AmigaForever.png
	${glowicon} --glow ${icons}/AmigaForever_Selected.png \
		drive-harddisk-4.svg \
		../../amigaforever/volumeoverlays/AmigaForever.png

	${glowicon} --base ${icons}/Data.png \
		drive-harddisk-4.svg
	${glowicon} --glow ${icons}/Data_Selected.png \
		drive-harddisk-4.svg

	${glowicon} --base ${icons}/Games.png \
		drive-harddisk-4.svg \
		../../gnome/volume-overlays/applications-games.png
	${glowicon} --glow ${icons}/Games_Selected.png \
		drive-harddisk-4.svg \
		../../gnome/volume-overlays/applications-games.png

	${glowicon} --base ${icons}/Media.png \
		drive-harddisk-4.svg
	${glowicon} --glow ${icons}/Media_Selected.png \
		drive-harddisk-4.svg

	# ${glowicon} --base ${icons}/"Ram Disk".png \
	# 	drive-harddisk-4.svg
	# ${glowicon} --glow ${icons}/"Ram Disk"_Selected.png \
	# 	drive-harddisk-4.svg

	${glowicon} --base ${icons}/Software.png \
		drive-harddisk-4.svg
	${glowicon} --glow ${icons}/Software_Selected.png \
		drive-harddisk-4.svg

	${glowicon} --base ${prefs}/Storage.png \
		drive-harddisk-4.svg \
		../../humanity/64/prefs-overlay.png
	${glowicon} --glow ${prefs}/Storage_Selected.png \
		drive-harddisk-4.svg \
		../../humanity/64/prefs-overlay.png

	${glowicon} --base ${icons}/System.png \
		drive-harddisk-4.svg ../../overlays/fs-uae-volume.png
	${glowicon} --glow ${icons}/System_Selected.png \
		drive-harddisk-4.svg ../../overlays/fs-uae-volume.png

	${glowicon} --base ${icons}/WHDLoad.png \
		drive-harddisk-4.svg
	${glowicon} --glow ${icons}/WHDLoad_Selected.png \
		drive-harddisk-4.svg

	${glowicon} --base ${icons}/Work.png \
		drive-harddisk-4.svg
	${glowicon} --glow ${icons}/Work_Selected.png \
		drive-harddisk-4.svg

	# ${glowicon} --base ${system}/Tools.png \
	# 	drive-harddisk-4.svg
	# ${glowicon} --glow ${system}/Tools_Selected.png \
	# 	drive-harddisk-4.svg


tools:
	mkdir -p ${tools}

	${glowicon} --base ${tools}/FileScanner.png \
		drive-harddisk-4.svg ../overlays/system-search.png
	${glowicon} --glow ${tools}/FileScanner_Selected.png \
		drive-harddisk-4.svg ../overlays/system-search.png

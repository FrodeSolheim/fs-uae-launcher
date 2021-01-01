data = ../../data
glowicon = ./glowicon.sh

icons = ${data}/Icons
system = ${icons}/System
prefs = ${system}/Prefs
platforms = ${system}/Prefs/Platforms
tools = ${system}/Tools
utilities = ${system}/Utilities

all: icons utilities
	make -C 64
	make -C fontawesome
	make -C humanity
	make -C tango

	cp TitleBarClose.svg ${icons}/
	cp TitleBarMaximize.svg ${icons}/
	cp TitleBarMenu.svg ${icons}/
	cp TitleBarMinimize.svg ${icons}/

${icons}:
	mkdir -p ${icons}

icons: ${icons}/Shared.png ${icons}/Shared_Selected.png

${icons}/Shared.png: ${icons} \
		tango/64/drive-harddisk-4.svg \
		shared/tango-software-update-available.png
	${glowicon} --base ${icons}/Shared.png \
		tango/64/drive-harddisk-4.svg \
		shared/tango-software-update-available.png

${icons}/Shared_Selected.png: ${icons} \
		tango/64/drive-harddisk-4.svg \
		shared/tango-software-update-available.png
	${glowicon} --glow ${icons}/Shared_Selected.png \
		tango/64/drive-harddisk-4.svg \
		shared/tango-software-update-available.png


utilities: ${utilities}/Checksum.png ${utilities}/Checksum_Selected.png

${utilities}:
	mkdir -p ${utilities}

${utilities}/Checksum.png: ${utilities} \
		system/utilities/checksum/humanity-multipart-encrypted.svg \
		system/utilities/checksum/tango-application-certificate.png
	${glowicon} --base ${utilities}/Checksum.png \
		system/utilities/checksum/humanity-multipart-encrypted.svg \
		system/utilities/checksum/tango-application-certificate.png

${utilities}/Checksum_Selected.png: ${utilities} \
		system/utilities/checksum/humanity-multipart-encrypted.svg \
		system/utilities/checksum/tango-application-certificate.png
	${glowicon} --glow ${utilities}/Checksum_Selected.png \
		system/utilities/checksum/humanity-multipart-encrypted.svg \
		system/utilities/checksum/tango-application-certificate.png

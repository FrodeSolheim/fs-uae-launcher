version = $(strip $(shell cat ../../VERSION))
arch = $(strip $(shell python3 ../arch.py))

emulator_dir = fs-uae_$(version)_windows_$(arch)
launcher_dir = fs-uae-launcher_$(version)_windows_$(arch)

all: progdir zipfile setup

clean:
	rm -Rf fs-uae-launcher-*_windows*
	rm -Rf fs-uae-launcher_*_windows*

progdir:
	rm -Rf $(launcher_dir)

	make -C ../..

	rm -Rf ../build
	# ../dist
	cd ../.. && python3 setup.py build_exe
	mv ../../build/exe.mingw-3.4 $(launcher_dir)

	rm -f $(launcher_dir)/imageformats/qgif*.dll
	rm -f $(launcher_dir)/imageformats/qmng*.dll
	rm -f $(launcher_dir)/imageformats/qsvg*.dll
	rm -f $(launcher_dir)/imageformats/qtga*.dll
	rm -f $(launcher_dir)/imageformats/qtiff*.dll
	rm -f $(launcher_dir)/imageformats/*d.dll
	rm -f $(launcher_dir)/imageformats/*d4.dll
	rm -f $(launcher_dir)/platforms/qminimal*.dll
	rm -f $(launcher_dir)/platforms/*d.dll

	python3 clib.py libjpeg-8.dll $(launcher_dir)

	cp -a ../../share $(launcher_dir)

	# mkdir -p $(launcher_dir)/share/fs-uae-launcher/fs_uae_launcher
	# cp -pPR ../../fs_uae_launcher/res $(launcher_dir)/share/fs-uae-launcher/fs_uae_launcher/
	# cp -pPR ../../fs_uae_launcher/data $(launcher_dir)/share/fs-uae-launcher/fs_uae_launcher/
	# mkdir -p $(launcher_dir)/share/fs-uae-launcher/fs_uae_workspace
	# cp -pPR ../../fs_uae_workspace/data $(launcher_dir)/share/fs-uae-launcher/fs_uae_workspace/

	python3 sign.py $(launcher_dir)/fs-uae-launcher.exe

	#cp -a /c/Microsoft.VC90.CRT $(launcher_dir)/
	#cp -a /c/msvcr100.dll $(launcher_dir)/
	#cp -a /c/msvcp100.dll $(launcher_dir)/
	# cp -a /c/Python33/Lib/site-packages/PyQt5/libEGL.dll $(launcher_dir)/
	# cp -a /c/Python33/Lib/site-packages/PyQt5/Qt5Svg.dll $(launcher_dir)/
	# cp -a /c/Python33/Lib/site-packages/PyQt4/QtSvg4.dll $(launcher_dir)/
	# cp -a /c/Python33/Lib/site-packages/PyQt4/QtXml4.dll $(launcher_dir)/
	# cp -a /c/Python33/DLLs/python3.dll $(launcher_dir)/
	# cp -a $(emulator_dir) $(launcher_dir)/FS-UAE

zipfile:
	cd $(launcher_dir) && zip -9 -r ../../../$(launcher_dir).zip *

setup:
	sed s/9.8.7/${version}/g fs-uae-launcher.iss > fs-uae-launcher.iss2.tmp
	sed s/ARCH/${arch}/g fs-uae-launcher.iss2.tmp > fs-uae-launcher.iss.tmp
	python3 iscc.py fs-uae-launcher.iss.tmp
	python3 sign.py ../fs-uae-launcher_$(version)_windows_$(arch).exe
	rm fs-uae-launcher.iss.tmp

version = $(strip $(shell cat ../VERSION))
emulator_dir = fs-uae_$(version)_windows
launcher_dir = fs-uae-launcher_$(version)_windows

all: progdir zipfile setup

clean:
	rm -Rf fs-uae-launcher-*_windows*
	rm -Rf fs-uae-launcher_*_windows*

progdir:
	rm -Rf $(launcher_dir)

	make -C ..

	rm -Rf ../build ../dist
	cd .. && python3 setup.py build_exe
	mv ../build/exe.win32-3.3 $(launcher_dir)

	cp -a ../share $(launcher_dir)
	# mkdir -p $(launcher_dir)/share/fs-uae-launcher/fs_uae_launcher
	# cp -pPR ../fs_uae_launcher/res $(launcher_dir)/share/fs-uae-launcher/fs_uae_launcher/
	# cp -pPR ../fs_uae_launcher/data $(launcher_dir)/share/fs-uae-launcher/fs_uae_launcher/
	# mkdir -p $(launcher_dir)/share/fs-uae-launcher/fs_uae_workspace
	# cp -pPR ../fs_uae_workspace/data $(launcher_dir)/share/fs-uae-launcher/fs_uae_workspace/

	python replace-icon.py $(launcher_dir)/fs-uae-launcher.exe ../icon/fs-uae-launcher.ico
	python /c/signtool.py $(launcher_dir)/fs-uae-launcher.exe
	#cp -a /c/Microsoft.VC90.CRT $(launcher_dir)/
	cp -a /c/msvcr100.dll $(launcher_dir)/
	cp -a /c/msvcp100.dll $(launcher_dir)/
	# cp -a /c/Python33/Lib/site-packages/PyQt5/libEGL.dll $(launcher_dir)/
	# cp -a /c/Python33/Lib/site-packages/PyQt5/Qt5Svg.dll $(launcher_dir)/
	cp -a /c/Python33/Lib/site-packages/PyQt4/QtSvg4.dll $(launcher_dir)/
	cp -a /c/Python33/Lib/site-packages/PyQt4/QtXml4.dll $(launcher_dir)/
	cp -a /c/Python33/DLLs/python3.dll $(launcher_dir)/
	# cp -a $(emulator_dir) $(launcher_dir)/FS-UAE

zipfile:
	cd $(launcher_dir) && zip -9 -r ../../$(launcher_dir).zip *

setup:
	sed s/9.8.7/${version}/g fs-uae-launcher.iss > fs-uae-launcher.iss.tmp
	iscc fs-uae-launcher.iss.tmp
	python /c/signtool.py ../fs-uae-launcher_$(version)_windows.exe
	rm fs-uae-launcher.iss.tmp

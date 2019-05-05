version = $(strip $(shell cat ../../VERSION))
library_zip = $(launcher_dir)/library.zip
python_dir = $$LOCALAPPDATA/Programs/Python/Python36
python = $(python_dir)/python.exe
qt_dir = $(python_dir)/Lib/site-packages/PyQt5/Qt
arch = $(strip $(shell $(python) ../arch.py))
launcher_dir = Launcher/Windows/$(arch)
launcher_zip = fs-uae-launcher_$(version)_windows_$(arch).zip
launcher_txz = fs-uae-launcher_$(version)_windows_$(arch).tar.xz


all: clean progdir zip

clean:
	rm -Rf fs-uae-launcher-*_windows*
	rm -Rf fs-uae-launcher_*_windows*
	rm -Rf $(launcher_dir)
	rm -Rf Launcher
	rm -f *.tmp

progdir:
	rm -Rf Launcher

	make -C ../..
	rm -Rf ../build

	cd ../.. && PYTHONHASHSEED=1 $(python) setup.py build_exe
	mkdir -p $(launcher_dir)
	mv ../../build/exe.win-amd64-3.6/* $(launcher_dir)

	mkdir $(launcher_dir)/imageformats
	cp $(qt_dir)/plugins/imageformats/qico.dll $(launcher_dir)/imageformats
	cp $(qt_dir)/plugins/imageformats/qjpeg.dll $(launcher_dir)/imageformats
	mkdir $(launcher_dir)/platforms
	cp $(qt_dir)/plugins/platforms/qwindows.dll $(launcher_dir)/platforms

	mkdir -p Launcher/Data
	cp -a ../../share/locale Launcher/Data/Locale
	cp ../../requests/cacert.pem Launcher/Data
	rm -Rf $(launcher_dir)/share/applications
	rm -Rf $(launcher_dir)/share/icons

	rm -Rf $(launcher_dir)/amitools
	rm -Rf $(launcher_dir)/arcade
	rm -Rf $(launcher_dir)/fsbc
	rm -Rf $(launcher_dir)/fsgs
	rm -Rf $(launcher_dir)/fspy
	rm -Rf $(launcher_dir)/fstd
	rm -Rf $(launcher_dir)/fsui
	rm -Rf $(launcher_dir)/launcher
	rm -Rf $(launcher_dir)/OpenGL
	rm -Rf $(launcher_dir)/oyoyo
	rm -Rf $(launcher_dir)/workspace

	zip -d $(library_zip) amitools/\*
	zip -d $(library_zip) arcade/\*
	zip -d $(library_zip) fsbc/\*
	zip -d $(library_zip) fsgs/\*
	zip -d $(library_zip) fspy/\*
	zip -d $(library_zip) fstd/\*
	zip -d $(library_zip) fsui/\*
	zip -d $(library_zip) launcher/\*
	zip -d $(library_zip) OpenGL/\*
	zip -d $(library_zip) oyoyo/\*
	zip -d $(library_zip) workspace/\*

	# This file differs between each build
	zip -d $(library_zip) BUILD_CONSTANTS.pyc
	# Remove wrong-cased members from the archive
	zip -d $(library_zip) ConfigParser.pyc || true
	zip -d $(library_zip) Queue.pyc || true
	PYTHONPATH=../.. python3 -m fspy.zipfile deterministic \
		--fix-pyc-timestamps $(library_zip)

	make -C ../python
	mkdir -p Launcher/Python
	cp -a ../python/*.zip Launcher/Python

	echo $(ver) > Launcher/Version.txt
	echo $(ver) > $(launcher_dir)/Version.txt

	python3 sign.py $(launcher_dir)/fs-uae-launcher.exe

zip:
	# cd $(launcher_dir) && zip -9 -r ../../../$(launcher_zip) *
	zip -9 -r ../../$(launcher_zip) Launcher

tar.xz: progdir
	# cd $(launcher_dir) && tar cfvJ ../../../$(launcher_txz) *
	tar cfvJ ../../$(launcher_txz) Launcher

setup:
	sed s/9.8.7/${version}/g fs-uae-launcher.iss > fs-uae-launcher.iss2.tmp
	sed s/ARCH/${arch}/g fs-uae-launcher.iss2.tmp > fs-uae-launcher.iss.tmp
	python3 iscc.py fs-uae-launcher.iss.tmp
	python3 sign.py ../fs-uae-launcher_$(version)_windows_$(arch).exe
	rm fs-uae-launcher.iss.tmp

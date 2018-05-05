version = $(strip $(shell cat ../../VERSION))
arch = $(strip $(shell python3 ../arch.py))

emulator_dir = fs-uae_$(version)_windows_$(arch)
launcher_dir = fs-uae-launcher_$(version)_windows_$(arch)
library_zip = $(launcher_dir)/library.zip

all: progdir zip setup

clean:
	rm -Rf fs-uae-launcher-*_windows*
	rm -Rf fs-uae-launcher_*_windows*

progdir:
	rm -Rf $(launcher_dir)

	make -C ../..
	rm -Rf ../build

	cd ../.. && PYTHONHASHSEED=1 python3 setup.py build_exe
	mv ../../build/exe.mingw-3.6 $(launcher_dir)

	cp -a ../../share $(launcher_dir)
	cp ../../requests/cacert.pem $(launcher_dir)
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
	zip -d $(library_zip) ConfigParser.pyc
	zip -d $(library_zip) Queue.pyc
	PYTHONPATH=../.. python3 -m fspy.zipfile deterministic \
		--fix-pyc-timestamps $(library_zip)

	make -C ../python
	cp -a ../python/*.zip $(launcher_dir)

	python3 sign.py $(launcher_dir)/fs-uae-launcher.exe

zip:
	cd $(launcher_dir) && zip -9 -r ../../../$(launcher_dir).zip *

tar.xz: progdir
	cd $(launcher_dir) && tar cfvJ ../../../$(launcher_dir).tar.xz *

setup:
	sed s/9.8.7/${version}/g fs-uae-launcher.iss > fs-uae-launcher.iss2.tmp
	sed s/ARCH/${arch}/g fs-uae-launcher.iss2.tmp > fs-uae-launcher.iss.tmp
	python3 iscc.py fs-uae-launcher.iss.tmp
	python3 sign.py ../fs-uae-launcher_$(version)_windows_$(arch).exe
	rm fs-uae-launcher.iss.tmp

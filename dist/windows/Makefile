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
	cd ../.. && python3 setup.py build_exe
	mv ../../build/exe.mingw-3.4 $(launcher_dir)

	rm -f $(launcher_dir)/imageformats/qdds*.dll
	rm -f $(launcher_dir)/imageformats/qicns*.dll
	rm -f $(launcher_dir)/imageformats/qjp2*.dll
	rm -f $(launcher_dir)/imageformats/qmng*.dll
	rm -f $(launcher_dir)/imageformats/qsvg*.dll
	rm -f $(launcher_dir)/imageformats/qtga*.dll
	rm -f $(launcher_dir)/imageformats/qtiff*.dll
	rm -f $(launcher_dir)/imageformats/qwbmp*.dll
	rm -f $(launcher_dir)/imageformats/qwebp*.dll
	rm -f $(launcher_dir)/imageformats/*d.dll
	rm -f $(launcher_dir)/imageformats/*d4.dll
	rm -f $(launcher_dir)/platforms/qminimal*.dll
	rm -f $(launcher_dir)/platforms/*d.dll

	# mv $(launcher_dir)/imageformats/* $(launcher_dir)
	# rm -Rf $(launcher_dir)/imageformats/
	# mv $(launcher_dir)/platforms/* $(launcher_dir)
	# rm -Rf $(launcher_dir)/platforms/

	python3 clib.py libjpeg-8.dll $(launcher_dir)

	cp -a ../../share $(launcher_dir)
	cp ../../requests/cacert.pem $(launcher_dir)
	rm -Rf $(launcher_dir)/share/applications
	rm -Rf $(launcher_dir)/share/icons

	rm -Rf $(launcher_dir)/OpenGL
	rm -Rf $(launcher_dir)/arcade
	rm -Rf $(launcher_dir)/fsbc
	rm -Rf $(launcher_dir)/fsgs
	rm -Rf $(launcher_dir)/fstd
	rm -Rf $(launcher_dir)/fsui
	rm -Rf $(launcher_dir)/launcher
	rm -Rf $(launcher_dir)/oyoyo
	rm -Rf $(launcher_dir)/six
	rm -Rf $(launcher_dir)/workspace

	zip -d $(launcher_dir)/library.zip OpenGL/\*
	zip -d $(launcher_dir)/library.zip arcade/\*
	zip -d $(launcher_dir)/library.zip fsbc/\*
	zip -d $(launcher_dir)/library.zip fsgs/\*
	zip -d $(launcher_dir)/library.zip fstd/\*
	zip -d $(launcher_dir)/library.zip fsui/\*
	zip -d $(launcher_dir)/library.zip launcher/\*
	zip -d $(launcher_dir)/library.zip oyoyo/\*
	zip -d $(launcher_dir)/library.zip six/\*
	zip -d $(launcher_dir)/library.zip workspace/\*

	make -C ../python
	cp -a ../python/*.zip $(launcher_dir)

	python3 sign.py $(launcher_dir)/fs-uae-launcher.exe

zipfile:
	cd $(launcher_dir) && zip -9 -r ../../../$(launcher_dir).zip *

setup:
	sed s/9.8.7/${version}/g fs-uae-launcher.iss > fs-uae-launcher.iss2.tmp
	sed s/ARCH/${arch}/g fs-uae-launcher.iss2.tmp > fs-uae-launcher.iss.tmp
	python3 iscc.py fs-uae-launcher.iss.tmp
	python3 sign.py ../fs-uae-launcher_$(version)_windows_$(arch).exe
	rm fs-uae-launcher.iss.tmp

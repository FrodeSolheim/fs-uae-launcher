version = $(strip $(shell cat ../../VERSION))
arch = $(strip $(shell python3 ../arch.py))

emulator_dir = fs-uae_$(version)_windows_$(arch)
launcher_dir = fs-uae-launcher_$(version)_windows_$(arch)
# library_zip = $(launcher_dir)/lib/python36.zip
library_zip = $(launcher_dir)/lib/library.zip

all: progdir zip setup

clean:
	rm -Rf fs-uae-launcher-*_windows*
	rm -Rf fs-uae-launcher_*_windows*

progdir:
	rm -Rf $(launcher_dir)

	make -C ../..
	rm -Rf ../build

	# # Create dummy sqlite3.dll (cx_Freeze looks for it...)
	# mkdir -p /mingw32/DLLs
	# cp /mingw32/bin/libsqlite3-0.dll /mingw32/DLLs/sqlite3.dll
	# mkdir -p /mingw64/DLLs
	# cp /mingw64/bin/libsqlite3-0.dll /mingw64/DLLs/sqlite3.dll

	cd ../.. && python3 setup.py build_exe
	mv ../../build/exe.mingw-3.6 $(launcher_dir)

	# Remove dummy sqlite3.dll
	# rm /mingw32/DLLs/sqlite3.dll
	# rm /mingw64/DLLs/sqlite3.dll
	# rm  $(launcher_dir)/lib/sqlite3.dll

	# Remove debug libraries
	rm $(launcher_dir)/*d.dll

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

	rm -Rf $(launcher_dir)/amitools
	rm -Rf $(launcher_dir)/arcade
	rm -Rf $(launcher_dir)/fsbc
	rm -Rf $(launcher_dir)/fsgs
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
	zip -d $(library_zip) fstd/\*
	zip -d $(library_zip) fsui/\*
	zip -d $(library_zip) launcher/\*
	zip -d $(library_zip) OpenGL/\*
	zip -d $(library_zip) oyoyo/\*
	zip -d $(library_zip) workspace/\*

	# mv $(launcher_dir)/lib $(launcher_dir)/python3.6
	# mkdir -p $(launcher_dir)/lib
	# mv $(launcher_dir)/python3.6 $(launcher_dir)/lib/
	# mv $(launcher_dir)/lib/python3.6/python36.zip $(launcher_dir)/lib/

	mv $(launcher_dir)/lib/* $(launcher_dir)/
	rm -Rf $(launcher_dir)/lib

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

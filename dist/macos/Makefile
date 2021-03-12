version = $(strip $(shell cat ../../VERSION))
arch = $(strip $(shell python3 ../arch.py))
ver_os_arch = $(version)_macos_$(arch)

dname = fs-uae-launcher_$(ver_os_arch)
macos =  Launcher.app/Contents/MacOS
frameworks = Launcher.app/Contents/Frameworks
resources = Launcher.app/Contents/Resources
data = Launcher.app/Contents/Resources/Data
locale = Launcher.app/Contents/Resources/Locale
python = Launcher.app/Contents/Resources/Python
pylib = /Library/Frameworks/Python.framework/Versions/3.6/lib
qtdir = $(pylib)/python3.6/site-packages/PyQt5/Qt

all: bindist-launcher

clean:
	rm -Rf Launcher.app "FS-UAE Launcher.app"

cxfreeze: clean
	make -C ../..
	rm -Rf ../../build
	ln -fs $(qtdir)/lib/Qt*.framework $(pylib)
	cd ../.. && PYTHONHASHSEED=1 python3 setup.py build_exe
	rm  $(pylib)/Qt*.framework

	mkdir -p $(macos)
	mkdir -p $(resources)

	mkdir -p $(locale)
	cp -pPR ../../share/locale/* $(locale)/

	mkdir -p $(data)
	cp ../../cacert.pem $(data)/

	mv ../../build/*/* $(macos)
	mkdir -p ${python}
	mv $(macos)/library.zip ${python}/library.zip

	rm -Rf $(resources)/applications
	rm -Rf $(resources)/icons
	rm -Rf $(macos)/Qt*

addqt:
	rm -Rf ${macos}/platforms
	mkdir -p ${macos}/platforms
	cp $(qtdir)/plugins/platforms/libqcocoa.dylib ${macos}/platforms/

	rm -Rf ${macos}/imageformats
	mkdir -p ${macos}/imageformats
	cp $(qtdir)/plugins/imageformats/libqgif.dylib ${macos}/imageformats/
	cp $(qtdir)/plugins/imageformats/libqicns.dylib ${macos}/imageformats/
	cp $(qtdir)/plugins/imageformats/libqjpeg.dylib ${macos}/imageformats/
	cp $(qtdir)/plugins/imageformats/libqsvg.dylib ${macos}/imageformats/

	mkdir -p ${macos}/frameworks
	# cp -r $(qtdir)/lib/QtCore.framework $(frameworks)/
	# cp -r $(qtdir)/lib/QtGui.framework $(frameworks)/
	# cp -r $(qtdir)/lib/QtWidgets.framework $(frameworks)/
	# cp -r $(qtdir)/lib/QtOpenGL.framework $(frameworks)/
	# cp -r $(qtdir)/lib/QtDBus.framework $(frameworks)/
	# cp -r $(qtdir)/lib/QtPrintSupport.framework $(frameworks)/

	cp $(qtdir)/lib/QtCore.framework/Versions/5/QtCore $(macos)/
	cp $(qtdir)/lib/QtGui.framework/Versions/5/QtGui $(macos)/
	cp $(qtdir)/lib/QtWidgets.framework/Versions/5/QtWidgets $(macos)/
	cp $(qtdir)/lib/QtOpenGL.framework/Versions/5/QtOpenGL $(macos)/
	cp $(qtdir)/lib/QtDBus.framework/Versions/5/QtDBus $(macos)/
	cp $(qtdir)/lib/QtPrintSupport.framework/Versions/5/QtPrintSupport $(macos)/
	cp $(qtdir)/lib/QtSvg.framework/Versions/5/QtSvg $(macos)/

launcher: cxfreeze addqt
	find Launcher.app -name *_debug.dylib -delete

	# rm -Rf $(macos)/imageformats
	# rm -Rf $(macos)/platforms

	rm -f $(macos)/PyQt5.QtNetwork.so
	rm -f $(macos)/PyQt5.QtQml.so
	rm -f $(macos)/PyQt5.QtQuick.so

	python3 standalone.py Launcher.app

	# rm -f $(macos)/libncursesw.5.dylib

	cp Info.plist Launcher.app/Contents/
	cp ../../icon/fs-uae-launcher.icns $(resources)/fs-uae-launcher.icns

	make -C ../python

	rm -Rf $(macos)/amitools
	rm -Rf $(macos)/arcade
	rm -Rf $(macos)/fsbc
	rm -Rf $(macos)/fsgs
	rm -Rf $(macos)/fspy
	rm -Rf $(macos)/fstd
	rm -Rf $(macos)/fsui
	rm -Rf $(macos)/launcher
	rm -Rf $(macos)/OpenGL
	rm -Rf $(macos)/oyoyo
	rm -Rf $(macos)/workspace

	zip -d ${python}/library.zip amitools/\*
	zip -d ${python}/library.zip arcade/\*
	zip -d ${python}/library.zip fsbc/\*
	zip -d ${python}/library.zip fsgs/\*
	zip -d ${python}/library.zip fspy/\*
	zip -d ${python}/library.zip fstd/\*
	zip -d ${python}/library.zip fsui/\*
	zip -d ${python}/library.zip launcher/\*
	zip -d ${python}/library.zip OpenGL/\*
	zip -d ${python}/library.zip oyoyo/\*
	zip -d ${python}/library.zip workspace/\*

	# This file differs between each build
	zip -d ${python}/library.zip BUILD_CONSTANTS.pyc
	# Remove wrong-cased members from the archive
	zip -d ${python}/library.zip ConfigParser.pyc || true
	zip -d ${python}/library.zip Queue.pyc || true
	PYTHONPATH=../.. \
		python3 -m fspy.zipfile deterministic \
		--fix-pyc-timestamps ${python}/library.zip

	mkdir -p ${python}
	cp -a ../python/*.zip ${python}/

bindist-launcher: launcher
	rm -Rf "FS-UAE Launcher.app"
	mv Launcher.app "FS-UAE Launcher.app"
	# python3 sign.py "FS-UAE Launcher.app"
	GZIP=-9 tar Jcfv ../../$(dname).tar.xz "FS-UAE Launcher.app"

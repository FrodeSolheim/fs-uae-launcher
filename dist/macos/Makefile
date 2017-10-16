version = $(strip $(shell cat ../../VERSION))
arch = $(strip $(shell python3 ../arch.py))

ver_os_arch = $(version)_macos_$(arch)
dname = fs-uae-launcher_$(ver_os_arch)
app = $(dname)/"FS-UAE Launcher.app"
macos =  $(app)/Contents/MacOS/
frameworks = $(app)/Contents/Frameworks/
resources = $(app)/Contents/Resources/

all: bindist-launcher

clean:
	rm -Rf ../macos/fs-uae-launcher*

launcher:
	make -C ../..
	rm -Rf $(dname)
	mkdir -p $(dname)
	cd ../.. && python3 setup.py build_exe

	#mv ../dist/"FS-UAE Launcher.app" $(dname)/
	# cp -pPR fs-uae_$(ver_os_arch)/FS-UAE.app $(app)/Contents/Resources/

	mkdir -p $(macos)
	mkdir -p $(resources)
	cp -pPR ../../share/* $(resources)/
	cp ../../requests/cacert.pem $(macos)
	rm -Rf $(resources)/applications
	rm -Rf $(resources)/icons
	mv ../../build/*/* $(macos)
	find $(dname)/ -name *_debug.dylib -delete
	mv $(app) $(dname)/temp.app

	rm -f $(dname)/temp.app/Contents/MacOS/platforms/libqminimal.dylib
	rm -f $(dname)/temp.app/Contents/MacOS/platforms/libqoffscreen.dylib

	rm -f $(dname)/temp.app/Contents/MacOS/imageformats/libqdds.dylib
	rm -f $(dname)/temp.app/Contents/MacOS/imageformats/libqjp2.dylib
	rm -f $(dname)/temp.app/Contents/MacOS/imageformats/libqmng.dylib
	rm -f $(dname)/temp.app/Contents/MacOS/imageformats/libqsvg.dylib
	rm -f $(dname)/temp.app/Contents/MacOS/imageformats/libqtga.dylib
	rm -f $(dname)/temp.app/Contents/MacOS/imageformats/libqtiff.dylib
	rm -f $(dname)/temp.app/Contents/MacOS/imageformats/libqwbmp.dylib
	rm -f $(dname)/temp.app/Contents/MacOS/imageformats/libqwebp.dylib

	# mv $(dname)/temp.app/Contents/MacOS/platforms/* \
	# 	$(dname)/temp.app/Contents/MacOS
	# rm -Rf $(dname)/temp.app/Contents/MacOS/platforms
	# mv $(dname)/temp.app/Contents/MacOS/imageformats/* \
	# 	$(dname)/temp.app/Contents/MacOS
	# rm -Rf $(dname)/temp.app/Contents/MacOS/imageformats

	# cp -pPR `qtpaths --install-prefix`/qml/* $(dname)/temp.app/Contents/MacOS
	python3 fs-make-standalone-app.py $(dname)/temp.app

	mv $(dname)/temp.app $(app)
	cp Info.plist $(app)/Contents/
	cp ../../icon/fs-uae-launcher.icns $(resources)/fs-uae-launcher.icns

	make -C ../python

	rm -Rf $(macos)/amitools
	rm -Rf $(macos)/arcade
	rm -Rf $(macos)/fsbc
	rm -Rf $(macos)/fsgs
	rm -Rf $(macos)/fstd
	rm -Rf $(macos)/fsui
	rm -Rf $(macos)/launcher
	rm -Rf $(macos)/OpenGL
	rm -Rf $(macos)/oyoyo
	rm -Rf $(macos)/workspace

	zip -d $(macos)/library.zip amitools/\*
	zip -d $(macos)/library.zip arcade/\*
	zip -d $(macos)/library.zip fsbc/\*
	zip -d $(macos)/library.zip fsgs/\*
	zip -d $(macos)/library.zip fstd/\*
	zip -d $(macos)/library.zip fsui/\*
	zip -d $(macos)/library.zip launcher/\*
	zip -d $(macos)/library.zip OpenGL/\*
	zip -d $(macos)/library.zip oyoyo/\*
	zip -d $(macos)/library.zip workspace/\*

	cp -a ../python/*.zip $(macos)

	# cp -pPR `qtpaths --install-prefix`/qml $(app)/Contents/MacOS
	# python3 sign.py $(app)

bindist-launcher: launcher
	cd $(dname) && GZIP=-9 tar Jcfv ../../../$(dname).tar.xz *

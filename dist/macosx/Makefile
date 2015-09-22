version = $(strip $(shell cat ../../VERSION))
arch = $(strip $(shell python3 ../arch.py))

ver_os_arch = $(version)_macosx_$(arch)
dname = fs-uae-launcher_$(ver_os_arch)
app = $(dname)/"FS-UAE Launcher.app"
macos =  $(app)/Contents/MacOS/
frameworks = $(app)/Contents/Frameworks/
resources = $(app)/Contents/Resources/

all: bindist-launcher

clean:
	rm -Rf ../macosx/fs-uae-launcher*

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
	mv ../../build/*/* $(macos)
	find $(dname)/ -name *_debug.dylib -delete
	mv $(app) $(dname)/temp.app

	# cp -pPR `qtpaths --install-prefix`/qml/* $(dname)/temp.app/Contents/MacOS
	python3 fs-make-standalone-app.py $(dname)/temp.app

	mv $(dname)/temp.app $(app)
	cp Info.plist $(app)/Contents/
	cp ../../icon/fs-uae-launcher.icns $(resources)/fs-uae-launcher.icns

	# cp -pPR `qtpaths --install-prefix`/qml $(app)/Contents/MacOS

	# python3 sign.py $(app)

bindist-launcher: launcher
	cd $(dname) && GZIP=-9 tar zcfv ../../../$(dname).tar.gz *

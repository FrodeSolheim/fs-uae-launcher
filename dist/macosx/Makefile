version = $(strip $(shell cat ../../VERSION))
macos = fs-uae-launcher_$(version)_macosx/"FS-UAE Launcher.app"/Contents/MacOS/
frameworks = fs-uae-launcher_$(version)_macosx/"FS-UAE Launcher.app"/Contents/Frameworks/
resources = fs-uae-launcher_$(version)_macosx/"FS-UAE Launcher.app"/Contents/Resources/

all: bindist-launcher

clean:
	rm -Rf ../macosx/fs-uae-launcher*

launcher:
	make -C ../..
	rm -Rf fs-uae-launcher_$(version)_macosx	
	mkdir -p fs-uae-launcher_$(version)_macosx
	cd ../.. && python3 setup.py build_exe

	#mv ../dist/"FS-UAE Launcher.app" fs-uae-launcher_$(version)_macosx/
	# cp -pPR fs-uae_$(version)_macosx/FS-UAE.app fs-uae-launcher_$(version)_macosx/"FS-UAE Launcher.app"/Contents/Resources/

	mkdir -p $(macos)
	mkdir -p $(resources)
	cp -pPR ../../share/* $(resources)/
	mv ../../build/*/* $(macos)
	find fs-uae-launcher_$(version)_macosx/ -name *_debug.dylib -delete
	mv fs-uae-launcher_$(version)_macosx/"FS-UAE Launcher.app" fs-uae-launcher_$(version)_macosx/temp.app

	# cp -pPR `qtpaths --install-prefix`/qml/* fs-uae-launcher_$(version)_macosx/temp.app/Contents/MacOS
	python3 fs-make-standalone-app.py fs-uae-launcher_$(version)_macosx/temp.app

	mv fs-uae-launcher_$(version)_macosx/temp.app fs-uae-launcher_$(version)_macosx/"FS-UAE Launcher.app"
	cp Info.plist fs-uae-launcher_$(version)_macosx/"FS-UAE Launcher.app"/Contents/
	cp ../../icon/fs-uae-launcher.icns $(resources)/fs-uae-launcher.icns

	# cp -pPR `qtpaths --install-prefix`/qml fs-uae-launcher_$(version)_macosx/"FS-UAE Launcher.app"/Contents/MacOS

	# python3 sign.py fs-uae-launcher_$(version)_macosx/"FS-UAE Launcher.app"

bindist-launcher: launcher
	cd fs-uae-launcher_$(version)_macosx && GZIP=-9 tar zcfv ../../../fs-uae-launcher_$(version)_macosx.tar.gz *

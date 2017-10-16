lib = ../../build/lib
zip=zip -r

all: build

build:
	# cd ../../fs-uae-launcher && ./bootstrap
	cd ../.. && rm -Rf build/lib
	cd ../.. && python3 setup.py build

	cd $(lib) && rm -f *.zip

	# cd $(lib) && $(zip) --exclude="*.ttf" arcade.zip arcade
	cd $(lib) && $(zip) amitools.zip amitools
	mv $(lib)/amitools.zip .
	cd $(lib) && $(zip) arcade.zip arcade
	mv $(lib)/arcade.zip .
	cd $(lib) && $(zip) fsbc.zip fsbc
	mv $(lib)/fsbc.zip .
	# cd $(lib) && $(zip) fsboot.zip fsboot
	# mv $(lib)/fsboot.zip .
	cd $(lib) && $(zip) fsgs.zip fsgs
	mv $(lib)/fsgs.zip .
	cd $(lib) && $(zip) fstd.zip fstd
	mv $(lib)/fstd.zip .
	cd $(lib) && $(zip) fsui.zip fsui
	mv $(lib)/fsui.zip .
	cd $(lib) && $(zip) launcher.zip launcher
	mv $(lib)/launcher.zip .
	cd $(lib) && $(zip) OpenGL.zip OpenGL
	mv $(lib)/OpenGL.zip .
	cd $(lib) && $(zip) oyoyo.zip oyoyo
	mv $(lib)/oyoyo.zip .
	# cd $(lib) && $(zip) --exclude="*.ttf" workspace.zip workspace
	cd $(lib) && $(zip) workspace.zip workspace
	mv $(lib)/workspace.zip .

	cd ../.. && rm -Rf build/lib

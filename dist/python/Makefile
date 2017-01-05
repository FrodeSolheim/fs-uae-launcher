lib = ../../build/lib

all: build

build:
	# cd ../../fs-uae-launcher && ./bootstrap
	cd ../.. && rm -Rf build/lib
	cd ../.. && python3 setup.py build

	cd $(lib) && rm -f *.zip

	# cd $(lib) && zip -r --exclude="*.ttf" arcade.zip arcade
	cd $(lib) && zip -r amitools.zip amitools
	mv $(lib)/amitools.zip .
	cd $(lib) && zip -r arcade.zip arcade
	mv $(lib)/arcade.zip .
	cd $(lib) && zip -r fsbc.zip fsbc
	mv $(lib)/fsbc.zip .
	# cd $(lib) && zip -r fsboot.zip fsboot
	# mv $(lib)/fsboot.zip .
	cd $(lib) && zip -r fsgs.zip fsgs
	mv $(lib)/fsgs.zip .
	cd $(lib) && zip -r fstd.zip fstd
	mv $(lib)/fstd.zip .
	cd $(lib) && zip -r fsui.zip fsui
	mv $(lib)/fsui.zip .
	cd $(lib) && zip -r launcher.zip launcher
	mv $(lib)/launcher.zip .
	cd $(lib) && zip -r OpenGL.zip OpenGL
	mv $(lib)/OpenGL.zip .
	cd $(lib) && zip -r oyoyo.zip oyoyo
	mv $(lib)/oyoyo.zip .
	# cd $(lib) && zip -r --exclude="*.ttf" workspace.zip workspace
	cd $(lib) && zip -r workspace.zip workspace
	mv $(lib)/workspace.zip .

	cd ../.. && rm -Rf build/lib

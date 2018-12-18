lib = ../../build/lib
zip=zip -r
#copy=python3 ../../fspy/zipfile.py deterministic
cp=python3 -m fspy.zipfile deterministic

all: build

build:
	# cd ../../fs-uae-launcher && ./bootstrap
	cd ../.. && rm -Rf build/lib
	cd ../.. && python3 setup.py build

	cd $(lib) && rm -f *.zip

	# cd $(lib) && $(zip) --exclude="*.ttf" arcade.zip arcade
	cd $(lib) && $(zip) amitools.zip amitools
	# mv $(lib)/amitools.zip .
	PYTHONPATH=../.. $(cp) $(lib)/amitools.zip amitools.zip
	# rm $(lib)/amitools.zip

	cd $(lib) && $(zip) arcade.zip arcade
	PYTHONPATH=../.. $(cp) $(lib)/arcade.zip arcade.zip
	# rm $(lib)/arcade.zip

	cd $(lib) && $(zip) fsbc.zip fsbc
	PYTHONPATH=../.. $(cp) $(lib)/fsbc.zip fsbc.zip
	# rm $(lib)/fsbc.zip

	# cd $(lib) && $(zip) fsboot.zip fsboot
	# PYTHONPATH=../.. $(cp) $(lib)/fsboot.zip .
	# rm $(lib)/fsboot.zip

	cd $(lib) && $(zip) fsgs.zip fsgs
	PYTHONPATH=../.. $(cp) $(lib)/fsgs.zip fsgs.zip
	# rm $(lib)/fspy.zip

	cd $(lib) && $(zip) fspy.zip fspy
	PYTHONPATH=../.. $(cp) $(lib)/fspy.zip fspy.zip
	# rm $(lib)/fspy.zip

	cd $(lib) && $(zip) fstd.zip fstd
	PYTHONPATH=../.. $(cp) $(lib)/fstd.zip fstd.zip
	# rm $(lib)/fstd.zip

	cd $(lib) && $(zip) fsui.zip fsui
	PYTHONPATH=../.. $(cp) $(lib)/fsui.zip fsui.zip
	# rm $(lib)/fsui.zip

	cd $(lib) && $(zip) launcher.zip launcher
	PYTHONPATH=../.. $(cp) $(lib)/launcher.zip launcher.zip
	# rm $(lib)/launcher.zip

	cd $(lib) && $(zip) OpenGL.zip OpenGL
	PYTHONPATH=../.. $(cp) $(lib)/OpenGL.zip OpenGL.zip
	# rm $(lib)/OpenGL.zip

	cd $(lib) && $(zip) oyoyo.zip oyoyo
	PYTHONPATH=../.. $(cp) $(lib)/oyoyo.zip oyoyo.zip
	# rm $(lib)/oyoyo.zip

	# cd $(lib) && $(zip) --exclude="*.ttf" workspace.zip workspace
	cd $(lib) && $(zip) workspace.zip workspace
	PYTHONPATH=../.. $(cp) $(lib)/workspace.zip workspace.zip
	# rm $(lib)/workspace.zip

	cd ../.. && rm -Rf build/lib

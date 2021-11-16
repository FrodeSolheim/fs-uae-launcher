all: build

build:
	make -C src

gamecontrollerdb:
	if [ -e ../fs-gamecontrollerdb ]; then \
		cd ../fs-gamecontrollerdb && make ; \
		fi
	if [ -e ../fs-gamecontrollerdb ]; then \
		cp ../fs-gamecontrollerdb/Data/GameControllerDB/* \
		fsgamesys/data/GameControllerDB/ ; \
		fi

clean:
	rm -Rf build
	rm -rf fsbuild/_build
	rm -Rf .mypy_cache
	rm -Rf __pycache__

.PHONY: build

all: build

build:
	make -C src

clean:
	rm -Rf build
	rm -rf fsbuild/_build
	rm -Rf .mypy_cache
	rm -Rf __pycache__

.PHONY: build

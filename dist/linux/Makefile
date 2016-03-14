version = $(strip $(shell cat ../../VERSION))

all:
	make -C ../python
	./build.py $(version)

clean:
	rm -Rf *-linux-* *-steamos-*

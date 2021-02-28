. ./PACKAGE.FS
. fsbuild/system.sh

make

BUILDDIR=fsbuild/_build

rm -Rf $BUILDDIR/pyinstaller
if [ "$SYSTEM_OS" = "Windows" ]; then
pyinstaller \
	--windowed \
	--specpath pyinstaller \
	--distpath $BUILDDIR/pyinstaller \
	$PACKAGE_NAME
elif [ "$SYSTEM_OS" = "macOS" ]; then
false
else
pyinstaller \
	--specpath pyinstaller \
	--distpath $BUILDDIR/pyinstaller \
	$PACKAGE_NAME
fi

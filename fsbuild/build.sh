. ./PACKAGE.FS
. fsbuild/system.sh

BUILDDIR=fsbuild/_build

rm -Rf $BUILDDIR/pyinstaller

if [ "$SYSTEM_OS" = "macOS" ]; then
false
else
pyinstaller \
--specpath pyinstaller \
--distpath $BUILDDIR/pyinstaller \
$PACKAGE_NAME
fi

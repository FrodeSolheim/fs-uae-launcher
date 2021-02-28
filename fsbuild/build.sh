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
BINDIR=fsbuild/_build/pyinstaller/fs-uae-launcher
elif [ "$SYSTEM_OS" = "macOS" ]; then
pyinstaller \
	--windowed \
	--specpath pyinstaller \
	--distpath $BUILDDIR/pyinstaller \
	$PACKAGE_NAME
BINDIR=fsbuild/_build/pyinstaller/fs-uae-launcher.app/Contents/MacOS
# Symlinks do not seem to work with notarization
find $BINDIR -type l -delete
else
pyinstaller \
	--specpath pyinstaller \
	--distpath $BUILDDIR/pyinstaller \
	$PACKAGE_NAME
BINDIR=fsbuild/_build/pyinstaller/fs-uae-launcher
fi

# These do not work with macOS notarization, but might as well remove for all
# platforms.
rm -Rf $BINDIR/PyQt5/Qt/translations
rm -Rf $BINDIR/PyQt5/Qt/qml

. ./PACKAGE.FS
. fsbuild/system.sh

make

BUILDDIR=fsbuild/_build

# Remove files from PyQt5 that we don't want to bundle (before pyinstaller
# pulls in their dependencies).
python3 fsbuild/fix-pyqt5.py

rm -Rf $BUILDDIR/pyinstaller
if [ "$SYSTEM_OS" = "Windows" ]; then
pyinstaller \
	--specpath pyinstaller \
	--distpath $BUILDDIR/pyinstaller \
	--log-level DEBUG \
	--windowed \
	$PACKAGE_NAME
BINDIR=fsbuild/_build/pyinstaller/$PACKAGE_NAME
elif [ "$SYSTEM_OS" = "macOS" ]; then
pyinstaller \
	--specpath pyinstaller \
	--distpath $BUILDDIR/pyinstaller \
	--log-level DEBUG \
	--windowed \
	--osx-bundle-identifier no.fengestad.fs-uae-launcher \
	$PACKAGE_NAME
BINDIR=fsbuild/_build/pyinstaller/$PACKAGE_NAME.app/Contents/MacOS
else
pyinstaller \
	--specpath pyinstaller \
	--distpath $BUILDDIR/pyinstaller \
	--log-level DEBUG \
	$PACKAGE_NAME
BINDIR=fsbuild/_build/pyinstaller/$PACKAGE_NAME
fi

# These do not work with macOS notarization, but might as well remove for all
# platforms.
rm -Rf $BINDIR/PyQt5/Qt/translations
rm -Rf $BINDIR/PyQt5/Qt/qml

# In case the Qt dir is Qt5...
rm -Rf $BINDIR/PyQt5/Qt5/translations
rm -Rf $BINDIR/PyQt5/Qt5/qml

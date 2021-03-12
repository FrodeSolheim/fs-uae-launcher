#!/bin/sh

set -e

. fsbuild/plugin.pre.sh

mkdir -p $PLUGIN_BINDIR

if [ "$SYSTEM_OS" = "macOS" ]; then
cp -a fsbuild/_build/pyinstaller/$PACKAGE_NAME.app \
    $PLUGIN_BINDIR/$PACKAGE_NAME_PRETTY.app
cp ./icon/fs-uae-launcher.icns \
    $PLUGIN_BINDIR/$PACKAGE_NAME_PRETTY.app/Contents/Resources/
cat > $PLUGIN_BINDIR/$PACKAGE_NAME_PRETTY.app/Contents/Info.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>CFBundleDisplayName</key>
        <string>$PACKAGE_MACOS_BUNDLE_DISPLAY_NAME</string>
        <key>CFBundleExecutable</key>
        <string>MacOS/$PACKAGE_NAME</string>
        <key>CFBundleIconFile</key>
        <string>$PACKAGE_NAME.icns</string>
        <key>CFBundleIdentifier</key>
        <string>$PACKAGE_MACOS_BUNDLE_ID</string>
        <key>CFBundleInfoDictionaryVersion</key>
        <string>6.0</string>
        <key>CFBundleName</key>
        <string>$PACKAGE_NAME</string>
        <key>CFBundlePackageType</key>
        <string>APPL</string>
        <key>CFBundleShortVersionString</key>
        <string>$PACKAGE_VERSION_MAJOR.$PACKAGE_VERSION_MINOR.$PACKAGE_VERSION_REVISION</string>
</dict>
</plist>
EOF

else
cp -a fsbuild/_build/pyinstaller/$PACKAGE_NAME/* $PLUGIN_BINDIR/
fi

mkdir -p $PLUGIN_DATADIR/arcade
cp -a ./arcade/res $PLUGIN_DATADIR/arcade/
mkdir -p $PLUGIN_DATADIR/launcher
cp -a ./launcher/res $PLUGIN_DATADIR/launcher/
mkdir -p $PLUGIN_DATADIR/fsgs
cp -a ./fsgs/res $PLUGIN_DATADIR/fsgs/
mkdir -p $PLUGIN_DATADIR/fsui
cp -a ./fsui/res $PLUGIN_DATADIR/fsui/
mkdir -p $PLUGIN_DATADIR/workspace
cp -a ./workspace/res $PLUGIN_DATADIR/workspace/

PLUGIN_SKIP_APPIFY=1
PLUGIN_SKIP_STANDALONE=1

. fsbuild/plugin.post.sh

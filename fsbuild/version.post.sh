. ./PACKAGE.FS

echo "VERSION = \"$PACKAGE_VERSION\"" > launcher/version.py
echo "PACKAGER = \"$PACKAGE_PACKAGER\"" >> launcher/version.py
echo "COMMIT = \"$PACKAGE_COMMIT\"" >> launcher/version.py

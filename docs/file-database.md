# File database

## (More) efficient big file libraries

Write about support for indexing files named [sha-1], [sha-1].gz, [sha-1].xz.
Can read content checksum from file name and skip decompressing content when
scanning these.

Also supports symlinks, will read the checksum from symlink destination name.

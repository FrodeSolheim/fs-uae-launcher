import os
from os import path
from typing import Dict

from fsgamesys.files.installablefile import InstallableFile
from fsgamesys.files.installablefiles import InstallableFiles


class XpkMaster:
    @staticmethod
    def addFiles(installDir: str, *, files: Dict[str, InstallableFile]):
        return prepare_xpkmaster_files(installDir, files=files)


def prepare_xpkmaster_files(destDir: str, *, files: InstallableFiles):
    for relativePath, sha1 in xpkMasterFileMap.items():
        files[
            path.join(destDir, relativePath.replace("/", os.sep))
        ] = InstallableFile(sha1=sha1)
        # file_dest_dir = os.path.join(dest_dir, os.path.dirname(name))
        # self.install_whdload_file(sha1, file_dest_dir, value)
        # install_whdload_file(sha1, destdir, relative_path)


# FIXME: map to { sha1, size } dicts

xpkMasterFileMap = {
    "Libs/xpkmaster.library": "5bd19f9503b59c5d19bfe1c6a6e3b6e7c0e9eae2",
    "Libs/compressors/xpkCBR0.library": "a2a76c10cb06315e51990911fa050669cc89830d",
    "Libs/compressors/xpkDLTA.library": "ca64f89919c2869cb6fd75346b9a21245a6d04a8",
    "Libs/compressors/xpkDUKE.library": "8102d77ae0a3d64496436ee56a9c577c84b11992",
    "Libs/compressors/xpkFAST.library": "4599430f3baa302635a85b26a7b70a4116dc5f09",
    "Libs/compressors/xpkFRLE.library": "d0746429187ab38e886a47820203315f734e8d89",
    "Libs/compressors/xpkHFMN.library": "f4a8dbe69e386d87d9ab8cbaf7fc3881b358fdb2",
    "Libs/compressors/xpkHUFF.library": "f22d099b81d2d039c4fbb3fea47cc9700b01fecf",
    "Libs/compressors/xpkIMPL.library": "0e00bc18aec757d86f9831131c2236a704c175db",
    "Libs/compressors/xpkMASH.library": "1093133a17cb635c21c5532ae26ded83b6d359ce",
    "Libs/compressors/xpkNONE.library": "46dca6e2ff2176f7a12c52ea992a7a49ae5ef269",
    "Libs/compressors/xpkNUKE.library": "168bee97805be1f85b65f615e6931c4942caf4e4",
    "Libs/compressors/xpkRAKE.library": "50cd2a19bee1ebd6b54b31c5b9461d5a81a2e910",
    "Libs/compressors/xpkRLEN.library": "c81cf6d99de56faa6154cc81a9876517c2a8efc0",
    "Libs/compressors/xpkSHRI.library": "fc96d367e7b3409074841c7f145ab6daef0a6a4d",
    "Libs/compressors/xpkSMPL.library": "d140b4e87a2ff76cf94616d97fe7b127d128d973",
    "Libs/compressors/xpkSQSH.library": "2191b616abd4b2fb34c89ae243c35feea2b71104",
}

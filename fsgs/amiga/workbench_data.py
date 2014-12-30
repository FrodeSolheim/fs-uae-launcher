"""
This module contains information about files present on common Workbench
disks. The data is used when creating a Workbench environment on demand.
Some files are removed because they differ between Cloanto WB floppies and
original WB floppies.
"""
import os
import sys
import hashlib
import traceback
from fsgs.amiga.adf import ADFFile


wb_133_startup_sequence = """\
c:SetPatch >NIL: ;patch system functions
Addbuffers df0: 10
cd c:
echo "A500/A2000 Workbench disk.  Release 1.3.3 version 34.34*N"
Sys:System/FastMemFirst ; move C00000 memory to last in list
BindDrivers
SetClock load ;load system time from real time clock (A1000 owners should
              ;replace the SetClock load with Date
FF >NIL: -0 ;speed up Text
resident CLI L:Shell-Seg SYSTEM pure add; activate Shell
resident c:Execute pure
mount newcon:
;
failat 11
run execute s:StartupII ;This lets resident be used for rest of script
wait >NIL: 5 mins ;wait for StartupII to complete (will signal when done)
;
SYS:System/SetMap usa1 ;Activate the ()/* on keypad
path ram: c: sys:utilities sys:system s: sys:prefs add ;set path for Workbench
LoadWB delay  ;wait for inhibit to end before continuing
endcli >NIL:
"""


wb_204_startup_sequence = """\
c:setpatch >NIL:
c:version >NIL:
addbuffers >NIL: df0: 15
Failat 21

Resident >NIL: C:Execute PURE ADD

makedir ram:T ram:Clipboards ram:env ram:env/sys
copy >NIL: ENVARC: ram:env all quiet noreq

assign ENV: ram:env
assign T: ram:t ;set up T: directory for scripts
assign CLIPS: ram:clipboards
assign REXX: s:

if exists sys:Monitors
    join >NIL: sys:monitors/~(#?.info) as t:mon-start
    execute t:mon-start
    delete >NIL: t:mon-start
endif

BindDrivers

setenv Workbench $Workbench
setenv Kickstart $Kickstart

IPrefs

echo "Amiga Release 2.  Kickstart $Kickstart, Workbench $Workbench"

conclip

mount speak:
mount aux:
mount pipe:

path ram: c: sys:utilities sys:rexxc sys:system s: sys:prefs sys:wbstartup add
if exists sys:tools
    path sys:tools add
    if exists sys:tools/commodities
        path sys:tools/commodities add
    endif
endif

; If this is the initial boot (i.e. keyboard env variable is not set)
; then execute PickMap which will query for a keymap and set the
; keyboard env variable.
;
; if keyboard env variable is set, set the keymap
if ${sys/keyboard} NOT EQ "*${sys/keyboard}"
    setmap ${sys/keyboard}
else
    PickMap sys: initial
endif

if exists s:user-startup
    execute s:user-startup
endif

LoadWB

endcli >NIL:
"""


wb_300_startup_sequence = """\
; $VER: startup-sequence 39.9 (9.8.92)

C:SetPatch QUIET
C:Version >NIL:
C:AddBuffers >NIL: DF0: 15
FailAt 21

C:MakeDir RAM:T RAM:Clipboards RAM:ENV RAM:ENV/Sys
C:Copy >NIL: ENVARC: RAM:ENV ALL NOREQ

Resident >NIL: C:Assign PURE
Resident >NIL: C:Execute PURE

Assign >NIL: ENV: RAM:ENV
Assign >NIL: T: RAM:T
Assign >NIL: CLIPS: RAM:Clipboards
Assign >NIL: REXX: S:
Assign >NIL: PRINTERS: DEVS:Printers
Assign >NIL: KEYMAPS: DEVS:Keymaps
Assign >NIL: LOCALE: SYS:Locale
Assign >NIL: LIBS: SYS:Classes ADD
Assign >NIL: HELP: LOCALE:Help DEFER

IF NOT EXISTS SYS:Fonts
  Assign FONTS:
EndIF

BindDrivers
C:Mount >NIL: DEVS:DOSDrivers/~(#?.info)

IF EXISTS DEVS:Monitors
  IF EXISTS DEVS:Monitors/VGAOnly
    DEVS:Monitors/VGAOnly
  EndIF

  C:List >NIL: DEVS:Monitors/~(#?.info|VGAOnly) TO T:M LFORMAT "DEVS:Monitors/%s"
  Execute T:M
  C:Delete >NIL: T:M
EndIF

SetEnv Workbench $Workbench
SetEnv Kickstart $Kickstart
UnSet Workbench
UnSet Kickstart

C:IPrefs

C:ConClip

Path >NIL: RAM: C: SYS:Utilities SYS:Rexxc SYS:System S: SYS:Prefs SYS:WBStartup SYS:Tools SYS:Tools/Commodities

IF EXISTS S:User-Startup
  Execute S:User-Startup
EndIF

Resident Execute REMOVE
Resident Assign REMOVE

C:LoadWB
EndCLI >NIL:
"""


wb_133_files = {
    "c/": "",
    "c/AddBuffers": "b4935ca3f55fbf53db41a61d32cee48d93d1c431",
    "c/Ask": "20156be306fadfe45b8fde83bbc90258f371a00c",
    "c/Assign": "52579fe27010466442e928cb2a62cecc20f9f184",
    "c/Avail": "9d3d8ff67cfc4d7e220db53268830b0a5b5f0a2b",
    "c/Binddrivers": "0f7eaf913a9a8d50af3573a695a8f4af3b8f0ad6",
    "c/Break": "7c1cb7e382d36feb70b773b6cfd030ff853057e1",
    "c/CD": "9f4c181e7d5e3c0e103f462ba1420570499ca922",
    "c/ChangeTaskPri": "f63a5652aacd198b6ee25a2aefa3518a53f14ab6",
    "c/Copy": "ef236641b73d0b849f6ceb4a218469ea8f1d06f2",
    "c/Date": "287859f1c0fc0f1772c9e9c4f767bd523515b194",
    "c/Delete": "d6304c0e704c94073ad67edd19725a4742697ef6",
    "c/Dir": "c4c80a92749862fe8fe877dff0d7ab88a824026d",
    "c/DiskChange": "37665418b614fb1d768ea85c32a165cfaec146c1",
    # "c/DiskDoctor": "c801fbdcc4b04ff492a67cfeaee0036fce70bb85",
    "c/Echo": "b43fc80f2fb23af7c3ee14c8e1b5eecfc3c587ee",
    # "c/Ed": "dad70eb4a65febb74283c2a189d6bb95b22b0886",
    "c/Edit": "d83ee8a2e1f9d1697875366dafc329f8e8e4d7e9",
    "c/Else": "8f64d3d3fc7c84e02c4211e68ca74b2fa528df7b",
    "c/EndCLI": "24a5167194970a0188c00b234a12d2fba4308478",
    "c/EndIf": "7f15af4934c472489f278268667c2788c2a7021b",
    "c/EndSkip": "7f15af4934c472489f278268667c2788c2a7021b",
    "c/Eval": "5af8c120e9cf1399740dab3eca367af242d015cc",
    "c/Execute": "29b7093beae26deab1bd66a98167bfdb96aa7cf7",
    "c/Failat": "49918ba167529cef1320452d7442eac73712e0e7",
    "c/Fault": "e7f20bbe32843bca9c206cab8be50ae1d77b680f",
    # "c/FF": "dc9b9750c2a38546f7be2dbe983ae258f2496b98",
    "c/FileNote": "36d14d7468eb136b1179f04fa3c218832638e960",
    "c/GetEnv": "be841e3d1794a11b9af1b299ff1d8c9be85d8338",
    "c/IconX": "442df04019ae6ff426c3464f8be8c523ad292830",
    "c/If": "e0f0c4880f33ab782d903663535812f777362983",
    "c/Info": "a22a7a4aa07bad698b725253bd796c6fbdca9eb8",
    "c/Install": "1792a60e0564098429838d8db592b6297769d6f9",
    "c/Join": "0e8d276bb1f70a52c608cd8c8315ef8e84cceaef",
    "c/Lab": "7f15af4934c472489f278268667c2788c2a7021b",
    "c/List": "0d5c1cddab2af3e41bfe485e4a8cb76dc99c4bc4",
    "c/LoadWB": "13f61f0d60028256cc790f4cef3bcca83fb20259",
    "c/Lock": "f8a6d2e97b637c1ac1be97eaf77e3f12c79154ac",
    "c/Makedir": "d01c425e8af0f4f4084a6b2ee13780240db4f027",
    "c/Mount": "4f18b1c83c0f7a59eaa11c08e7a82cb7941740b3",
    "c/NewCLI": "9298e77f0adaa7a789d6e5f9f3035f24e60364d6",
    "c/NewShell": "7b827b5fa5456c9e1d722f2611437864be1bfdec",
    "c/Path": "770f775d73fdd8df8c1890be2ba2f9fbd388c06b",
    "c/Prompt": "5bb558e3f2ed62d5f676e84bc23f70ed913b4412",
    "c/Protect": "fec1b09d6a808b0e101ee2ed923a7f0e60597caa",
    "c/Quit": "e8f9244859b2e55e5c10304b1ca35e5801265c23",
    "c/Relabel": "496bc49e1488e8276e2074063b839269b34d1889",
    "c/RemRAD": "bca2dbf0ea2a8885fd976c04d421b884796d070a",
    "c/Rename": "b94baf0954756f75272576c7b34cdd6859d896d3",
    "c/Resident": "70c21c5a6add12526b29690f8bde0327f91b6f78",
    "c/Run": "caf92a05af573c54a1c9044e51ac6aeaab534e23",
    "c/Search": "0359aa4849bb1e7f7fa37862a4ab2f34b6d3b6fb",
    # "c/SetClock": "95d98f533207f53c1d90ddc57f2815db56d9bba7",
    "c/SetDate": "cca8245571bd7ffc4ddd46e87441b2600bf8be74",
    "c/SetEnv": "ac8df5ae6adfc7d68e5a3f514b935bd5293b09b7",
    "c/SetPatch": "3b36ee49e10626594545c564957fb4882ac2bfc3",
    "c/Skip": "15c513c48b568dc77593c13bf593fc6f8e0bcdb8",
    "c/Sort": "39f4a8a41ec5ab3cb030be579b49b6a3a7046f5a",
    "c/Stack": "d48dc30db5f9d6c7c04259444ba74b7c2f3dffd0",
    "c/Status": "08fffe1acc5dec49345e188eaba1f2fa74cd7424",
    "c/Type": "afb53409c675bac58048e8e76d403d61e91c1fc9",
    "c/Version": "bfa3c28746dc9a56df4569e687d0c7f6bb7e5b80",
    "c/Wait": "c893b36bd2376c003e3d2b2f5791d757c5fa33f9",
    "c/Which": "d1c3a0b2d9a0bcc3db3580182b75961981e9d38d",
    "c/Why": "84d318064b8374399bad8139c5f8f6046aa0b6e0",
    "devs/": "",
    "devs/clipboard.device": "d1708898f40bdb4f525e615e833e7f109331ac56",
    "devs/clipboards/": "",
    "devs/keymaps/": "",
    "devs/keymaps/usa1": "39d79e8a775260c13df0f657ee20e5f3e742de9e",
    "devs/MountList": "b85692e12b2fc7eaa02e4d211b043b5cd6272200",
    "devs/narrator.device": "d51631238dc07925b89e57ebe9d2e412400a0384",
    "devs/parallel.device": "861b780af555f52088adf5106bb62c05444dba82",
    "devs/printer.device": "5f06ec8cd7c32c40d78af95c8953ec527647a861",
    "devs/printers/": "",
    "devs/printers/generic": "aaaab28025bef46e5c01dde3d01d2f03fc63df2b",
    "devs/ramdrive.device": "ca60b73bc779d95cdcf23ec5e92b44dc21b1b472",
    "devs/serial.device": "55df2ec0a1d9dc6a03c9335737e23a38b2d73213",
    "devs/system-configuration": "f4e0ca14cbfb69c78c491d4cb4253a9a8ba9a78b",
    "Empty/": "",
    "Expansion/": "",
    "fonts/": "",
    "fonts/diamond.font": "cfe171bc8ab48615c6ac8fdfc5cd9da098f35e66",
    "fonts/diamond/": "",
    "fonts/diamond/12": "e6634c30e031dae19428423952f0abbe75d84559",
    "fonts/diamond/20": "75cb8014065834d1be7261a265bf0939e95d483a",
    "fonts/emerald.font": "98d935aa47ca406384bb6c592c63549f2d43d604",
    "fonts/emerald/": "",
    "fonts/emerald/17": "359d8c7da2e5ff4c157eed528c8c41a5ea09530a",
    "fonts/emerald/20": "de377bd498532ff4d3aa92e60fae8a029e7fc608",
    "fonts/garnet.font": "57e054da85337f25d660d2eb983dcf924a44ca4d",
    "fonts/garnet/": "",
    "fonts/garnet/16": "e99e9fde239b557ba181d91261f84abfda6f8bcb",
    "fonts/garnet/9": "5705e5553c85dc2e6573e4420d704e9fca5efe25",
    "fonts/opal.font": "dc66cd2d713f027b22539c503c5a5647e1f29fbf",
    "fonts/opal/": "",
    "fonts/opal/12": "ebb7b174ba5f215172921ec7e8cb3774eb21c90b",
    "fonts/opal/9": "0cea9720d43e2280b6fa8583fcefa364b9540446",
    "fonts/ruby.font": "314e2c9ca75cb75cadca1038d19a5ab92f2ed656",
    "fonts/ruby/": "",
    "fonts/ruby/12": "c5b1fd7d3834ebd2a26fc23c42f174451ddea1c7",
    "fonts/ruby/15": "58e3f44c65d75c9bff0a9992536c084c2572dbc9",
    "fonts/ruby/8": "a09b9ce5bd1c4a68773e6abfccc5218d0ddd066d",
    "fonts/sapphire.font": "18f992c2fef46fd408b272f07f9d5598c5e61bcb",
    "fonts/sapphire/": "",
    "fonts/sapphire/14": "fb0da752206e8b29e94f6e3d68492c2f794c54d5",
    "fonts/sapphire/19": "250e989ac01401b10773ad11cf9e45ad83437fe6",
    "fonts/topaz.font": "66b2ef88f256216f340a2130920c3dafdc5b3038",
    "fonts/topaz/": "",
    "fonts/topaz/11": "be925d2d0a61962ff1de9deb742747a356fc2b87",
    "l/": "",
    "l/Aux-Handler": "2e621414176ce93959e066cacc86f16c70bb7f80",
    "l/Disk-Validator": "30ede410472723c95338ed2c870916ad275e9706",
    "l/FastFileSystem": "cc14a3ce4805d4e3a0397fe6997ff5428d90ecdf",
    "l/Newcon-Handler": "c530e2ce63f2c6203526345fb2d434f2d4a9f49d",
    "l/Pipe-Handler": "4e73c34bcf73ab5b590c7b016dc1176673322077",
    "l/Port-Handler": "d7e4ddab8cbd94f751a6ffd4bc93cfe07cb4cae2",
    "l/Ram-Handler": "c0b036019fbffc46b417a72dd296f8d33b19a308",
    "l/Shell-Seg": "4bbe3ccb55fab49c83ff7ab52b2af277e6d92429",
    "l/Speak-Handler": "1b3b3dcd0b46cc6dbf98467e319d0d396e7df22f",
    "libs/": "",
    "libs/diskfont.library": "f1a4d45d97f2df1cff6b83a4392c34cc7ac18bbc",
    "libs/icon.library": "4c9b95e6f786f707aa51b2483a9f21ac5e66d7c9",
    "libs/info.library": "aa46c186d762dc68d2e799a5d13cad6745b55d10",
    "libs/mathieeedoubbas.library": "cf565b2b7a9f6e8aae030e32490346589f90b780",
    "libs/mathieeedoubtrans.library":
    "29f906dc50594aca3a91cfb69bd3f332fdb1671f",
    "libs/mathtrans.library": "65bae4aac804fb4db79a427f12b6ef1e16d22882",
    "libs/translator.library": "6ddc4462f261317a61f3c371091021b243df562c",
    "libs/version.library": "8f062571cac294bf5556b5bdc9d48da2c2f21fae",
    "Prefs/": "",
    "Prefs/CopyPrefs": "0af96045315193d4ec4f6c40d5ea6c3765d3fb04",
    "Prefs/Preferences": "e8b98bbb4cc3a04cf31855d4dcf6c292d02a48b4",
    "s/": "",
    "s/CLI-Startup": "c9abb720ab20b5976e18c45dd6eee46187b367f9",
    "s/DPAT": "bd0ee7066b43ef7df98db2801a75ab4f79f13098",
    "s/PCD": "d6ff57db9f9cd193d99aa64581ca964494b5e430",
    # "s/Shell-Startup": "25ee071ea6069e7fb10ac23bef1bbb24426b1bf1",
    "s/SPAT": "208cd7d832fb8a0d81d45fc3db7bc31c12727b3f",
    "s/Startup-Sequence.HD": "0d3caa59e5f867a6f9f8c68d318a16da1bf60fd6",
    # "s/StartupII": "dae0c0aeb988f27c5a9a85dcdf502998570b3b45",
    "Shell": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
    "System/": "",
    "System/CLI": "a6e7eb1585e4ebd6f4ed606eb18d8f23af184bea",
    "System/Diskcopy": "009cfa0952888c059da450b46d731d7f1779ae63",
    "System/FastMemFirst": "5fd51854d5b109fcdbf52809497e642036aa4722",
    "System/FixFonts": "3fc2dfbc62326678c3daf9ee860bac6330666999",
    # "System/Format": "972bbf474d471bec395d19f6d737908542055d70",
    "System/InitPrinter": "6d35a5215846acef053211dfcd6563054b51da10",
    "System/MergeMem": "04c018c68442187d292c0a57e1686bc8269f2ac4",
    "System/NoFastMem": "87e8c332e69a5446535923157cb6678ccb992614",
    "System/SetMap": "6d6c0ca1163c9d921b193d0e3c04722800c8c88d",
    "t/": "",
    "Trashcan/": "",
    "Utilities/": "",
    "Utilities/Calculator": "66d0b0fcb4795517c6d30cb96662afce68d81585",
    "Utilities/Clock": "ca791b988dd647432dd36dcc519bc5ce7d2e0bd2",
    "Utilities/ClockPtr": "47c191dd0edeccbf80cb5402002101bcc791e171",
    "Utilities/CMD": "7e0917b6fbf4152fd9167af0eee2118b35d48fe7",
    "Utilities/GraphicDump": "b82aa41aa1d602a1e1452d757797dd22b97dc75a",
    "Utilities/InstallPrinter": "05f57e5ffc717c7a4eb80bb3917be6006ebdc0b0",
    "Utilities/More": "2eb6ab87d1ee9bf28bea826e2481dd3c4f6c1447",
    "Utilities/Notepad": "ca9e25cd122dc01a28b66eb8f3ebc3395504e6b7",
    "Utilities/PrintFiles": "66d70dae78836d1aa198b9fd46492f204be0459f",
    "Utilities/Say": "3f845bf4d06c680c960847115449adb4819cd8b7",
}


wb_204_files = {
    "C/": "",
    "C/AddBuffers": "6ed1a3f24a1f605aa7234410faebbfbb3fda3ee6",
    "C/Assign": "b5b7edb67f578019d46af425a16458ec0cdb1c2e",
    "C/Avail": "5e62c202fe3cb447a19c39efb43c935eed139a66",
    "C/BindDrivers": "7534362e5def2eb32819be52f242d28ebdc05a26",
    "C/Break": "97ca2404e17fc78e3d988131bb17183c5c3aa15a",
    "C/ChangeTaskPri": "66533bb2cee36475b03cd73ae8ab198889e81be3",
    "C/ConClip": "96dd0671b40743c18f9ec2b58b2ccb731092e29f",
    "C/Copy": "628a17ad2b883565a1312d105a65764076c42013",
    "C/CPU": "40bcedc1af7677096cb1e5f5e41e147cf4c952fc",
    "C/Date": "0d190c0ce0b99cd653a8f982964eed110ac540eb",
    "C/Delete": "0597fd916dd28850ef68bb904937cad0d347cf5a",
    "C/Dir": "184eef562670fd6b22b3025e385f992469fa50d4",
    "C/DiskChange": "2cae12bfbb1cc98348e7afabf0f48b09cadbaf5e",
    "C/DiskDoctor": "c801fbdcc4b04ff492a67cfeaee0036fce70bb85",
    "C/Ed": "077483aacde3b40eeeb7b2b08cff3c18d6174e1c",
    "C/Edit": "14a1b22e4d72f85cd64b49cfdc8380b294f2da15",
    "C/Eval": "fae9792514d07b6fbb5b04d778492941dee5c448",
    "C/Execute": "ef1e6f6db0f3a513e0dc98add537e1db87b1856a",
    "C/Filenote": "6c263e034a3aca677467d410e410ba808a5f2b8d",
    "C/IconX": "9a2088f98175b3341f8bf4831599d54832430c35",
    "C/Info": "d12eea32aef864fcb4717ee8447c01d5900c94f1",
    "C/Install": "b5e1a2ea287c29390d38e47ccb3749f7c449bd4e",
    "C/IPrefs": "f3eb8607aaac99043020f0a9a1156dec4f941a11",
    "C/Join": "da8d787eadd16e682216c808cbbd1427acde7280",
    "C/List": "74a07847e45f8ae61daa029dd21775f438013a08",
    "C/LoadWB": "c705d1579c04505819a6bc3c6c29ae8d2610da66",
    "C/Lock": "a671aabf698196baa6a237601d07fb49b7f64f60",
    "C/MagTape": "8d14c533f6fb73286a642bb208151c36da3af2c9",
    "C/MakeDir": "3e00b210538357ff2ca9f0bc16471f06fb994282",
    "C/MakeLink": "da8472a553ece5484d7ba1290884ad5d59db5770",
    "C/Mount": "b2f1e59e977cec1c83166977cd4350f5388c3c9f",
    "C/Protect": "e95073c0169dd7c7ca39b9842b339a1288ca3016",
    "C/Relabel": "056cb6a12033f5638b1353be1007106fd9267a6e",
    "C/RemRAD": "7e5d53c865debaa9d752f96ef818320248332ef6",
    "C/Rename": "d1cb2ab35c8fa0dc912b98dbcf002c2c3b220988",
    "C/Search": "89c1dd049ca2fff58269fd44af2705abdedff112",
    "C/SetClock": "0c166dd6f8baa45eda766f3b41a0f799f8e7f388",
    "C/SetDate": "d7a78803ade6e09dbbba051ab6d4fbcb923527eb",
    "C/SetFont": "8b5bd918009242703f5f8ae9237199bd35ef0efe",
    "C/SetPatch": "309db203c5c88d2867d9d6f75e5ef67d2c558a95",
    "C/Sort": "d886f81bdc74f4942acb52680e56d8bf50a0be8a",
    "C/Status": "71e09cfc79d8ede0721ba4a01e1cd43a6318a99f",
    "C/Type": "00917f88e78770f6b28562bede2cf64718325553",
    "C/Version": "86dcf19836869c7319a1b89083a0529d1ee0d049",
    "C/Wait": "a0d503a136dad028ec51e33cfd57d130c1b4b807",
    "C/Which": "22952cce8446a1405b1b22d057ec19614e38c366",
    "Devs/": "",
    "Devs/clipboard.device": "83f3490b6480a0515b37e6f926ab48daf9cad61e",
    "Devs/Keymaps/": "",
    "Devs/MountList": "b32b62007cbfd4e5412f003f3fd83a183845b447",
    # "Devs/narrator.device": "c5a35d605c39b9c59542d71883238a02e92d726d",
    "Devs/parallel.device": "88c8c2bae625caf7b2bdbea9688a763f035bc199",
    "Devs/printer.device": "b13d1ec922deafa5a479fc1c591f911ff95559eb",
    "Devs/Printers/": "",
    "Devs/Printers/generic": "11473c5271b970e36c70b408aac7c67fff7d97b6",
    "Devs/serial.device": "d814d6ce8efb4a87966dae581eddf4dca528094a",
    "Devs/system-configuration": "4be3d7e8395a5827085f57cb6cdbf5e88fa78506",
    "Expansion/": "",
    "Fonts/": "",
    "L/": "",
    "L/aux-handler": "5a20c44cdcba0793fd292e3f951832ad4670f65e",
    "L/port-handler": "d7e4ddab8cbd94f751a6ffd4bc93cfe07cb4cae2",
    "L/queue-handler": "a458c6935c90d8a9422600c84875237e0558f89b",
    # "L/speak-handler": "d577708e1a0be7566885824349102025f1a250c4",
    "Libs/": "",
    "Libs/asl.library": "8d1fd81d7c128c397443f0ceb696dab3fecc5828",
    "Libs/commodities.library": "eaa02d69480d8df876f3932bf13f7c6e6ebc6c78",
    "Libs/diskfont.library": "97022049498794fe8f6135b53ed01d0688903499",
    "Libs/iffparse.library": "32eb189c8c003e8bdb1c836fa0ffd12a5d2c9f17",
    "Libs/mathieeedoubbas.library": "ce7888086d9749d738e1141e7b7e200f5eb780a9",
    "Libs/mathieeedoubtrans.library":
    "6d6e29a25f7bc87d26a56d437441d3a2c789b126",
    "Libs/mathieeesingtrans.library":
    "b9b164b6a7bff61ffd703999c93f756ea447452f",
    "Libs/mathtrans.library": "92d5888b3d2d3bb83c66cc6e486d303821c518c9",
    "Libs/rexxsupport.library": "7ae7acdd99a89d00b706060f818ad340869827a2",
    "Libs/rexxsyslib.library": "b74995c09a0d6350498579b8ff406477ae5b9566",
    # "Libs/translator.library": "e99c035faf5184a3397c89a3df1a7606c8417be6",
    "Libs/version.library": "ac699c82157ccc204aaf1eb78e3c53c4a8f13bf5",
    "Monitors/": "",
    "Prefs/": "",
    "Prefs/Env-Archive/": "",
    "Prefs/Env-Archive/sys/": "",
    "Prefs/Env-Archive/sys/wbconfig.prefs":
    "9658314fdb2a32286dba8830cf701469ac0089d3",
    "Prefs/Font": "c8d0f7bd565fb151ff0738e9df9f063cd43cf244",
    "Prefs/IControl": "c3d984f4ca7213194c8bfa5cb20ef8487c107e7a",
    "Prefs/Input": "37b19e8dd679c1d901c6620d0635cd9a56b92ab9",
    "Prefs/Overscan": "d15843c3147bff57f3dd4ffc2303d1609ca0eb12",
    "Prefs/Palette": "3d8712e5b337e8a02c5e786975b5724bd9716f8e",
    "Prefs/Pointer": "79c013f9d2065b7c2f824e530c05e65b182c00de",
    "Prefs/Presets/": "",
    "Prefs/Printer": "89a003a1b26c5a0b9eb2fdf6ddd53cb5368445cb",
    "Prefs/PrinterGfx": "84d71c99acac85cf65cf073e736b55871e286d2c",
    "Prefs/ScreenMode": "640adc69430a72f08a42761b4d3740840d95a834",
    "Prefs/Serial": "8b7e24eb43396dc0fc5a341a2425213fb7d77ac3",
    "Prefs/Time": "bb07a47dbb7453fbeb61ecae5ba9459f33b4217c",
    "Prefs/WBPattern": "42b809a0d4f02ea5e7f720df3e7a5e97827a1689",
    "Rexxc/": "",
    "Rexxc/HI": "d3934c81b5a7832f0cdd64650f7c74eacc608a0a",
    "Rexxc/RX": "527adec943412976b2d40c4556ca48e0a5b0abee",
    "Rexxc/RXC": "b42afa06c53df3221683a2d42b2b2ce4f38a4525",
    "Rexxc/RXLIB": "04b10ce3d05feb2fdbd722e5a275a0c844e7d86e",
    "Rexxc/RXSET": "702b4613236e8faba2270744229171dc46a0d5ed",
    "Rexxc/TCC": "473c7136e636b9505332118cd69a3ba29db0dbbe",
    "Rexxc/TCO": "f8b901a6ec8c6844a7205f5ceec5aad6e6261531",
    "Rexxc/TE": "2f89c6cd66e559b6f3cf5a0783b14fb18236931d",
    "Rexxc/TS": "45a5aa31dd4d42099d41948ef976599fa221938d",
    "Rexxc/WaitForPort": "f3fea65223cb028f479d1831237385812675a065",
    "S/": "",
    "S/BRUtab": "36cad75345610b07e447edb5000a368ce14de0df",
    "S/DPat": "4c8aac6a4989201c01d36247a9622288beb6d291",
    "S/Ed-startup": "298221ea95f4bfa2cc9b0cec4d8643f708a16abc",
    "S/HDBackup.config": "5284e3e2897148a373da769df16530cd1fff45c6",
    "S/PCD": "d6ff57db9f9cd193d99aa64581ca964494b5e430",
    "S/PickMap": "0b9ca76ba793031e11dfd14cf26b1257f9b24d89",
    "S/Shell-startup": "3d50527c6c17256f50d04d212d97d0fb27bf862f",
    "S/SPat": "870ac2f50dbb2a75989c5418a2012df81455bea8",
    "S/Startup-sequence.HD": "d66c044a25bc4235ec1d2479f368aca733a4d77d",
    "System/": "",
    "System/AddMonitor": "9ef54a726a70298608654a8be35388adbbd4a5eb",
    "System/BindMonitor": "5bafd3b20970c9cb05e9619f28091d56ad1dc2c8",
    "System/CLI": "1d22d9100a26d12d375fe1fd938f46b5c09017f1",
    "System/DiskCopy": "c91ae2a853c386c6c4c2c5dbed394bc69074f552",
    "System/FixFonts": "5f093b674d951599af5b5b2f82f3007cfdfa2902",
    "System/Format": "e8f87083aefbaf68f03947accca10278b95ad9d5",
    "System/NoFastMem": "abb2cff5c39351d111bce07c22585d58219b31a1",
    "System/RexxMast": "6f64f8bc51aec68344fae4151697976f59946b8e",
    "System/Setmap": "859abaaab6de713c2a46043f5f5421d54b79d88f",
    "t/": "",
    "Trashcan/": "",
    "Utilities/": "",
    "Utilities/Clock": "079dadb61258bbb07112a4109b58552fe61f5741",
    "Utilities/Display": "5c21232ceea79568d915d2d9d0a96e80e01fd4cb",
    "Utilities/Exchange": "b227f5823b2b07f92670f2628426645fbfa4ec40",
    "Utilities/More": "39d44f82ad645b9b1cd2931125c5b340613f7e29",
    "Utilities/Say": "79614ec17080d87d580f6cd1e20e74f53c1b5174",
    "WBStartup/": "",
}


wb_300_files = {
    "C/": "",
    "C/AddBuffers": "6ed1a3f24a1f605aa7234410faebbfbb3fda3ee6",
    "C/AddDataTypes": "e8bbd0b50fb5de6fa2382e845e1d67011a1ddd2a",
    "C/Assign": "b5b7edb67f578019d46af425a16458ec0cdb1c2e",
    "C/Avail": "5e62c202fe3cb447a19c39efb43c935eed139a66",
    "C/BindDrivers": "be270c04b4591f10da960231e488929d67e58135",
    "C/Break": "97ca2404e17fc78e3d988131bb17183c5c3aa15a",
    "C/ChangeTaskPri": "66533bb2cee36475b03cd73ae8ab198889e81be3",
    "C/ConClip": "956fd130af649ac441d4b68ea9b01e29d4861357",
    "C/Copy": "0c5f9470fbcb36fdbcdf970fd1b22aa627328a24",
    "C/CPU": "0191712ede6348b8e1803f5807a941a85c12bd0a",
    "C/Date": "0d190c0ce0b99cd653a8f982964eed110ac540eb",
    "C/Delete": "0597fd916dd28850ef68bb904937cad0d347cf5a",
    "C/Dir": "184eef562670fd6b22b3025e385f992469fa50d4",
    "C/DiskChange": "2cae12bfbb1cc98348e7afabf0f48b09cadbaf5e",
    "C/Ed": "077483aacde3b40eeeb7b2b08cff3c18d6174e1c",
    "C/Edit": "14a1b22e4d72f85cd64b49cfdc8380b294f2da15",
    "C/Eval": "fae9792514d07b6fbb5b04d778492941dee5c448",
    "C/Execute": "ef1e6f6db0f3a513e0dc98add537e1db87b1856a",
    "C/Filenote": "6c263e034a3aca677467d410e410ba808a5f2b8d",
    "C/IconX": "09bd52d33b700538e9bed493f245a3ffce944ad3",
    "C/Info": "3f5f37e405ca929cf0b4c6ac6abbf7f8d4f19892",
    "C/Install": "b4bf5e4ecda66c6a66e1780d1143f632e573ed3b",
    "C/IPrefs": "5b5b70ec7b06a6fa142d01372a4e0fce1bff5461",
    "C/Join": "da8d787eadd16e682216c808cbbd1427acde7280",
    "C/List": "86c0a28542939ea5e0d2075f9db337d93b139fb7",
    "C/LoadWB": "e663a715c6ad69a7d3882b4772cbdc9de835e791",
    "C/Lock": "a671aabf698196baa6a237601d07fb49b7f64f60",
    # "C/MagTape": "8d14c533f6fb73286a642bb208151c36da3af2c9",
    "C/MakeDir": "3e00b210538357ff2ca9f0bc16471f06fb994282",
    "C/MakeLink": "da8472a553ece5484d7ba1290884ad5d59db5770",
    "C/Mount": "c691df2ceb10c6dccd4f735dea0f07c199e09074",
    "C/Protect": "e95073c0169dd7c7ca39b9842b339a1288ca3016",
    "C/Relabel": "056cb6a12033f5638b1353be1007106fd9267a6e",
    "C/RemRAD": "7e5d53c865debaa9d752f96ef818320248332ef6",
    "C/Rename": "d1cb2ab35c8fa0dc912b98dbcf002c2c3b220988",
    "C/RequestChoice": "5198856e4ebc9c88e5799627aeceaa42866f6525",
    "C/RequestFile": "46a45ca9906b52a215161c2141193fe740f41d71",
    "C/Search": "89c1dd049ca2fff58269fd44af2705abdedff112",
    "C/SetClock": "0c166dd6f8baa45eda766f3b41a0f799f8e7f388",
    "C/SetDate": "d7a78803ade6e09dbbba051ab6d4fbcb923527eb",
    "C/SetFont": "3b2bb7bb70d84a230a4614dae34c064b7cfc315d",
    "C/SetKeyboard": "d32a3aed9f10fdcbb4335296be50f70f2f15438e",
    "C/SetPatch": "4d4aae988310b07726329e436b2250c0f769ddff",
    "C/Sort": "d886f81bdc74f4942acb52680e56d8bf50a0be8a",
    "C/Status": "71e09cfc79d8ede0721ba4a01e1cd43a6318a99f",
    "C/Type": "00917f88e78770f6b28562bede2cf64718325553",
    "C/Version": "5a698d6494fa50fd3faa7e532def17b6c561d217",
    "C/Wait": "a0d503a136dad028ec51e33cfd57d130c1b4b807",
    "C/Which": "22952cce8446a1405b1b22d057ec19614e38c366",
    "Classes/": "",
    "Classes/DataTypes/": "",
    "Classes/DataTypes/8svx.datatype":
    "dae1f0ff6171479b27c21d3e32f7d4e383f969ab",
    "Classes/DataTypes/amigaguide.datatype":
    "d53c3e6abd119a3ca7c15805642a1e6ec96d374c",
    "Classes/DataTypes/ascii.datatype":
    "6f54362a5ce75221a62e0f1fd3a5d23fabc0f2bd",
    "Classes/DataTypes/ilbm.datatype":
    "c8251ed31ad79aa71cf6d3c134815c8f38c70226",
    "Classes/DataTypes/picture.datatype":
    "8028e6782c4069c45ffc4b51cef493f8339a1be9",
    "Classes/DataTypes/sound.datatype":
    "e4fbdbc5e55ddc4635dcd2e76e5623217c4a41a2",
    "Classes/DataTypes/text.datatype":
    "e6b80a188123cb397f7a79a1b580206bb369f2e2",
    "Classes/Gadgets/": "",
    "Classes/Gadgets/colorwheel.gadget":
    "7bbfccb8fd5d68b2ae8aac226eff877e8ebc9734",
    "Classes/Gadgets/gradientslider.gadget":
    "a54f39e9098f2c58e892b9183b555fe0a8574191",
    "Devs/": "",
    "Devs/clipboard.device": "c8d85bd384ea5033d5474283e83c02ad6cdaf32b",
    "Devs/DataTypes/": "",
    "Devs/DataTypes/8SVX": "b9116bb7654e12f7d281d32ca333a0f283e15532",
    "Devs/DataTypes/AmigaGuide": "e89b0bf0d75585b8f27e40d711164ab9e2a0c222",
    "Devs/DataTypes/FTXT": "cee60b9550ace3d44ba1d214ed350b05587c3919",
    "Devs/DataTypes/ILBM": "1cf3598ca839c554e6a7acc333ddd8327f8ac5d3",
    "Devs/DOSDrivers/": "",
    "Devs/DOSDrivers/PIPE": "624dd68e9a2794bf5bd60e58c1b3679a1dfd273c",
    "Devs/Keymaps/": "",
    # "Devs/mfm.device": "63b150010e420f96304375badca126812daa2255",
    "Devs/Monitors/": "",
    "Devs/parallel.device": "88c8c2bae625caf7b2bdbea9688a763f035bc199",
    "Devs/postscript_init.ps": "3c0bc3408a4ac929936f647637a04f45d227cca0",
    "Devs/printer.device": "aaf3970e54bedaf84cd69268fc6cf3730c395ba1",
    "Devs/Printers/": "",
    "Devs/Printers/Generic": "11473c5271b970e36c70b408aac7c67fff7d97b6",
    "Devs/serial.device": "d814d6ce8efb4a87966dae581eddf4dca528094a",
    "Devs/system-configuration": "4be3d7e8395a5827085f57cb6cdbf5e88fa78506",
    "Expansion/": "",
    "L/": "",
    # "L/aux-handler": "5a20c44cdcba0793fd292e3f951832ad4670f65e",
    # "L/CrossDOSFileSystem": "9f05f997b3aa0c3a431bea96cc4bbc153ba48814",
    # "L/FileSystem_Trans/": "",
    # "L/FileSystem_Trans/DANSK.crossdos":
    # "3db3dbfdb9f6d874368f12152944b00099fd9943",
    # "L/FileSystem_Trans/INTL.crossdos":
    # "6d803e82923564dd2f12b68836b2356282edfd93",
    "L/port-handler": "d7e4ddab8cbd94f751a6ffd4bc93cfe07cb4cae2",
    "L/queue-handler": "a458c6935c90d8a9422600c84875237e0558f89b",
    "Libs/": "",
    "Libs/amigaguide.library": "42b1ea9b94f12f4ad5275bb29a8a49fb977f1910",
    "Libs/asl.library": "ae59765242d7d1fc022d819a980652463e72688a",
    "Libs/bullet.library": "efffa71e955805d543842cbd0c67e75b591fe567",
    "Libs/commodities.library": "e52e0a7e2fb653a6895fb1cf15d0b37aed18f909",
    "Libs/datatypes.library": "1ea18282089ae14620c1fc71e82592d52217ff2a",
    "Libs/diskfont.library": "15d9765f1b66c4a3068d11186ea5bf41a8c8ad3b",
    "Libs/iffparse.library": "946ef60b4ba9f63593dbadfbc447546d7ab9725c",
    "Libs/locale.library": "a12b91f662a1c527ff6411b43555bc7eaeb370b4",
    "Libs/mathieeedoubbas.library": "08d8508cdcb77ad421a6dd6f80721b727c09d96b",
    "Libs/mathieeedoubtrans.library":
    "6d6e29a25f7bc87d26a56d437441d3a2c789b126",
    "Libs/mathieeesingtrans.library":
    "b9b164b6a7bff61ffd703999c93f756ea447452f",
    "Libs/mathtrans.library": "92d5888b3d2d3bb83c66cc6e486d303821c518c9",
    "Libs/rexxsupport.library": "7ae7acdd99a89d00b706060f818ad340869827a2",
    "Libs/rexxsyslib.library": "b74995c09a0d6350498579b8ff406477ae5b9566",
    "Libs/version.library": "9af4fa21ce77ca97b4604ffb095a9b2488295c85",
    "Prefs/": "",
    "Prefs/Env-Archive/": "",
    "Prefs/Env-Archive/Sys/": "",
    "Prefs/Env-Archive/Sys/wbconfig.prefs":
    "9658314fdb2a32286dba8830cf701469ac0089d3",
    "Prefs/Presets/": "",
    "Rexxc/": "",
    "Rexxc/HI": "d3934c81b5a7832f0cdd64650f7c74eacc608a0a",
    "Rexxc/RX": "527adec943412976b2d40c4556ca48e0a5b0abee",
    "Rexxc/RXC": "b42afa06c53df3221683a2d42b2b2ce4f38a4525",
    "Rexxc/RXLIB": "04b10ce3d05feb2fdbd722e5a275a0c844e7d86e",
    "Rexxc/RXSET": "702b4613236e8faba2270744229171dc46a0d5ed",
    "Rexxc/TCC": "473c7136e636b9505332118cd69a3ba29db0dbbe",
    "Rexxc/TCO": "f8b901a6ec8c6844a7205f5ceec5aad6e6261531",
    "Rexxc/TE": "2f89c6cd66e559b6f3cf5a0783b14fb18236931d",
    "Rexxc/TS": "45a5aa31dd4d42099d41948ef976599fa221938d",
    "Rexxc/WaitForPort": "f3fea65223cb028f479d1831237385812675a065",
    "S/": "",
    # "S/DPat": "227c6ed4ae33850577a0b03e22b7dfd966b421c4",
    "S/Ed-startup": "2a4e2dd940726199aea3c5cab73dcc527b624fb8",
    # "S/PCD": "02d4b5292a9ea3b56d68ca7bba3d1df5055b3a25",
    "S/Shell-Startup": "d039a940c89ec6c30a1b3568bfd6afe626a28b6d",
    # "S/SPat": "4f63e17cb9ca68b5dc5eb37fd02508f4c5ae0761",
    "System/": "",
    "System/CLI": "9f25538fd0a6b134dd7a094350731cdc1e9234e3",
    "System/DiskCopy": "902aa22b272961911a279bba4aca1fd7ba9c537b",
    "System/FixFonts": "86757c1120ce2137e3c72024fa9de898de8a7b24",
    "System/Format": "76918338279f5c1a2b86405f39d9e9c8e9ac0981",
    "System/NoFastMem": "6295d9937d3eb3370af14bf510c9ad02f687bd4b",
    "System/RexxMast": "6f64f8bc51aec68344fae4151697976f59946b8e",
    "T/": "",
    "Utilities/": "",
    "Utilities/Clock": "fda1ad2f1bfb730d9c0dbda4b1141935b67f65ae",
    "Utilities/More": "daced6e93fce3bf91a659ea161e343b87233cc54",
    "Utilities/MultiView": "c8e7b9f35907e168a03f5b46c9890b4094077750",
    "WBStartup/": "",
}


wb_133_floppies = [
    # Workbench v1.3.3 rev 34.34 (1990)(Commodore)(A500-A2000)
    # (Disk 1 of 2)(Workbench).adf
    "86cb4e007f9fdcf6c5eda6adba3f60f188063875",
    # Workbench v1.3.3 rev 34.34 (1990)(Commodore)(A500-A2000)(Dk)
    # (Disk 1 of 2)(Workbench)[m].adf
    "8d8314faa3b5fbc472c11d5fc669358522c1d00b",
    # amiga-os-134-workbench.adf
    "42c5af6554212e9d381f7535c3951ee284e127b2",
]


wb_204_floppies = [
    # Workbench v2.04 rev 37.67 (1991)(Commodore)
    # (Disk 1 of 4)(Workbench).adf
    "8d5c0310a86f14fb3e6a1da001ceb50b9a592c51",
    # Workbench v2.04 rev 37.67 (1991)(Commodore)
    # (Disk 1 of 4)(Workbench)[m].adf
    "d9d8bc1964d9159b3669fadedcd140ead197b0b7",
    # Workbench v2.04 rev 37.67 (1991)(Commodore)
    # (Disk 1 of 4)(Workbench)[m4].adf
    "21a4363e236011f0173c393207a2225a0a3002b0",
    # Workbench v2.04 rev 37.67 (1991)(Commodore)
    # (Disk 1 of 4)(Workbench)[m2].adf
    "898c0c372c476d8410890388b81ca642cc0b381d",
    # Workbench v2.04 rev 37.67 (1991)(Commodore)
    # (Disk 1 of 4)(Workbench)[m3].adf
    "5913fa0fb6cfa74ae9c80870f6ab8a4289036788",
    # amiga-os-204-workbench.adf
    "898c0c372c476d8410890388b81ca642cc0b381d",
]


wb_300_floppies = [
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[!].adf
    "e663c92a9c88fa38d02bbb299bea8ce70c56b417",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[m2].adf
    "cf2f24cf5f5065479476a38ec8f1016b1f746884",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[m5].adf
    "4f4770caae5950eca4a2720e0424df052ced6a32",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[a].adf
    "9496daa66e6b2f4ddde4fa2580bb3983a25e3cd2",
    # Workbench v3.0 rev 39.29 (1992)(Commodore)(A1200-A4000)(M10)
    # (Disk 2 of 6)(Workbench)[m3].adf
    "0e7f30223af254df0e2b91ea409f35c56d6164a6",
    # amiga-os-300-workbench.adf
    "4f4770caae5950eca4a2720e0424df052ced6a32",
]


def update_files():
    base_dir = os.path.expanduser("~/Documents/FS-UAE/Floppies/Workbench")
    # floppies = {}
    floppy_file_sets = {}
    files = {}
    for floppy in os.listdir(base_dir):
        if not floppy.lower().endswith(".adf"):
            continue
        path = os.path.join(base_dir, floppy)
        with open(path, "rb") as f:
            floppy_sha1 = hashlib.sha1(f.read()).hexdigest()
        sha1sums = set()
        try:
            adf = ADFFile(path)
        except Exception:
            print("error parsing", path)
            traceback.print_exc()
            continue
        names = adf.namelist()
        for name in names:
            if name.endswith("/"):
                continue
            data = adf.open(name, "r").read()
            sha1 = hashlib.sha1(data).hexdigest()
            sha1sums.add(sha1)
            # floppies[floppy.lower()] = os.path.join(base_dir, floppy)
            files.setdefault(sha1, set()).add((floppy_sha1, name))
        floppy_file_sets[(floppy, floppy_sha1)] = sha1sums

    interesting_files = set()
    for file_map in [wb_204_files, wb_300_files]:
        for name, sha1 in file_map.items():
            if sha1:
                interesting_files.add(sha1)

    # print("")
    # print("workbench_file_map = {")
    # for sha1 in sorted(interesting_files):
    #     print("    \"{0}\": [".format(sha1))
    #     #print("        \"{0}\",".format(floppy_sha1))
    #     for floppy_sha1, name in sorted(files[sha1]):
    #         #print("        \"{0}\",".format(floppy_sha1))
    #         print("        (\"{0}\", \"{1}\"),".format(floppy_sha1, name))
    #     print("    ],")
    # print("}")
    # print("")

    for name, file_map in [
            ("wb_133_floppies", wb_133_files),
            ("wb_204_floppies", wb_204_files),
            ("wb_300_floppies", wb_300_files)]:
        print("\n" + name + " = [")
        file_set = set([x for x in file_map.values() if x])
        for floppy_data, floppy_file_set in floppy_file_sets.items():
            floppy_name, floppy_sha1 = floppy_data
            if floppy_file_set.issuperset(file_set):
                print("    # {0}".format(floppy_name))
                print("    \"{0}\",".format(floppy_sha1))
        print("]")


def main():
    if sys.argv[1] == "--update-files":
        update_files()
        return

    base_dir = os.path.expanduser("~/Documents/FS-UAE/Floppies/Workbench")
    floppies = {}
    for floppy in os.listdir(base_dir):
        if not floppy.lower().endswith(".adf"):
            continue
        floppies[floppy.lower()] = os.path.join(base_dir, floppy)

    floppy = floppies[sys.argv[1].lower()]
    adf = ADFFile(floppy)
    names = adf.namelist()
    startup_sequence = ""
    for name in names:
        if name.lower() == "s/startup-sequence":
            startup_sequence = adf.open(name, "r").read()
            continue
        if name.endswith(".info"):
            continue
        if name.endswith("/"):
            sha1 = ""
        else:
            data = adf.open(name, "r").read()
            sha1 = hashlib.sha1(data).hexdigest()
        if sha1:
            if len(name) > (80 - 4 - 2 - 1 - 2 - 2 - 40):
                print("    \"{0}\":\n    \"{1}\",".format(name, sha1))
            else:
                print("    \"{0}\": \"{1}\",".format(name, sha1))
        else:
            print("    \"{0}\": \"\",".format(name))
    print("")
    print(startup_sequence)


if __name__ == "__main__":
    main()

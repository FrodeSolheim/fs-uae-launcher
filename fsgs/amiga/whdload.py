DEFAULT_WHDLOAD_VERSION = "18.2"

# noinspection SpellCheckingInspection
whdload_support_files = {
    "1d1c557f4a0f5ea88aeb96d68b09f41990340f70":
        "Devs/Kickstarts/kick33180.A500.RTB",
    "1ad1b55e7226bd5cd66def8370a69f19244da796":
        "Devs/Kickstarts/kick40068.A1200.RTB",
    "209c109855f94c935439b60950d049527d2f2484":
        "Devs/Kickstarts/kick34005.A500.RTB",
    "973b42dcaf8d6cb111484b3c4d3b719b15f6792d":
        "Devs/Kickstarts/kick40068.A4000.RTB",
    "09e4d8a055b4a9801c6b011e7a3de42bafaf070d":
        "C/uae-configuration",
    "3b40b7277f0408ebb98526205748138f88d84330":
        "C/OSEmu.400",
}

# noinspection SpellCheckingInspection
whdload_files = {
    "10.0": {
        "3096b2f41dfebf490aac015bdf0e91a80045c2c0": "C/WHDLoad",
    },
    "13.0": {
        "4bcb393e820d68b0520da9131e0d529018e303d1": "C/WHDLoad",
    },
    "16.0": {
        "883b9e37bc81fc081f78a3f278b732f97bdddf5c": "C/WHDLoad",
    },
    "16.1": {
        "250506c2444d9fb89b711b4fba5d70dd554e6f0e": "C/WHDLoad",
    },
    "16.2": {
        "a8bc2828c7da88f6236a8e82c763c71582f66cfd": "C/WHDLoad",
    },
    "16.3": {
        "5d636899fa9332b7dfccd49df3447238b5b71e49": "C/WHDLoad",
    },
    "16.4": {
        "1bb42fc83ee9237a6cfffdf15a3eb730504c9f65": "C/WHDLoad",
    },
    "16.5": {
        "8974e6c828ac18ff1cc29e56a31da0775ddeb0f0": "C/WHDLoad",
    },
    "16.6": {
        "b268bf7a05630d5b2bbf99616b32f282bac997bf": "C/WHDLoad",
    },
    "16.7": {
        "be94bc3d70d5980fac7fd04df996120e8220c1c0": "C/WHDLoad",
    },
    "16.8": {
        "a3286827c821386ac6e0bb519a7df807550d6a70": "C/WHDLoad",
    },
    "16.9": {
        "b4267a21918d6375e1bbdcaee0bc8b812e366802": "C/WHDLoad",
    },
    "17.0": {
        "0ec213a8c62beb3eb3b3509aaa44f21405929fce": "C/WHDLoad",
    },
    "17.1": {
        "1a907ca4539806b42ad5b6f7aeebacb3720e840d": "C/WHDLoad",
    },
    "2013-03-01": {
        "7ee8516eceb9e799295f1b16909749d08f13d26c": "C/WHDLoad",
    },
    "17.2": {
        "d8f45f7808fb1ac356d88b8848660a6b96f04349": "C/WHDLoad",
    },
    "18.0": {
        "6f778e28673e9f931f81212ab03d9617a41cee40": "C/WHDLoad",
    },
    "18.1": {
        "fb4c64b0b5e682125e53eb2ace9bf0ccd3b8501f": "C/WHDLoad",
    },
    "18.2": {
        "0a9e7bfa1183420543e44c08410af1c5500fa704": "C/WHDLoad",
    },
}

default_whdload_prefs = """
; wait for button pressed (slave must support this)
;ButtonWait

; disable cache-ability of Chip-Memory
;ChipNoCache

; path for core dump files
;CoreDumpPath=T:

; raw key code to quit with core dump (debug)
;DebugKey=$5b

; command to execute on WHDLoad startup
;ExecuteStartup=rx offline.rexx

; command to execute on WHDLoad exit
;ExecuteCleanup=rx online.rexx

; selects expert mode
;Expert

; raw key code to enter HrtMon/TK
;FreezeKey=$5d

; use MMU (for 68030)
;MMU

; ignore unwanted auto-vector interrupts
;NoAutoVec

; disable audio filter
;NoFilter

; do not flush memory
;NoFlushMem

; do not allocate memory reverse
;NoMemReverse

; disable the disk write cache
;NoWriteCache

;QuitKey=$45

; wait after reading from disk (1/50 seconds)
;ReadDelay=150

; raw key code to restart
;RestartKey=$5c

; command for Show Regs
;ShowRegs=SYS:Utilities/MuchMore W WL=80 WT=80 WW=582 WH=700

; time to display splash window (1/50 seconds)
;SplashDelay=0

; wait after saving something to disk (1/50 seconds)
;WriteDelay=150
"""

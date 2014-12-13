[Setup]
AppName=FS-UAE Launcher
AppVersion=9.8.7
AppVerName=FS-UAE Launcher 9.8.7
DefaultDirName={localappdata}\fs-uae-launcher
DefaultGroupName=FS-UAE
UninstallDisplayIcon={app}\fs-uae-launcher.exe
OutputBaseFilename=fs-uae-launcher_9.8.7_windows
OutputDir=..
PrivilegesRequired=lowest
ShowLanguageDialog=no
DisableDirPage=yes
; DisableWelcomePage=yes
DisableReadyPage=yes
DisableStartupPrompt=yes
DisableProgramGroupPage=yes

[Files]
Source: "fs-uae-launcher_9.8.7_windows\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion;

[installDelete]
Type: files; Name: "{userprograms}\FS-UAE\FS-UAE Emulator.lnk"
Type: filesandordirs; Name: "{app}\FS-UAE"

[Icons]
Name: "{group}\FS-UAE Launcher"; Filename: "{app}\fs-uae-launcher.exe"

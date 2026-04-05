[Setup]
DisableWelcomePage=no
DisableDirPage=no
WizardImageFile=C:\Users\User\Documents\ProgramList_PY\assets\ps1.bmp
AppName=Родительский Лаунчер
AppVersion=1.0
AppPublisher=Alex Skornyakov
AppPublisherURL=https://github.com/VortexCodeRU
AppSupportURL=https://github.com/VortexCodeRU
AppUpdatesURL=https://github.com/VortexCodeRU
DefaultDirName={autopf}\Родительский Лаунчер
DefaultGroupName=Родительский Лаунчер
OutputDir=Output
OutputBaseFilename=ParentLauncher_Setup
SetupIconFile=C:\Users\User\Documents\ProgramList_PY\assets\photo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Files]
Source: "C:\Users\User\Documents\ProgramList_PY\dist\ParentLauncher.exe"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Родительский Лаунчер"; Filename: "{app}\ParentLauncher.exe"
Name: "{commondesktop}\Родительский Лаунчер"; Filename: "{app}\ParentLauncher.exe"

[Run]
Filename: "{app}\ParentLauncher.exe"; Description: "Запустить Родительский Лаунчер"; Flags: nowait postinstall skipifsilent
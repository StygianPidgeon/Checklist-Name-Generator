[Setup]
AppName=Checklist Name Generator (no OCR)
AppVersion=1.0.1
AppPublisher=Dawn Holley
DefaultDirName={localappdata}\Checklist Name Generator
DefaultGroupName=Checklist Name Generator
OutputDir=Output
OutputBaseFilename=Checklist Name Generator Setup (no OCR)
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=dh.ico
PrivilegesRequired=lowest

[Files]
;Everything in _internal except Poppler
Source: "dist\checklist name generator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "dist\checklist name generator\_internal\Poppler\*,dist\checklist name generator\_internal\Tesseract-OCR\*"
;Optional Poppler
Source: "dist\checklist name generator\_internal\Poppler\*"; DestDir: "{app}\Poppler"; Flags: ignoreversion recursesubdirs createallsubdirs; Tasks: firsttimeonly\installpoppler

[Icons]
Name: "{group}\Checklist Name Generator"; Filename: "{app}\checklist name generator.exe"
Name: "{autodesktop}\Checklist Name Generator"; Filename: "{app}\checklist name generator.exe"; Tasks: desktopicon

[Tasks]
Name: "firsttimeonly"; Description: "First time install"

Name: "firsttimeonly\installpoppler"; Description: "Install Poppler"

Name: "desktopicon"; Description: "Create a desktop shortcut"

[Run]
Filename: "{app}\checklist name generator.exe"; Description: "Launch Checklist Name Generator"; Flags: nowait postinstall skipifsilent
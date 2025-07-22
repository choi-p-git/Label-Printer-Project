[Setup]
AppName=Label Parser
AppVersion=1.0
DefaultDirName={localappdata}\LabelPrinter
DefaultGroupName=Label Parser
UninstallDisplayIcon={app}\label_parser.exe
OutputDir=.
OutputBaseFilename=LabelParserSetup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
DisableWelcomePage=no

[Files]
Source: "dist\label_parser.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\label_parser\_internal\pymupdf\*.pyd"; DestDir: "{app}\pymupdf"; Flags: ignoreversion
Source: "dist\label_parser\_internal\pymupdf\*.dll"; DestDir: "{app}\pymupdf"; Flags: ignoreversion
Source: "dist\config.ini"; DestDir: "{app}"; Flags: ignoreversion
Source: "Label Library\*"; DestDir: "{localappdata}\LabelPrinter\Label Library"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "SumatraPDF\*"; DestDir: "{localappdata}\LabelPrinter\SumatraPDF"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Label Parser"; Filename: "{app}\label_parser.exe"
Name: "{userdesktop}\Label Parser"; Filename: "{app}\label_parser.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\label_parser.exe"; Description: "Launch Label Parser"; Flags: nowait postinstall skipifsilent

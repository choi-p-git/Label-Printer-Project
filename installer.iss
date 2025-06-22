; installer.iss – Barcode Label Printer Installer (User-Local Install)
#define MyAppName "Label Printer"

[Setup]
AppName=Label Printer
AppVersion=0.1.5
DefaultDirName={localappdata}\LabelPrinter
DefaultGroupName=Label Printer
OutputDir=dist
OutputBaseFilename=LabelPrinterInstaller
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
ArchitecturesInstallIn64BitMode=x64
AllowNoIcons=yes
UninstallDisplayIcon={app}\LabelPrinter.exe

[Files]
; Main PyInstaller output
Source: "dist\LabelPrinter\*"; DestDir: "{app}"; Flags: recursesubdirs

; config.ini – Only installed if not already present
Source: "config.ini"; DestDir: "{app}"; Flags: onlyifdoesntexist

; SumatraPDF portable executable – installed in local appdata
Source: "SumatraPDF\SumatraPDF-3.5.2-64.exe"; DestDir: "{localappdata}\LabelPrinter\SumatraPDF"; Flags: ignoreversion

; Brother Printer Driver Installer – optional
Source: "Brother_Driver\D_SETUP.exe"; DestDir: "{tmp}\BrotherDriver"; Flags: recursesubdirs

[Dirs]
; Label Library folder (writable by user)
Name: "{localappdata}\LabelPrinter\Label Library"

[Icons]
Name: "{group}\Label Printer"; Filename: "{app}\LabelPrinter.exe"
Name: "{userdesktop}\Label Printer"; Filename: "{app}\LabelPrinter.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"

[Run]
; Optional: Launch Label Printer on install
Filename: "{app}\LabelPrinter.exe"; Description: "Launch Barcode Label Printer"; Flags: nowait postinstall skipifsilent

; Optional: Prompt driver installation
Filename: "{tmp}\BrotherDriver\setup.exe"; Description: "Install Brother TD-4000 Driver (Optional)"; \
    Flags: postinstall runascurrentuser unchecked shellexec; \
    StatusMsg: "Preparing Brother TD-4000 Driver Setup..."

[Registry]
; Uninstall path tracking
Root: HKCU; Subkey: "Software\LabelPrinter"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"

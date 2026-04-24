#define MyAppName "YouTube Video & MP3 Downloader"
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Company"
#define MyAppExeName "YouTubeDownloader.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{3B4F3A5A-E36D-4E11-9A82-840DE00B8D49}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\YouTubeDownloader
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Install for current user (no admin rights required)
PrivilegesRequired=lowest
OutputDir=.\InstallerOutput
OutputBaseFilename=YouTubeDownloader_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; IMPORTANT: Source path is relative to where this .iss file is located
Source: "dist\YouTubeDownloader\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\YouTubeDownloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

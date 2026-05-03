' Launches Poor Man's Beier (web UI) without showing a console window.
Set s = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
here = fso.GetParentFolderName(WScript.ScriptFullName)
s.CurrentDirectory = here
s.Run "python """ & here & "\flasher_server.py""", 0, False

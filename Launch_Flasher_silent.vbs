' Launches Poor Man's Beier (web UI) without ever showing a console window.
' Uses pythonw.exe (windowless Python) so nothing pops up in the taskbar.
Set s   = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
here = fso.GetParentFolderName(WScript.ScriptFullName)
s.CurrentDirectory = here

' Try pythonw first (no console). Fall back to python with hidden window.
On Error Resume Next
s.Run "pythonw """ & here & "\flasher_server.py""", 0, False
If Err.Number <> 0 Then
  Err.Clear
  s.Run "python """ & here & "\flasher_server.py""", 0, False
End If

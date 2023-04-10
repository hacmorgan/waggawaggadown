cd C:\Users\Emily\src\abyss\waggawaggadown\wwd
python3 -m pip install --upgrade ..
clear
python3 .\main.py
$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');

# To make double clickable shortcut to this script, make the shortcut target this:
# powershell.exe -command "& 'C:\Users\Emily\src\abyss\waggawaggadown\tools\RUN.ps1'"
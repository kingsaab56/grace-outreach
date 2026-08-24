@echo off
taskkill /F /IM cloudflared.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
echo ? Server aur Tunnel band ho gaye hain.
pause

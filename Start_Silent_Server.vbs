Set WshShell = CreateObject("WScript.Shell")
' 1. Start Python Web Portal Silently in Background
WshShell.Run "python web_portal.py", 0, False

' 2. Start Cloudflare HTTPS Tunnel Silently in Background
WshShell.Run "powershell -WindowStyle Hidden -Command "".\cloudflared.exe tunnel --url http://localhost:8501""", 0, False

MsgBox "🚀 Grace Outreach Server & HTTPS Tunnel background mein start ho gaye hain!", 64, "Grace Server Active"

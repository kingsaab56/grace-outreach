# Cloudflare HTTPS Quick Tunnel Launcher for Grace Outreach
$tunnelUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
$dest = ".\cloudflared.exe"

if (-Not (Test-Path $dest)) {
    Write-Host "Downloading Secure HTTPS Tunnel Engine..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $tunnelUrl -OutFile $dest
}

Write-Host "`n=======================================================" -ForegroundColor Green
Write-Host " Starting Secure HTTPS Global Access for Colleagues... " -ForegroundColor Green
Write-Host "=======================================================`n" -ForegroundColor Green

.\cloudflared.exe tunnel --url http://localhost:8501

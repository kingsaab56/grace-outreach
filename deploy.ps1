Write-Host "🚀 Auto-Building and Deploying to Railway Cloud..." -ForegroundColor Cyan

# 1. Update/Generate code
python apply_settings_audio.py

# 2. Direct Push to Railway without manual prompts
.\railway.exe up --detach

Write-Host "✔ Deployed successfully to Cloud 24/7!" -ForegroundColor Green
Write-Host "👉 Live Link: https://heartfelt-nourishment-production-5c03.up.railway.app" -ForegroundColor Yellow

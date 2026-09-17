@echo off
title Grace Outreach Assistant - Enterprise Portal
color 0A
cd /d "E:\Grace Outreach Assistant"
echo =======================================================
echo     Grace Outreach Assistant Enterprise V5
echo             Developed by King Saab
echo =======================================================
echo Starting Grace Assistant Engine on Port 8080...
start "" http://localhost:8080/api/?tab=matrix
python main.py
pause

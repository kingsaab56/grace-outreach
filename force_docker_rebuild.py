import os
import time

stamp = str(int(time.time()))

# 1. Update Dockerfile to force Railway to re-read everything without cache
dockerfile_content = f"""FROM python:3.11-slim
WORKDIR /app
# Build bust stamp: {stamp}
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
ENV BUILD_VERSION={stamp}
CMD ["python", "web_portal.py"]
"""

with open("Dockerfile", "w", encoding="utf-8", newline='\n') as f:
    f.write(dockerfile_content)

print(f"✔ Dockerfile updated with unique build tag: {stamp}")

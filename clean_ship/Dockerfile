FROM python:3.11-slim
WORKDIR /app
# Build bust stamp: 1787560874
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
ENV BUILD_VERSION=1787560874
CMD ["python", "web_portal.py"]

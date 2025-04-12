FROM python:3.12-slim

# 필수 패키지 설치 (Chrome & 드라이버 포함)
RUN apt-get update && apt-get install -y \
    curl unzip gnupg \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 \
    libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 xdg-utils lsb-release \
    chromium chromium-driver \
    && apt-get clean

# 환경 변수 설정
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# Streamlit 포트
EXPOSE 8501

# 실행 명령
CMD ["streamlit", "run", "app.py", "--server.headless=true", "--server.port=8501", "--server.enableCORS=false"]
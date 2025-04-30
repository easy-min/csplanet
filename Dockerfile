# 1) 베이스 이미지
FROM python:3.11-slim

# 2) 환경 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3) 작업 디렉터리
WORKDIR /app

# 4) 시스템 패키지 설치 (PostgreSQL, 빌드용)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# 5) requirements 복사 및 설치
COPY requirements/base.txt requirements/
COPY requirements/local.txt requirements/
RUN pip install --upgrade pip \
 && pip install -r requirements/base.txt -r requirements/local.txt

# 6) 애플리케이션 코드 복사
COPY . .

# 7) 정적 파일 수집
RUN python manage.py collectstatic --noinput

# 8) Gunicorn으로 서비스 기동
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

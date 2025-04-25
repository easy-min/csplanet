# 1) 베이스 이미지: Python 3.11 슬림
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

# 2) .pyc 생성 방지, stdout/stderr 버퍼링 해제
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3) 작업 디렉터리 생성 및 설정
WORKDIR /app

# 4) 의존성 캐시를 위해 requirements만 먼저 복사
COPY requirements/base.txt requirements/
COPY requirements/local.txt requirements/

# 5) 시스템 패키지와 파이썬 패키지 설치
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev \
 && pip install --upgrade pip \
 && pip install -r requirements/base.txt -r requirements/local.txt \
 && apt-get purge -y --auto-remove gcc \
 && rm -rf /var/lib/apt/lists/*

# 6) 나머지 애플리케이션 코드 복사
COPY . .

# 7) 정적 파일 수집
RUN python manage.py collectstatic --noinput

# 8) Gunicorn으로 WSGI 앱 구동
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

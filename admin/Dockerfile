# Python 3.12를 기반으로 한 슬림 이미지 사용
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# pyproject.toml 복사 및 의존성 설치
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install .

# 애플리케이션 코드 복사
COPY . .

# static 파일 수집을 위한 디렉토리 생성
RUN mkdir -p /app/staticfiles

# 비root 사용자 생성 및 권한 설정
RUN useradd --create-home --shell /bin/bash django && \
    chown -R django:django /app
USER django

# 포트 노출
EXPOSE 8000

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/login/ || exit 1

# 시작 명령어 (gunicorn 사용)
CMD ["gunicorn", "--config", "gunicorn.conf.py", "myunsejeomju.wsgi:application"]
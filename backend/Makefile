# 뮨세점주 백엔드 Makefile
# 테스트, 개발, 배포 관련 작업을 자동화합니다.

# 변수 정의
PYTHON := uv run python
PYTEST := uv run pytest
MANAGE := $(PYTHON) manage.py
PROJECT_NAME := myunsejeomju-backend

# 기본 설정
.DEFAULT_GOAL := help
.PHONY: help install test lint format clean dev build docker

# 도움말 표시
help: ## 사용 가능한 명령어 목록을 표시합니다
	@echo "$(PROJECT_NAME) - 사용 가능한 명령어:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo

# 개발 환경 설정
install: ## 프로젝트 의존성을 설치합니다
	@echo "📦 의존성 설치 중..."
	uv sync --frozen
	@echo "✅ 의존성 설치 완료!"

install-dev: ## 개발용 의존성을 포함하여 설치합니다
	@echo "📦 개발용 의존성 설치 중..."
	uv sync --frozen --extra dev --extra test
	@echo "✅ 개발용 의존성 설치 완료!"

install-test-deps: ## 테스트 의존성만 설치합니다
	@echo "📦 테스트 의존성 설치 중..."
	uv sync --frozen --extra test
	@echo "✅ 테스트 의존성 설치 완료!"

# 데이터베이스 관련
migrate: ## 데이터베이스 마이그레이션을 실행합니다
	@echo "🔄 데이터베이스 마이그레이션 실행 중..."
	$(MANAGE) migrate
	@echo "✅ 마이그레이션 완료!"

makemigrations: ## 새로운 마이그레이션을 생성합니다
	@echo "📝 마이그레이션 파일 생성 중..."
	$(MANAGE) makemigrations
	@echo "✅ 마이그레이션 파일 생성 완료!"

seed: ## 테스트용 데이터를 생성합니다
	@echo "🌱 시드 데이터 생성 중..."
	$(MANAGE) seed_data
	$(MANAGE) seed_tables
	@echo "✅ 시드 데이터 생성 완료!"

# 테스트 관련
test: install-test-deps ## 모든 테스트를 실행합니다
	@echo "🧪 전체 테스트 실행 중..."
	$(PYTEST) -v
	@echo "✅ 테스트 완료!"

test-unit: install-test-deps ## 단위 테스트만 실행합니다
	@echo "🔧 단위 테스트 실행 중..."
	$(PYTEST) -v -m unit
	@echo "✅ 단위 테스트 완료!"

test-integration: install-test-deps ## 통합 테스트만 실행합니다
	@echo "🔗 통합 테스트 실행 중..."
	$(PYTEST) -v -m integration
	@echo "✅ 통합 테스트 완료!"

test-concurrency: install-test-deps ## 동시성 테스트만 실행합니다
	@echo "⚡ 동시성 테스트 실행 중..."
	$(PYTEST) -v -m concurrency
	@echo "✅ 동시성 테스트 완료!"

test-fast: install-test-deps ## 빠른 테스트만 실행합니다 (slow 마커 제외)
	@echo "🚀 빠른 테스트 실행 중..."
	$(PYTEST) -v -m "not slow"
	@echo "✅ 빠른 테스트 완료!"

test-parallel: install-test-deps ## 병렬로 테스트를 실행합니다
	@echo "⚡ 병렬 테스트 실행 중..."
	$(PYTEST) -v -n auto
	@echo "✅ 병렬 테스트 완료!"

test-coverage: install-test-deps ## 코드 커버리지를 측정하며 테스트를 실행합니다
	@echo "📊 코드 커버리지 측정 중..."
	$(PYTEST) -v --cov=domain --cov=infrastructure --cov=presentation \
		--cov-report=html --cov-report=term-missing
	@echo "✅ 커버리지 리포트가 htmlcov/ 디렉토리에 생성되었습니다!"
	@echo "브라우저에서 htmlcov/index.html을 열어 확인하세요."

test-watch: install-test-deps ## 파일 변경 시 자동으로 테스트를 실행합니다
	@echo "👀 테스트 감시 모드 시작..."
	$(PYTEST) -v --looponfail

# 특정 테스트 실행
test-repo: ## Repository 테스트만 실행합니다
	@echo "🗃️ Repository 테스트 실행 중..."
	$(PYTEST) -v tests/unit/test_repositories.py
	@echo "✅ Repository 테스트 완료!"

test-usecase: ## Use Case 테스트만 실행합니다
	@echo "💼 Use Case 테스트 실행 중..."
	$(PYTEST) -v tests/unit/test_use_cases.py
	@echo "✅ Use Case 테스트 완료!"

test-api: ## API 테스트만 실행합니다
	@echo "🌐 API 테스트 실행 중..."
	$(PYTEST) -v tests/integration/test_api_orders.py
	@echo "✅ API 테스트 완료!"

# 코드 품질
lint: ## 코드 품질을 검사합니다
	@echo "🔍 코드 품질 검사 중..."
	$(PYTHON) -m flake8 domain infrastructure presentation
	@echo "✅ 린트 검사 완료!"

format: ## 코드 포맷팅을 실행합니다
	@echo "🎨 코드 포맷팅 중..."
	$(PYTHON) -m black domain infrastructure presentation tests
	$(PYTHON) -m isort domain infrastructure presentation tests
	@echo "✅ 코드 포맷팅 완료!"

type-check: ## 타입 검사를 실행합니다
	@echo "🔬 타입 검사 중..."
	$(PYTHON) -m mypy domain infrastructure presentation
	@echo "✅ 타입 검사 완료!"

# 개발 서버
dev: ## 개발 서버를 실행합니다
	@echo "🚀 개발 서버 시작..."
	$(MANAGE) runserver

dev-shell: ## Django 셸을 실행합니다
	@echo "🐚 Django 셸 시작..."
	$(MANAGE) shell

# 정리 작업
clean: ## 캐시 파일들을 정리합니다
	@echo "🧹 캐시 파일 정리 중..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "✅ 정리 완료!"

clean-db: ## SQLite 데이터베이스를 삭제합니다
	@echo "🗑️ 데이터베이스 삭제 중..."
	rm -f db.sqlite3
	@echo "✅ 데이터베이스 삭제 완료!"

reset-db: clean-db migrate seed ## 데이터베이스를 초기화하고 시드 데이터를 생성합니다
	@echo "🔄 데이터베이스 초기화 완료!"

# Docker 관련
docker-build: ## Docker 이미지를 빌드합니다
	@echo "🐳 Docker 이미지 빌드 중..."
	docker build -t $(PROJECT_NAME) .
	@echo "✅ Docker 이미지 빌드 완료!"

docker-up: ## Docker Compose로 서비스를 시작합니다
	@echo "🐳 Docker 서비스 시작 중..."
	docker-compose up -d
	@echo "✅ Docker 서비스 시작 완료!"

docker-down: ## Docker Compose 서비스를 중지합니다
	@echo "🐳 Docker 서비스 중지 중..."
	docker-compose down
	@echo "✅ Docker 서비스 중지 완료!"

docker-logs: ## Docker 서비스 로그를 확인합니다
	docker-compose logs -f

# 종합 테스트 스위트
test-all: test-unit test-integration test-concurrency ## 모든 타입의 테스트를 순차적으로 실행합니다
	@echo "🎉 전체 테스트 스위트 완료!"

# 성능 테스트
test-performance: ## 성능 관련 테스트를 실행합니다
	@echo "⚡ 성능 테스트 실행 중..."
	$(PYTEST) -v -m "slow or concurrency" --durations=10
	@echo "✅ 성능 테스트 완료!"

# 개발자 워크플로우
dev-setup: install-dev migrate seed ## 개발 환경을 완전히 설정합니다
	@echo "🎯 개발 환경 설정 완료!"
	@echo "다음 명령어로 개발 서버를 시작하세요: make dev"

# 배포 준비
build: clean format lint test ## 배포 준비를 위한 전체 빌드를 실행합니다
	@echo "🚀 빌드 완료! 배포 준비가 끝났습니다."
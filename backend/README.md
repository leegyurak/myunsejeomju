# 면세점주 백엔드 API 서버

테이블 기반 음식 주문 서비스를 위한 최신 Django REST API 백엔드 시스템으로, **클린 아키텍처** 원칙과 **도메인 주도 설계(DDD)**를 적용하여 구축되었습니다.

## 기술 스택

- **프레임워크**: Django 5.2.4 + Django REST Framework
- **데이터베이스**: MySQL 8.0
- **패키지 관리자**: uv (고속 Python 패키지 설치 도구)
- **아키텍처**: 클린 아키텍처
- **결제 연동**: Toss Deposit URL + PayAction
- **주문 알림**: Discord 웹훅 알림
- **컨테이너화**: Docker + Docker Compose

## 아키텍처 개요

이 프로젝트는 관심사의 명확한 분리와 함께 **클린 아키텍처** 원칙을 따릅니다:

```
backend/
├── domain/                     # 도메인 레이어 - 핵심 비즈니스 로직
│   ├── entities/              # 비즈니스 엔티티 (Food, Table, Order)
│   │   ├── food.py           # 음식 엔티티 (열거형, 비즈니스 규칙)
│   │   ├── table.py          # 테이블 엔티티 (UUID 기반 식별)
│   │   └── order.py          # 주문 엔티티 (상태 관리)
│   ├── repositories/          # 추상 리포지토리 인터페이스
│   │   ├── food_repository.py
│   │   ├── table_repository.py
│   │   └── order_repository.py
│   └── use_cases/            # 비즈니스 유스케이스 (애플리케이션 서비스)
│       ├── food_use_cases.py
│       ├── table_use_cases.py
│       └── order_use_cases.py
├── infrastructure/            # 인프라스트럭처 레이어 - 외부 관심사
│   ├── database/             # 데이터베이스 구현
│   │   ├── models.py        # Django ORM 모델
│   │   ├── repositories.py  # 리포지토리 구현체
│   │   ├── admin.py         # Django 관리자 설정
│   │   └── migrations/      # 데이터베이스 마이그레이션
│   └── external/            # 외부 서비스
│       └── discord_service.py # Discord 웹훅 통합
├── presentation/             # 프레젠테이션 레이어 - API 인터페이스
│   ├── api/                 # REST API 뷰
│   │   ├── views.py        # API 엔드포인트 구현
│   │   └── urls.py         # URL 라우팅 설정
│   └── serializers/         # 데이터 직렬화
│       ├── food_serializers.py
│       ├── table_serializers.py
│       └── order_serializers.py
└── myunsejeomju/           # Django 프로젝트 설정
    ├── settings.py         # 애플리케이션 설정
    ├── urls.py            # 메인 URL 설정
    ├── wsgi.py           # WSGI 애플리케이션
    └── asgi.py           # ASGI 애플리케이션 (향후 WebSocket 지원)
```

### 레이어 의존성

```
프레젠테이션 레이어
        ↓
    유스케이스  
        ↓
   도메인 엔티티
        ↑
인프라스트럭처 레이어
```

## 핵심 기능

### 1. 테이블 관리 시스템
- **UUID 기반 식별자**를 통한 안전한 테이블 접근
- **동적 테이블 생성** 및 고유 식별자 할당
- **테이블별 주문 추적** 및 이력 관리

### 2. 주문 처리 시스템
- **실시간 주문 생성** (원자적 트랜잭션)
- **선주문 시스템** 및 결제 연동
- **주문 상태 관리**: `pre_order` → `completed`
- **주문 이력 추적** 및 총 지출액 계산

### 3. 음식 카탈로그 관리
- **카테고리 기반 분류**: `menu`(메뉴), `drinks`(음료)
- **재고 관리** 및 품절 상태 추적
- **동적 가격 책정** (주문 시점 가격 고정)

### 4. 결제 연동
- **SuperToss API 통합** 모바일 결제
- **PayAction 웹훅** 실시간 결제 알림
- **자동 주문 상태 업데이트** (결제 완료 시)

### 5. 외부 서비스 연동
- **Discord 알림** (주문 완료 시)
- **웹훅 기반 결제 처리** (안정성 보장)

## REST API 엔드포인트

### 음식 관리
```http
GET    /api/foods/                     # 전체 음식 목록 조회
GET    /api/foods/?category=menu       # 카테고리별 필터링
GET    /api/foods/{food_id}/           # 특정 음식 상세 정보
```

### 테이블 관리
```http
GET    /api/tables/                    # 전체 테이블 목록
POST   /api/tables/create/             # 새 테이블 생성 (UUID 반환)
GET    /api/tables/{table_id}/         # 테이블 상세 정보
GET    /api/tables/{table_id}/orders/  # 테이블별 주문 이력
DELETE /api/tables/{table_id}/orders/reset/  # 테이블 주문 초기화
```

### 주문 처리
```http
POST   /api/orders/                    # 일반 주문 생성
GET    /api/orders/history/            # 전체 주문 이력
GET    /api/orders/history/?table_id=  # 테이블별 주문 필터링
POST   /api/orders/pre-order/{table_id}/    # 선주문 생성 (결제 연동)
GET    /api/orders/{order_id}/payment-status/  # 결제 상태 확인
```

### 웹훅 엔드포인트
```http
POST   /api/webhook/payment/           # PayAction 결제 웹훅
```

## 데이터 모델

### 음식 모델
```python
class FoodModel:
    name: str                    # 음식명
    price: int                   # 가격 (원)
    category: str               # 'menu' 또는 'drinks'
    description: str            # 설명 (선택사항)
    image: str                  # 이미지 URL (선택사항)
    sold_out: bool             # 품절 여부
```

### 테이블 모델
```python
class TableModel:
    id: UUID                    # 기본키 (UUID4)
    name: str                   # 테이블명 (선택사항)
    created_at: datetime        # 생성 시각
```

### 주문 모델
```python
class OrderModel:
    id: UUID                    # 기본키 (UUID4)
    table: TableModel          # 테이블 외래키
    status: str                # 'pre_order' 또는 'completed'
    payer_name: str           # 결제자명
    pre_order_amount: int     # 선주문 총액 (선주문용)
    order_date: datetime      # 주문 시각
    discord_notified: bool    # 알림 전송 여부
```

## 요청/응답 예시

### 일반 주문 생성
```json
POST /api/orders/
Content-Type: application/json

{
  "table_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": [
    {"food_id": 1, "quantity": 2},
    {"food_id": 7, "quantity": 1}
  ]
}
```

**응답:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "table": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "total_amount": 25000,
  "items": [
    {
      "food": {"id": 1, "name": "비빔밥", "price": 12000},
      "quantity": 2,
      "total_price": 24000
    }
  ]
}
```

### 선주문 생성 (결제 연동)
```json
POST /api/orders/pre-order/550e8400-e29b-41d4-a716-446655440000/
Content-Type: application/json

{
  "payer_name": "홍길동",
  "total_amount": 15000,
  "items": [
    {"food_id": 3, "quantity": 1},
    {"food_id": 8, "quantity": 2}
  ]
}
```

**응답:**
```json
{
  "order_id": "789e0123-e45b-67c8-d901-234567890123",
  "redirect_url": "supertoss://send?amount=15000&bank=%EC%BC%80%EC%9D%B4%EB%B1%85%ED%81%AC&accountNo=100148347666&origin=qr",
  "message": "선주문이 성공적으로 생성되었습니다. 결제 URL로 리다이렉트 해주세요."
}
```

## 환경 설정

### 필수 요구사항
- Python 3.12+
- uv 패키지 관리자
- MySQL 8.0 (운영환경용)

### 설치 방법

1. **프로젝트 클론 및 설정:**
```bash
cd backend
uv sync --frozen
```

2. **환경 변수 설정:**
```bash
cp .env.example .env
# .env 파일을 수정하여 환경에 맞게 설정
```

3. **데이터베이스 설정:**
```bash
# 마이그레이션 적용
uv run python manage.py migrate

# 초기 데이터 생성
uv run python manage.py seed_data     # 음식 데이터
uv run python manage.py seed_tables   # 테스트 테이블 (A1-A5, B1-B5, C1-C5)
```

4. **개발 서버 실행:**
```bash
uv run python manage.py runserver
# 서버가 http://127.0.0.1:8000 에서 실행됩니다
```

## Docker 배포

### 개발 환경
```bash
docker-compose up --build
```

### 운영 환경 변수
```env
# Django 설정
SECRET_KEY=운영용-비밀키
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 데이터베이스 설정
DB_NAME=myunsejeomju_db
DB_USER=myunsejeomju_user
DB_PASSWORD=안전한_비밀번호
DB_HOST=db
DB_PORT=3306

# 외부 서비스
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 비즈니스 로직 흐름

### 일반 주문 흐름
1. 클라이언트가 `table_id`와 `items`로 주문 요청 전송
2. 시스템이 테이블 존재 여부와 음식 재고 확인
3. `completed` 상태로 주문 생성
4. 주문 상세 정보와 총액을 포함한 응답 반환

### 선주문 흐름
1. 클라이언트가 결제 정보와 함께 선주문 생성
2. 시스템이 SuperToss 결제 URL 생성
3. 클라이언트가 결제 앱으로 리다이렉트
4. PayAction 웹훅이 결제 완료 알림
5. 시스템이 주문 상태를 `completed`로 업데이트
6. 식당에 Discord 알림 전송

### 결제 웹훅 처리
1. PayAction이 `/api/webhook/payment/`로 POST 요청 전송
2. 시스템이 웹훅 데이터 검증 및 결제 정보 추출
3. `payer_name`과 `amount`로 매칭되는 선주문 검색
4. 주문 상태를 `pre_order`에서 `completed`로 업데이트
5. 결제 기록을 데이터베이스에 저장

## 테스트

### 자동화된 테스트 실행 (Makefile 사용)

#### 전체 테스트 실행
```bash
# 모든 테스트 실행
make test

# 전체 테스트 스위트 (모든 타입 순차 실행)
make test-all
```

#### 테스트 타입별 실행
```bash
# 단위 테스트만 실행
make test-unit

# 통합 테스트만 실행  
make test-integration

# 동시성 테스트만 실행
make test-concurrency

# 빠른 테스트만 실행 (slow 마커 제외)
make test-fast

# 성능 테스트 실행
make test-performance
```

#### 특정 레이어별 테스트
```bash
# Repository 레이어 테스트
make test-repo

# Use Case 레이어 테스트
make test-usecase

# API 엔드포인트 테스트
make test-api
```

#### 고급 테스트 옵션
```bash
# 코드 커버리지 측정
make test-coverage

# 병렬 실행으로 속도 향상
make test-parallel

# 파일 변경 시 자동 테스트 실행
make test-watch
```

#### 개발 워크플로우
```bash
# 개발 환경 완전 설정 (설치 + 마이그레이션 + 시드 데이터)
make dev-setup

# 커밋 전 검사 (포맷팅 + 린트 + 빠른 테스트)
make pre-commit

# CI 파이프라인 (설치 + 테스트 + 린트)
make ci

# 개발 서버 실행
make dev
```

#### 데이터베이스 관리
```bash
# 마이그레이션 실행
make migrate

# 시드 데이터 생성
make seed

# 데이터베이스 초기화
make reset-db
```

#### 코드 품질 관리
```bash
# 코드 포맷팅
make format

# 린트 검사
make lint

# 타입 검사
make type-check
```

#### 사용 가능한 모든 명령어 확인
```bash
# 도움말 표시
make help
```

### 테스트 구조

```
tests/
├── unit/                    # 단위 테스트
│   ├── test_repositories.py # Repository 레이어 테스트
│   └── test_use_cases.py   # Use Case 레이어 테스트
├── integration/            # 통합 테스트
│   ├── test_concurrency.py # 동시성 제어 테스트
│   └── test_api_orders.py  # API 엔드포인트 테스트
└── factories/              # 테스트 데이터 팩토리
    ├── model_factories.py  # Django 모델 팩토리
    └── entity_factories.py # 도메인 엔티티 팩토리
```

### 테스트 마커

- `@pytest.mark.unit`: 단위 테스트 (빠름, 외부 의존성 없음)
- `@pytest.mark.integration`: 통합 테스트 (DB 사용)
- `@pytest.mark.concurrency`: 동시성 테스트 (멀티스레드)
- `@pytest.mark.slow`: 시간이 오래 걸리는 테스트
- `@pytest.mark.database`: 데이터베이스가 필요한 테스트

### 동시성 테스트 중점 사항

1. **품절 상품 동시 주문 방지**: 여러 사용자가 동시에 품절된 음식을 주문할 때 모든 요청이 적절히 거부되는지 확인
2. **Race Condition 방지**: SELECT FOR UPDATE를 통한 데이터베이스 락이 올바르게 작동하는지 검증
3. **트랜잭션 격리**: 트랜잭션 경계에서 데이터 일관성이 유지되는지 확인

### API 수동 테스트
```bash
# 전체 음식 조회
curl -X GET http://localhost:8000/api/foods/

# 새 테이블 생성
curl -X POST http://localhost:8000/api/tables/create/

# 주문 생성
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"table_id":"테이블-아이디","items":[{"food_id":1,"quantity":2}]}'
```

## 성능 고려사항

- **데이터베이스 인덱싱** - 자주 조회되는 필드(table_id, order_date)에 인덱스 적용
- **원자적 트랜잭션** - 주문 생성 시 데이터 일관성 보장
- **효율적인 직렬화** - DRF를 통한 빠른 API 응답
- **연결 풀링** - 운영환경에서 데이터베이스 연결 최적화

## 보안 기능

- **UUID 기반 식별** - 열거 공격(enumeration attack) 방지
- **CORS 설정** - 교차 출처 요청 제한
- **입력 검증** - DRF 직렬화를 통한 데이터 유효성 검사
- **환경 변수** - 민감한 정보의 안전한 설정

## 모니터링 및 로깅

- **Discord 알림** - 실시간 주문 모니터링
- **헬스체크 엔드포인트** - 컨테이너 오케스트레이션용

## 프로젝트 특징

### 클린 아키텍처 적용
- **의존성 역전**: 인터페이스를 통한 느슨한 결합
- **단일 책임 원칙**: 각 레이어별 명확한 책임 분리
- **테스트 용이성**: 비즈니스 로직과 인프라 분리로 테스트 편의성 향상

### 확장성 고려사항
- **모듈러 설계**: 새로운 기능 추가 시 기존 코드 영향 최소화
- **인터페이스 분리**: 구현체 변경 시 유연성 확보
- **설정 외부화**: 환경별 설정 분리로 배포 유연성 향상
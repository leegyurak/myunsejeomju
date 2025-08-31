# Festival Backend

Django + DRF + Clean Architecture를 사용한 축제 음식 주문 시스템 백엔드 (테이블 단위 주문)

## 프로젝트 구조

```
backend/
├── domain/                 # 도메인 레이어 (비즈니스 로직)
│   ├── entities/          # 엔티티 (Food, Table, Order)
│   ├── repositories/      # 리포지토리 인터페이스
│   └── use_cases/         # 유즈케이스
├── infrastructure/        # 인프라스트럭처 레이어
│   └── database/         # Django 모델 및 리포지토리 구현
├── application/          # 애플리케이션 레이어
├── presentation/         # 프레젠테이션 레이어
│   ├── api/             # API 뷰
│   └── serializers/     # DRF 시리얼라이저
└── festival_backend/    # Django 설정
```

## 주요 기능

- **테이블 관리**: UUID 기반 테이블 생성
- **테이블별 주문**: 각 테이블마다 독립적인 주문 관리
- **선주문 시스템**: 결제자 정보와 함께 사전 주문 및 SuperToss 연동
- 음식 목록 조회 (카테고리별 필터링 지원)
- 음식 상세 정보 조회
- 테이블별 주문 내역 조회

## API 엔드포인트

### 음식 관련
- `GET /api/foods/` - 음식 목록 조회
- `GET /api/foods/?category=menu` - 메뉴 카테고리 음식 조회
- `GET /api/foods/?category=drinks` - 음료 카테고리 음식 조회
- `GET /api/foods/{id}/` - 특정 음식 상세 조회

### 테이블 관련
- `GET /api/tables/` - 테이블 목록 조회
- `GET /api/tables/{table_id}/` - 특정 테이블 상세 조회 (UUID)
- `POST /api/tables/create/` - 새 테이블 생성
- `GET /api/tables/{table_id}/orders/` - 특정 테이블의 주문 내역 조회

### 주문 관련
- `POST /api/orders/` - 주문 생성 (table_id 필수)
- `GET /api/orders/history/` - 전체 주문 내역 조회
- `GET /api/orders/history/?table_id={table_id}` - 특정 테이블 주문 내역 조회
- `POST /api/orders/pre-order/{table_id}/` - 선주문 생성 및 SuperToss 결제 연동

## 설치 및 실행

### 사전 요구사항
- Python 3.12+
- uv (Python 패키지 매니저)

### 설치
```bash
cd backend
uv sync
```

### 데이터베이스 설정
```bash
# 마이그레이션 적용
uv run python manage.py migrate

# 초기 데이터 생성
uv run python manage.py seed_data    # 음식 데이터
uv run python manage.py seed_tables  # 테이블 데이터 (A1-A5, B1-B5, C1-C5)
```

### 개발 서버 실행
```bash
uv run python manage.py runserver
```

서버가 `http://127.0.0.1:8000`에서 실행됩니다.

## 테이블 단위 주문 시스템

이 시스템은 테이블 단위로 주문을 관리합니다:

1. **테이블 ID**: UUID 기반으로 각 테이블을 고유하게 식별
2. **주문 연결**: 모든 주문은 특정 테이블에 연결됨
3. **주문 상태 관리**: `pre_order` (선주문), `completed` (완료) 상태 지원
4. **결제 연동**: SuperToss를 통한 자동 결제 처리
5. **프론트엔드 연동**: 프론트엔드에서 path parameter로 table_id 전달

### 주문 생성 예시

#### 일반 주문
```json
POST /api/orders/
{
  "table_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": [
    {"food_id": 1, "quantity": 2},
    {"food_id": 7, "quantity": 1}
  ]
}
```

#### 선주문 (Pre-Order)
```json
POST /api/orders/pre-order/550e8400-e29b-41d4-a716-446655440000/
{
  "payer_name": "홍길동",
  "total_amount": 15000
}
```

선주문 생성 시 자동으로 SuperToss 결제 페이지로 리다이렉트됩니다:
```
supertoss://send?amount=15000&bank=하나은행&accountNo=36491080223907&origin=qr
```

## Clean Architecture

이 프로젝트는 Clean Architecture 원칙을 따릅니다:

1. **Domain Layer**: 비즈니스 로직과 엔티티 (Food, Table, Order)
2. **Infrastructure Layer**: 데이터베이스, 외부 서비스
3. **Application Layer**: 애플리케이션 서비스
4. **Presentation Layer**: API 뷰와 시리얼라이저

## 환경 설정

`.env` 파일에서 다음 설정을 관리할 수 있습니다:

```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

## CORS 설정

프론트엔드 애플리케이션과의 통신을 위해 CORS가 설정되어 있습니다.
기본적으로 `localhost:3000`에서의 요청을 허용합니다.
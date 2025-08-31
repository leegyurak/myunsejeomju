# 숭실대축제 어드민 시스템

숭실대축제 주문 관리를 위한 어드민 웹 애플리케이션입니다.

## 주요 기능

### 1. 메뉴 관리
- 메뉴 등록, 조회, 수정, 삭제
- 품절 처리 기능
- 카테고리별 관리 (메뉴/음료)

### 2. 테이블별 주문 내역
- 테이블 목록 조회
- 테이블별 주문 내역 조회
- 테이블별 매출 통계

### 3. 전체 주문 내역
- 전체 주문 목록 조회
- 주문자 이름으로 검색
- 주문 상태별 필터링 (완료/선주문)
- 정렬 기능 (날짜/금액)
- 매출 통계

## 기술 스택

- **Frontend**: React 18, TypeScript
- **Routing**: React Router v6
- **Styling**: Inline CSS
- **API**: REST API 연동

## 설치 및 실행

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm start

# 빌드
npm run build
```

## API 연동

백엔드 API 서버와 연동하여 다음 엔드포인트를 사용합니다:

- `GET /api/foods/` - 음식 목록 조회
- `POST /api/foods/` - 음식 등록
- `PATCH /api/foods/{id}/` - 음식 수정
- `DELETE /api/foods/{id}/` - 음식 삭제
- `GET /api/tables/` - 테이블 목록 조회
- `GET /api/tables/{id}/orders/` - 테이블별 주문 조회
- `GET /api/orders/history/` - 전체 주문 내역 조회

## 프로젝트 구조

```
src/
├── components/
│   ├── Layout.tsx           # 레이아웃 컴포넌트
│   ├── MenuManagement.tsx   # 메뉴 관리
│   ├── TableOrders.tsx      # 테이블별 주문
│   └── OrderHistory.tsx     # 전체 주문 내역
├── services/
│   └── api.ts              # API 서비스
├── types/
│   ├── food.ts             # 음식 타입 정의
│   ├── order.ts            # 주문 타입 정의
│   └── table.ts            # 테이블 타입 정의
├── App.tsx
├── App.css
├── index.tsx
├── index.css
└── react-app-env.d.ts
```

## 환경 설정

기본적으로 백엔드 API 서버가 `http://localhost:8000`에서 실행되고 있다고 가정합니다.
다른 주소를 사용하는 경우 `src/services/api.ts`의 `API_BASE_URL`을 수정하세요.
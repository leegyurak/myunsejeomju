# 🍽️ 면세점주 (MyunseJeomju)

**면세점주**는 현대적인 음식 주문 시스템으로, 고객이 쉽게 음식을 주문하고 관리할 수 있도록 도와주는 풀스택 웹 애플리케이션입니다.

## 📋 프로젝트 개요

면세점주는 음식점 운영을 위한 종합 솔루션으로, 고객 주문부터 관리자 페이지까지 모든 기능을 제공합니다. 마이크로서비스 아키텍처를 기반으로 확장성과 유지보수성을 고려하여 설계되었습니다.

## 🏗️ 아키텍처

이 프로젝트는 3개의 독립적인 서비스로 구성됩니다:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │     Backend     │    │      Admin      │
│   (React/TS)    │◄───┤  (Django/REST)  ├───►│   (Django)      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🎨 Frontend
- **기술 스택**: React 19 + TypeScript
- **주요 기능**: 
  - 사용자 친화적인 주문 인터페이스
  - 반응형 웹 디자인
  - 실시간 주문 상태 확인

### ⚙️ Backend
- **기술 스택**: Django 5 + Django REST Framework + MySQL
- **주요 기능**:
  - RESTful API 제공
  - 주문 관리 시스템
  - 사용자 인증 및 권한 관리
  - 데이터베이스 관리

### 🛠️ Admin
- **기술 스택**: Django Admin Interface
- **주요 기능**:
  - 주문 관리
  - 메뉴 관리
  - 사용자 관리
  - 통계 및 리포트

## 🚀 빠른 시작

### 전체 서비스 실행 (Docker Compose)

```bash
# 1. 저장소 클론
git clone https://github.com/devgyurak/myunsejeomju.git
cd myunsejeomju

# 2. 각 서비스의 Docker Compose 실행
# Backend 실행
cd backend
docker-compose up -d
cd ..

# Admin 실행
cd admin
docker-compose up -d
cd ..

# Frontend 실행 (개발 모드)
cd frontend
npm install
npm start
```

### 개별 서비스 실행

#### Frontend 개발 환경 설정
```bash
cd frontend
npm install
npm start
# http://localhost:3000에서 접속
```

#### Backend 개발 환경 설정
```bash
cd backend
pip install -e .[dev,test]
python manage.py migrate
python manage.py runserver
# http://localhost:8000에서 API 접속
```

#### Admin 개발 환경 설정
```bash
cd admin
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8001
# http://localhost:8001/admin에서 관리자 접속
```

## 🐳 Docker 배포

각 서비스는 독립적인 Docker 이미지로 빌드되며, 태그 기반 자동 배포를 지원합니다.

### 수동 빌드
```bash
# Frontend
docker build -t myunsejeomju-frontend ./frontend

# Backend
docker build -t myunsejeomju-backend ./backend

# Admin
docker build -t myunsejeomju-admin ./admin
```

### 자동 배포
Git 태그를 푸시하면 GitHub Actions를 통해 자동으로 Docker Hub에 배포됩니다:

```bash
git tag v1.0.0
git push origin v1.0.0
```

## 🧪 테스트 실행

### Backend 테스트
```bash
cd backend
pytest
# 또는 커버리지와 함께
pytest --cov
```

### Frontend 테스트
```bash
cd frontend
npm test
```

## 📁 프로젝트 구조

```
myunsejeomju/
├── 📁 frontend/          # React 클라이언트 애플리케이션
│   ├── 📁 src/
│   ├── 📁 public/
│   ├── 🐳 Dockerfile
│   └── 📦 package.json
├── 📁 backend/           # Django REST API 서버
│   ├── 📁 myunsejeomju/
│   ├── 📁 tests/
│   ├── 🐳 Dockerfile
│   └── 📄 pyproject.toml
├── 📁 admin/             # Django 관리자 인터페이스
│   ├── 📁 myunsejeomju/
│   ├── 🐳 Dockerfile
│   └── 🗄️ docker-compose.yml
└── 📁 .github/           # CI/CD 워크플로우
    └── 📁 workflows/
```

## 🛡️ 환경 변수

각 서비스에 필요한 환경 변수들:

### Backend & Admin
```bash
SECRET_KEY=your-django-secret-key
DEBUG=False
DATABASE_URL=mysql://user:password@host:port/dbname
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Docker Hub 배포 (GitHub Secrets)
```bash
DOCKERHUB_USERNAME=your-username
DOCKERHUB_PASSWORD=your-password
```

## 🤝 기여하기

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👨‍💻 개발자

- **Developer**: [devgyurak](https://github.com/leegyurak)

## 📧 문의

프로젝트에 대한 문의사항이나 버그 리포트는 [Issues](https://github.com/devgyurak/myunsejeomju/issues)에 등록해 주세요.

---

<div align="center">
  <strong>🍽️ 면세점주로 더 나은 주문 경험을 만들어보세요! 🍽️</strong>
</div>
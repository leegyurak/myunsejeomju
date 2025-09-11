<h1 align="center"> 면세점주 (Myunsejeomju) </h1> <br>
<p align="center">
  <a href="#">
    <img alt="Myunsejeomju" title="Myunsejeomju" src="#" width="450">
  </a>
</p>

<p align="center">
  음식점 주문 및 결제 시스템. React + Django로 구축.
</p>

<p align="center">
  <a href="#">
    <img alt="Web Application" title="Web App" src="#" width="140">
  </a>
</p>

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Feedback](#feedback)
- [Contributors](#contributors)
- [Build Process](#build-process)
- [Backers](#backers-)
- [Sponsors](#sponsors-)
- [Acknowledgments](#acknowledgments)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

[![React](https://img.shields.io/badge/React-19-blue.svg?style=flat-square)](https://reactjs.org/)
[![Django](https://img.shields.io/badge/Django-5.2+-green.svg?style=flat-square)](https://djangoproject.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9+-blue.svg?style=flat-square)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?style=flat-square)](https://python.org/)

음식점 메뉴 주문, 결제 처리, 직원 호출 등의 기능을 제공하는 웹 기반 주문 시스템입니다. React + Django 기반으로 구축되어 있으며, 모바일과 데스크톱에서 모두 사용 가능합니다.

**웹 브라우저에서 바로 이용 가능합니다.**

<p align="center">
  <img src = "http://i.imgur.com/HowF6aM.png" width=350>
</p>

## Features

면세점주에서 사용할 수 있는 주요 기능들:

* 음식 메뉴 보기 및 주문
* 다양한 결제 수단 지원 (카카오페이, 토스페이)
* 직원 호출 기능
* 주문 상태 확인
* 관리자 대시보드
* 모바일 반응형 디자인
* 실시간 주문 처리

<p align="center">
  <img src = "http://i.imgur.com/IkSnFRL.png" width=700>
</p>

<p align="center">
  <img src = "http://i.imgur.com/0iorG20.png" width=700>
</p>

## Feedback

피드백이나 개선 사항이 있으시면 [Issues](https://github.com/your-repo/issues/new)를 통해 알려주세요. 기능 요청은 언제나 환영합니다. 기여를 원하신다면 [contributing guidelines](./CONTRIBUTING.md)를 참고해 주세요!

## Contributors

이 프로젝트는 [all-contributors](https://github.com/kentcdodds/all-contributors) 사양을 따르며, 다음의 [귀중한 기여자들](./CONTRIBUTORS.md)에 의해 만들어졌습니다.

## Build Process

- **선행 요구사항**: Node.js 16+, Python 3.12+, uv, MySQL 8.0+
- 리포지토리 클론 또는 다운로드
- **Frontend**: `cd frontend && npm install && npm start`
- **Backend**: `cd backend && uv sync && uv run python manage.py migrate && uv run python manage.py runserver`
- **Admin**: `cd admin && uv sync && uv run python manage.py migrate && uv run python manage.py runserver 8001`
- **Docker 사용**: `docker-compose up`으로 전체 시스템 실행

자세한 개발 가이드와 문제 해결 정보는 [contributing guidelines](./CONTRIBUTING.md)를 참고하세요.

**개발 환경 설정**: 각 컴포넌트별로 환경 변수 파일(`.env`)을 설정해야 합니다. 결제 시스템 API 키는 개발용이므로 실제 서비스에서는 변경해야 합니다.

## 기술 스택

### Frontend
- React 19 + TypeScript
- React Router DOM
- Create React App

### Backend  
- Django 5.2+ + Django REST Framework
- MySQL + PyMySQL
- Gunicorn

### Admin Panel
- Django Admin
- MySQL Database

## 배포

Docker Compose를 사용한 프로덕션 배포:

```bash
docker-compose -f docker-compose.yml up -d
```

## Acknowledgments

개발 도구 및 라이브러리 지원에 감사드립니다.

# 📰 DAESORY NEWS: 실시간 뉴스 추천, 검색 및 분석 서비스

## 프로젝트 소개

<img src="https://github.com/user-attachments/assets/60910a47-46eb-4ddc-ab3e-45aa48911b6c" width="800" style="display:block; margin:auto"/>

**DAESORY NEWS**는 다양한 언론사의 뉴스를 실시간으로 수집하고 전처리하여 사용자가 뉴스에 더 깊이 몰입할 수 있도록 돕는  **맞춤형 뉴스 추천**, **검색 기능**, **분석 대시보드**, **뉴스 기반 챗봇**을 포함한 통합 뉴스 플랫폼입니다.  
Airflow, Kafka, Flink, Spark, HDFS, PostgreSQL, Elasticsearch, Django, Vue 등의 기술을 활용하여  **뉴스 수집부터 저장, 분석, 검색, 대화형 질의응답 제공**까지 모든 과정을 **자동화**합니다.

---

## 시스템 아키텍처

![system-architecture](/uploads/5349c460d110889b4903ac2535f33211/SystemArchitecture.png)

- **뉴스 수집**: Python RSS 크롤러 → Kafka  
- **전처리 및 저장**: Flink + OpenAI API → PostgreSQL, Elasticsearch, HDFS  
- **분석 및 보고**: Spark → PDF 생성  
- **전체 오케스트레이션**: Airflow DAG 자동화  

---

## 서비스 주요 기능

- 🗞️ **맞춤형 뉴스 추천**  
  사용자가 좋아요한 기사의 임베딩 기반으로 유사 뉴스 추천

- 🔎 **관련 뉴스 검색**  
  Elasticsearch를 기반으로 입력한 키워드 또는 문장과 유사한 뉴스를 빠르게 검색 가능

- 📊 **대시보드 제공**  
  사용자의 관심 카테고리, 주요 키워드, 주간 열람 수, 좋아요한 기사 등을 시각화

- 🤖 **뉴스 기반 챗봇**  
  사용자가 보고 있는 뉴스 본문을 바탕으로 GPT 기반 RAG 응답 제공

---

## 시연 이미지 및 영상

### 🖼️ 주요 화면

| 화면 | 이미지 |
|------|--------|
| 뉴스 목록 | ![news-list](/uploads/9e26386891b7e6b769796d1d36a68ae6/news-list.png) |
| 뉴스 상세 | ![news-detail](/uploads/f02786adf32cdd6cf936ab34d282d037/news-detail.png) |
| 뉴스 검색 | ![news-search](/uploads/8f25ab4e8700369424f879ef18f80ff3/news-search.png) |
| 대시보드 | ![dashboard](/uploads/0defcfc929433b0aa1316da00a46e831/dashboard.png) |
| 로그인 | ![login](/uploads/7d74651a6b0f245186d6801d7023cd4b/login.png) |
| 회원가입 | ![register](/uploads/48e858a4c7fecad479329c605f7a6264/register.png) |

---

### 🎥 시연 영상
[시연 영상 보기](https://youtu.be/__o4B1__y-E)

---

## 기반 기술별 기능 정리

### 데이터 파이프라인 (Airflow, Kafka, Flink, Spark, HDFS, PostgreSQL, Elasticsearch)

- Kafka

   - Python 기반 RSS 크롤러가 연합뉴스, 매일경제, 한국경제 등 주요 언론사의 RSS 데이터를 수집하여 Kafka로 전송
   - 수집한 뉴스 데이터를 카테고리별로 Topic 분류
   - 실시간 스트리밍 파이프라인의 시작점 역할

- Flink

   - Kafka Topic으로부터 뉴스 데이터를 실시간으로 소비
   - OpenAI API를 호출하여 기사 본문에 대한 키워드 추출 및 임베딩(1536차원) 생성
   - 처리된 뉴스 데이터를 PostgreSQL, Elasticsearch, HDFS에 동시 저장

- PostgreSQL

   - Django 백엔드와 연동
   - 뉴스 본문, 메타데이터, 사용자 상호작용(조회수, 좋아요 등)을 저장
   - `pgvector`를 활용하여 문서 임베딩 저장 및 추천 연산 가능

- Elasticsearch

   - 검색 성능 최적화를 위한 뉴스 색인 저장소
   - `title`, `content`, `writer`, `keywords` 필드를 대상으로 텍스트 검색 수행
   - Django API를 통해 유사 뉴스 추천 및 키워드 검색 기능 제공

- HDFS

   - Flink에서 처리된 데이터를 분석용 원본(JSON) 형태로 저장
   - Spark 분석 및 PDF 리포트 생성 작업을 위한 장기 보관소로 활용

- Spark

   - 하루 단위로 HDFS에 저장된 뉴스 데이터를 수집
   - 사용자 상호작용 데이터를 기반으로 키워드/카테고리 통계를 추출
   - 추출 결과를 시각화하여 PDF 형태의 일일 리포트로 저장

- Airflow

   - 전체 파이프라인을 DAG 단위로 자동화 구성
     - **Kafka → Flink → 3방향 저장 DAG**  
       - Flink가 Kafka로부터 실시간 뉴스 데이터를 소비하고  
         처리 결과를 PostgreSQL, Elasticsearch, HDFS에 분산 저장  
       - 실행 주기: 매시간

     - **Spark 분석 리포트 DAG**  
       - HDFS에 저장된 하루치 뉴스를 Spark로 분석  
       - 키워드/카테고리 통계 PDF 리포트 생성  
       - 실행 주기: 매일 새벽 1시

     - **PostgreSQL, Elasticsearch 동기화 DAG**  
       - Flink 결과 중 누락되었거나 실패한 데이터를 PostgreSQL/Elasticsearch에 재동기화  
       - 실행 주기: 매시간

---

### 백엔드 (Django + Django REST Framework)

- **Django + DRF + PostgreSQL**

   - **프로젝트 구조 및 앱 분리**
     - `mynews`: 전체 프로젝트 베이스 설정 및 공통 모델 정의
     - `news_article`: 뉴스 기사 정보 관리 (임베딩 포함)
     - `news_interaction`: 좋아요 및 조회 기록 API 제공
     - `news_dashboard`: 사용자 맞춤형 대시보드 API
     - `news_search`: Elasticsearch + PostgreSQL 연동 검색 API
     - `news_chatbot`: 뉴스 기반 GPT 챗봇 API

   - **ORM 모델 정의**
     - `NewsArticle`: 기사 정보 (제목, 본문, 키워드, 임베딩 포함), `managed=False` 설정
     - `NewsLike`: 사용자-기사 좋아요 관계
     - `NewsView`: 사용자-기사 조회 관계 (익명 허용 가능)

   - **상호작용 API (`news_interaction`)**
     - 좋아요 등록/취소 (POST/PUT)
     - 좋아요 여부 및 개수 조회 (GET)
     - 조회 기록 저장 및 조회수 확인 (POST/GET)

   - **사용자별 대시보드 API (`news_dashboard`)**
     - 좋아요 기반 카테고리 선호 통계
     - 키워드 빈도 상위 5개 추출 (`JSONField` 기반)
     - 최근 7일간 뉴스 열람 수 집계 (비어 있는 날짜 포함)
     - 좋아요한 기사 리스트 + 상호작용 수치 포함

   - **인증 및 세션**
     - JWT 인증 적용: `dj-rest-auth`, `rest_framework_simplejwt`
     - 이메일 기반 로그인/회원가입
     - 세션 및 JWT 병행 사용: 사용자별 챗봇 대화 이력 관리 등

   - **기타 설정**
     - `pgvector` 확장으로 1536차원 임베딩 벡터 저장 지원
     - CORS 설정: 개발 환경에서는 모든 출처 허용
     - 데이터베이스: PostgreSQL (`news` DB, 수동 마이그레이션)

- **Elasticsearch**

   - **하이브리드 뉴스 검색 시스템 (`news_search`)**
     - 색인명: `news-articles`
     - 대상 필드: `title`, `content`, `writer`, `keywords`
     - 검색 결과의 `_id`(url) 기준으로 PostgreSQL에서 실제 기사 정보 조회

- **LangChain + GPT (OpenAI API)**

   - **뉴스 기반 챗봇 (`news_chatbot`)**
     - RAG (Retrieval-Augmented Generation) 구조 적용
       - `SystemMessage`: 기사 제목, 작성일, 본문 포함
       - `HumanMessage`: 사용자 질문
       - `AIMessage`: GPT 응답
     - 최근 20개 메시지 기준 컨텍스트 유지
     - Django 세션 기반 사용자별 기사 대화 이력 관리
     - 대화 초기화 엔드포인트 `/chat/reset/<article_id>/` 제공

---

### 프론트 (Vue 3 + Pinia + Chart.js)

- **Vue 3 + Composition API**

   - 컴포넌트별 `script setup` 방식으로 구성
   - `ref`, `computed`, `watch`, `onMounted`, `defineProps` 등 Composition API 전반 사용
   - `defineOptions`로 컴포넌트 네이밍 명시

- **Pinia (상태 관리)**

   - `auth.js`  
     - 로그인, 로그아웃, 회원가입, 토큰 갱신, 사용자 정보 저장
     - 토큰 로컬스토리지 유지 (`persist`)
   - `newsFilter.js`  
     - 카테고리 탭(`activeTab`), 정렬(`sortBy`), 페이지(`currentPage`) 상태 관리

- **Vue Router**

   - 주요 경로 설정
     ```
     /news          뉴스 목록
     /news/:id      뉴스 상세 (GPT 챗봇 포함)
     /dashboard     사용자 대시보드
     /login         로그인
     /register      회원가입
     ```
   - 인증 필요 경로에 `meta: { requiresAuth: true }` 설정
   - 404 처리: `/:pathMatch(.*)*`

- **Axios**

   - `utils/axios.js`에서 Axios 인스턴스 생성
   - `VITE_API_BASE_URL` 환경 변수 기반 요청
   - 로그인 성공 시 Authorization 헤더 자동 설정

- **컴포넌트 구성**

   - **뉴스 관련**
     - `NewsCard.vue`: 뉴스 리스트 카드
     - `NewsDetailView.vue`: 상세 보기 및 GPT 챗봇, 관련 뉴스
     - `ArticlePreview.vue`: 관련 뉴스/좋아요 뉴스 미리보기
     - `NewsChatbot.vue`: LangChain 기반 챗봇 UI
   - **레이아웃**
     - `TheHeader.vue`: 검색 + 라우팅 + 로그인/로그아웃 처리
     - `TheFooter.vue`: 고정 푸터
     - `ContentBox.vue`: 공통 카드 박스
   - **대시보드**
     - `DashBoardView.vue`: 도넛/바 차트 + 좋아요 기사 리스트
     - `vue-chartjs` + `chart.js` 조합으로 시각화 처리

- **인증 기능**

   - `LoginView.vue`, `RegisterView.vue`를 통한 이메일 기반 로그인/가입
   - 인증 여부에 따른 기능 제어 (예: 챗봇, 대시보드 접근, 추천 뉴스 정렬)
   - 인증 상태는 Pinia에서 전역 유지 및 자동 토큰 갱신 지원

- **스타일링 및 UX**

   - 각 컴포넌트별 SCSS(SASS) scoped 스타일 구성
   - 반응형 대응 (미디어 쿼리)
   - 입력창, 로딩상태, 비활성화 등 UI 디테일 구현
   - 챗봇 대화 흐름 및 스크롤 자동 이동 처리

- **기타**

   - 검색창 입력 시 `/news?q=...` 쿼리 기반 검색 실행
   - 기사 클릭 시 조회수 API 자동 호출
   - 샘플 데이터 fallback (대시보드 미로그인 시)

---

## 설치 및 실행 방법

### 전체 실행 순서

1. 데이터 파이프라인 실행
2. 백엔드 실행
3. 프론트엔드 실행

---

### 🛰️ 데이터 파이프라인 실행 (Docker Compose)

```bash
cd data-pipeline
docker-compose up --build
```

- Kafka, Flink, PostgreSQL, Elasticsearch, HDFS, Airflow 실행됨  
- Airflow UI: [http://localhost:8080](http://localhost:8080)  
- 기본 계정: ID `airflow`, PW `airflow`

**Airflow 실행 순서**
1. `news_pipeline_dag`
2. `sync_pg_to_es_dag`
3. `daily_report_dag`

---

### 🔧 백엔드 실행 (Django)

```bash
cd back-end
python -m venv venv
venv\Scripts\activate  # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

### 🎨 프론트엔드 실행 (Vue 3)

```bash
cd front-end
npm install
npm run dev
```

접속 주소: [http://localhost:3000](http://localhost:3000)

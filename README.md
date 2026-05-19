# NoA

> 태양광 잉여전력 기반 양돈농가 슬러지 건조 경제성 진단 서비스

양돈농가가 태양광 잉여전력을 활용해 분뇨·슬러지 처리비를 얼마나 절감할 수 있는지 확인할 수 있는 Streamlit 기반 웹 서비스입니다.

사용자는 농장 지역, 돼지 사육두수, 태양광 용량, 월 처리비 등을 입력하고, 시스템은 공공데이터 API, 지역 코드 CSV, Roboflow API, Python 계산 로직을 활용해 진단 결과를 제공합니다.

---

## Service Flow

```text
사용자 입력
        ↓
돼지 사육두수 입력 또는 이미지 업로드
        ↓
Roboflow API 기반 돼지 개체수 추정
        ↓
지역 코드 CSV 기반 관측지점 코드 조회
        ↓
공공데이터 API 기반 일사량 조회
        ↓
Python 계산 로직 실행
        ↓
태양광 발전량, 건조 가능량, 절감액, ROI 계산
        ↓
Streamlit UI 결과 출력
        ↓
RAG 챗봇 질의응답
```

---

## Data & API

### 농업기상 공공데이터 API

- **제공처**: 농촌진흥청 국립농업과학원 / 공공데이터포털
- **데이터명**: 농업기상 기본 관측데이터 조회
- **링크**: https://www.data.go.kr/data/15078057/openapi.do
- **활용 목적**: 지역별 일사량 데이터를 조회하여 태양광 발전량 계산에 활용

### 지역 코드 CSV

- **제공처**: 농촌진흥청 농업기상 관측지점정보
- **링크**: https://weather.rda.go.kr/weather/observationInfo.do
- **활용 목적**: 사용자가 선택한 지역명을 API 호출에 필요한 관측지점 코드로 변환

### Roboflow API

- **제공처**: Roboflow Universe
- **데이터셋명**: pig_seg
- **링크**: https://universe.roboflow.com/harbin-institute-of-technologycontrol-engineering/pig_seg-jnpek
- **활용 목적**: 이미지에서 돼지 객체를 탐지하고 개체수 추정

---

## Calculation Logic

계산 로직은 별도의 외부 API가 없기 때문에 Python 내부 로직으로 처리합니다.
계산에 사용되는 값은 참고 문서와 시나리오 값을 기반으로 하며, MVP 단계의 추정값입니다.

### 주요 계산 항목

- 월 분뇨 발생량
- 건조 대상 슬러지 추정량
- 월 태양광 발전량
- 월 잉여전력
- 태양광 기반 슬러지 건조 가능량
- 월 예상 처리비 절감액
- 절감률
- ROI

---

## AI Implementation

### Computer Vision

Roboflow API를 활용하여 업로드된 이미지에서 돼지 객체를 탐지하고 개체수를 추정합니다.
직접 학습한 모델을 저장소에 포함하지 않고, 외부 Computer Vision API를 호출하는 방식으로 사용합니다.

### Rule-based Calculation

경제성 진단 결과는 학습 모델이 아니라 Python 내부 계산 로직으로 산출합니다.

### RAG Chatbot
RAG는 계산을 수행하지 않습니다.

---

## Tech Stack

| Category | Stack |
|---|---|
| UI | Streamlit |
| Language | Python |
| Data Processing | Pandas |
| API Request | Requests |
| LLM| OpenAI|
| Embedding | sentence-transformers |
| Vector DB | ChromaDB |
| PDF Parsing | pdfplumber |
| Computer Vision | Roboflow API |
| Environment | python-dotenv |
| Data Storage | CSV / PDF|
| Version Control | Git / GitHub |

---


## Environment Variables

본 저장소에는 API 인증키를 포함하지 않습니다.
API Key는 로컬 개발 환경의 `.env` 파일에서 관리합니다.

```env
SOLAR_EXPOSURE_API_KEY=your_public_data_api_key
ROBOFLOW_API_KEY=your_roboflow_api_key
```

`.env` 파일은 GitHub에 업로드하지 않도록 `.gitignore`에 포함합니다.

---

## Repository Policy

본 저장소에는 다음 항목을 포함하지 않습니다.

- API 인증키
- `.env` 파일
- Roboflow API Key
- 공공데이터 API Key

공개 가능한 코드, CSV 설정값, Streamlit UI, Python 계산 로직만 저장소에 포함합니다.




# AI Workflow
> 본 프로젝트는 **조사 → 정리 → 개발 → 발표** 각 단계에 최적의 AI 도구를 선택적으로 투입하는 분업 구조를 채택합니다.
 
| 단계 | 도구 | 핵심 역할 |
|---|---|---|
| 조사 | Perplexity | 실시간 문서 기반 팩트 체크 및 출처 수집 |
| 정리 | Claude  | Notion Mcp Server를 활용한 빠른 문서 정리|
| 아이디어 | ChatGPT / Gemini | 서비스 기획 및 아이디어 발산 |
| 개발 | Claude Code / Gemini CLI | 소스코드 구현 및 자동화 |
| 발표 | Gamma | 웹 임베드 기반 인터랙티브 슬라이드 |
 
---
 

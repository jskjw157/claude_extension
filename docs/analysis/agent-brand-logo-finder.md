# 에이전트 분석: brand-logo-finder

## 1. 에이전트 개요
- **이름**: `brand-logo-finder`
- **목적**: 사용자가 브랜드 로고나 자산을 요청할 때, Brandfetch 서비스를 활용하여 관련 정보를 검색하고 제공합니다.
- **모델**: `haiku` (빠르고 비용 효율적인 모델 선택)
- **도구(Tools)**: `WebFetch`, `WebSearch`

## 2. 프롬프트 구조 분석

### 2.1 YAML Frontmatter
```yaml
---
name: brand-logo-finder
description: Finds brand logos using Brandfetch. Use when user asks for a brand's logo, brand assets, or brand identity information.
tools: WebFetch, WebSearch
model: haiku
---
```
- **name**: 에이전트의 고유 식별자.
- **description**: 오케스트레이터(또는 Claude Code 라우팅 시스템)가 이 에이전트를 언제 호출해야 하는지 명확한 트리거 조건을 제시합니다. ("Use when user asks for...")
- **tools**: 필요한 외부 도구를 명시적으로 허용합니다. 여기서는 웹 검색과 페이지 가져오기 기능이 필수적입니다.
- **model**: 작업의 난이도에 맞춰 경량 모델(`haiku`)을 지정하여 속도와 비용을 최적화했습니다.

### 2.2 Role & Process Definition
- **Role**: "brand logo finder specialist"라는 페르소나를 부여하여 역할의 범위를 한정합니다.
- **Process**: 작업 수행 단계를 명확한 순서(1~4단계)로 정의합니다.
    1.  **Find Brand Domain**: `WebSearch`를 통해 공식 도메인을 먼저 찾도록 유도합니다. (Brandfetch URL 패턴을 맞추기 위함)
    2.  **Extract Domain**: 검색 결과에서 정확한 도메인을 추출합니다.
    3.  **Access Brandfetch**: `https://brandfetch.com/[brand-domain]` 패턴을 사용하여 직접 접근을 시도합니다.
    4.  **Extract Logo Info**: 페이지 내용에서 정보를 파싱합니다.

### 2.3 Output & Example
- **Output Format**: 제공해야 할 정보의 필드(Brand Name, Logo URLs, Colors 등)를 구조화하여 정의했습니다.
- **Example**: 입력("Spotify")에 대한 처리 과정을 예시로 보여주어 에이전트가 프로세스를 이해하는 것을 돕습니다.

### 2.4 Guidelines (Edge Case Handling)
- 공식 도메인 우선 검색 원칙
- 복수 도메인 발견 시 권위 있는 도메인(.com) 선택
- Brandfetch 미발견 시 대체 확장자 시도 등 예외 처리 로직을 포함합니다.

## 3. 핵심 시사점 (Best Practices)
1.  **모델 최적화**: 단순 검색 및 정보 추출 작업에는 `haiku`와 같은 경량 모델을 명시하여 효율성을 높였습니다.
2.  **패턴 기반 접근**: 외부 서비스(Brandfetch)의 URL 패턴(`brandfetch.com/[domain]`)을 활용하여 복잡한 API 연동 없이도 웹 스크래핑만으로 데이터를 확보하는 영리한 전략을 사용합니다.
3.  **명확한 프로세스 체인**: `검색 -> 도메인 추출 -> URL 구성 -> 데이터 추출`로 이어지는 논리적 흐름을 강제하여 성공률을 높였습니다.

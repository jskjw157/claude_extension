# Monet-Registry Claude 활용 완벽 가이드

## 1. 프로젝트 개요

**monet-registry**는 600+ 프로덕션급 React UI 컴포넌트 레지스트리로, Claude를 활용한 자동화의 모범 사례입니다.

| 항목 | 내용 |
|------|------|
| 목적 | 랜딩페이지 컴포넌트 레지스트리 |
| 기술 | Next.js 15, React 19, TypeScript, TailwindCSS |
| Claude 활용 | 에이전트, 스킬, MCP 통합 |

---

## 2. Claude 디렉토리 구조

```
.claude/
├── agents/                         # 전문화된 에이전트
│   ├── brand-logo-finder.md        # 브랜드 로고 검색
│   ├── build-and-screenshot.md     # 빌드 & 스크린샷 자동화
│   └── img-to-component.md         # 이미지→컴포넌트 변환
└── skills/
    └── subagent-creator/           # 서브에이전트 생성 프레임워크
        ├── SKILL.md
        ├── assets/
        │   └── subagent-template.md
        └── references/
            ├── available-tools.md
            └── examples.md
```

---

## 3. 에이전트 정의 패턴

### 3.1 YAML Frontmatter 구조

```yaml
---
name: agent-name                    # kebab-case 필수
description: 에이전트 설명 + 사용 시점  # 자동 위임의 핵심
tools: Tool1, Tool2, Tool3          # 선택 - 생략 시 전체 상속
model: sonnet/opus/haiku/inherit    # 선택 - 모델 지정
permissionMode: default             # 선택 - 권한 모드
skills: skill1, skill2              # 선택 - 자동 로드 스킬
---

[시스템 프롬프트 - 역할, 책임, 동작 정의]
```

### 3.2 Description 작성 핵심 (자동 위임 트리거)

**좋은 예시:**
```yaml
description: Expert code reviewer. Use PROACTIVELY after writing or modifying code.
description: Debugging specialist for errors, test failures, and unexpected behavior.
description: base64 이미지를 전달받아 컴포넌트로 구현한다.
```

**나쁜 예시:**
```yaml
description: Helps with code  # 너무 모호함
```

### 3.3 도구(Tools) 조합 패턴

| 용도 | 도구 조합 |
|------|----------|
| **읽기 전용 분석** | `Read, Grep, Glob, Bash` |
| **코드 수정** | `Read, Write, Edit, Grep, Glob, Bash` |
| **최소 권한** | `Read, Grep, Glob` |
| **전체 권한** | (tools 필드 생략) |
| **외부 검색** | `WebFetch, WebSearch` |

---

## 4. 에이전트 실제 예시 분석

### 4.1 brand-logo-finder (45줄) - 단순 에이전트

```yaml
---
name: brand-logo-finder
description: Finds brand logos using Brandfetch. Use when user asks for a brand's logo.
tools: WebFetch, WebSearch
model: haiku                        # 가벼운 작업이므로 haiku 사용
---
```

**특징:**
- 최소한의 도구만 지정
- 경량 모델(haiku) 사용
- 명확한 사용 시점 기술

### 4.2 build-and-screenshot (241줄) - 복잡한 에이전트

```yaml
---
name: build-and-screenshot
description: 컴포넌트 메타데이터 검증/빌드, 프로젝트 빌드, 스크린샷 캡처를 순차적으로 수행
tools: Bash, Read, Glob, Edit
---
```

**구조:**
1. 참조 파일 목록
2. 유효값 열거 (21개 카테고리, 26개 기능태그 등)
3. 6단계 파이프라인
4. 에러 자동수정 테이블 (14개 패턴)
5. 메타데이터 템플릿
6. 출력 형식 정의

**에러 자동수정 테이블 예시:**
```
| 에러                    | 수정 방법                              |
|------------------------|---------------------------------------|
| schemaVersion 불일치    | "2.0"으로 변경                         |
| name 형식 오류          | kebab-case로 변환                      |
| category enum 오류      | 폴더명에서 추론 또는 'other' 사용        |
| 알 수 없는 태그          | 유효 태그로 교체 또는 freeformKeywords로 이동 |
| preview 절대경로        | 상대경로로 변환                         |
| metadata.yaml 누락      | 템플릿으로 생성                         |
```

### 4.3 img-to-component (287줄) - 가장 상세한 에이전트

```yaml
---
name: img-to-component
description: base64 이미지를 전달받아 컴포넌트로 구현한다.
model: inherit                      # 상위 컨텍스트 모델 상속
---
```

**4단계 프로세스:**

**Phase 1: 이미지 분석**
```
1. 시각적 분석:
   - 레이어 opacity, roundness, border style
   - Figma auto-layout 기반 배치 분석
   - sharp MCP로 정확한 색상 추출
   - font weight, italic 여부
   - line break 위치

2. 4차원 태그 분석:
   - functional: email-capture, animation, carousel...
   - style: dark-theme, modern, minimal, gradient...
   - layout: centered, two-column, full-width...
   - industry: saas, fintech, ai, startup...

3. 언어 분석: en / ko
```

**Phase 2: 컴포넌트 네이밍**
- 반드시 lower-kebab-case

**Phase 3: 스크립트 실행**
```bash
python3 scripts/create-registry-component.py \
  --name "{NAME}" \
  --image-path "{이미지 경로}" \
  --keywords "{키워드1}, {키워드2}" \
  --language "{en|ko}" \
  --tags-functional "{태그1}, {태그2}" \
  --tags-style "{태그1}, {태그2}" \
  --tags-layout "{태그1}, {태그2}" \
  --tags-industry "{태그1}, {태그2}"
```

**Phase 4: 구현 가이드라인**
- 비디오 구현 패턴 (YouTube, HTML5)
- Framer 애니메이션 변환 (motion/react)
- nanobanana MCP 이미지 생성
- 폰트 선택 가이드 (17개 폰트 카테고리별)

---

## 5. 스킬(Skill) 정의 패턴

### 5.1 스킬 디렉토리 구조

```
.claude/skills/{skill-name}/
├── SKILL.md              # 메인 문서 (필수)
├── assets/               # 템플릿, 보일러플레이트
└── references/           # 참조 문서
```

### 5.2 SKILL.md 형식

```markdown
---
name: skill-name
description: 스킬 설명 + 사용 시점 명시
allowed-tools:
  - Bash
  - Read
  - Write
---

# Skill Title

## Instructions
1. 단계별 지침

## Usage
```python
from module import Class
instance = Class()
instance.method()
```

## Config
| 항목 | 값 |
|------|-----|
| 설정1 | 값1 |

## Features
- 기능 목록
```

### 5.3 서브에이전트 생성 스킬 예시

**6가지 패턴 제공:**
1. Code Reviewer - 코드 리뷰 전문
2. Debugger - 디버깅 전문
3. Data Scientist - 데이터 분석
4. Test Runner - 테스트 실행
5. Documentation Writer - 문서화
6. Security Auditor - 보안 감사

---

## 6. 프롬프트 워크플로우 (prompt/ 디렉토리)

### 6.1 init.md - 프로젝트 초기화

```
1. 색상 시스템 설정 (60-30-10 룰)
2. 섹션 구성:
   필수: Header, Footer, Hero, Why?, CTA
   추가: 2-3개 커스텀 섹션
3. 모든 섹션 구현
4. 메타데이터 업데이트
5. 품질 검증 (lint, build)
```

### 6.2 url-to-page.md - URL 스크래핑 파이프라인

**5단계 파이프라인:**

```
Stage 1: 웹사이트 스크래핑
  Command: npx tsx scripts/scrape/scrape-website.ts --url "{URL}"
  Output: public/scraped/{domain}-{date}/
    ├── full-page.png
    ├── page.html
    ├── styles.json
    ├── dom-tree.json
    ├── sections.json
    ├── images.json
    ├── videos.json
    ├── framer.json (Framer 사이트인 경우)
    └── sections/
        └── section-*.png, section-*.html

Stage 2: 섹션 분할 검증
  - full-page.png vs 시각적 경계 비교
  - sections.json 정확도 확인
  - 카테고리 분류 (hero, feature, pricing 등)

Stage 3: 병렬 섹션 컴포넌트 생성
  - 네이밍: {domain}-{category}-{index}
  - 예: example-com-hero-0, example-com-pricing-1

Stage 4: 페이지 컴포넌트 생성
  Command: npx tsx scripts/generate-page-component.ts \
    --name "{domain}-landing" \
    --sections "{id1},{id2},{id3}"

Stage 5: 레지스트리 업데이트
  Command: pnpm metadata:build
```

### 6.3 배치 처리 패턴

```yaml
# 체크리스트 형식 (unsection-hero-sections-checklist.yaml)
- name: image-1.jpg
  implemented: false

- name: image-2.jpg
  implemented: true
  component-id: component-name
```

**처리 흐름:**
1. 체크리스트 읽기
2. 미구현 이미지 식별
3. 최대 20개 병렬 처리
4. 완료 시 체크리스트 업데이트
5. 다음 배치 반복

---

## 7. MCP 도구 통합

### 7.1 nanobanana MCP (이미지 생성)

**XML 디스크립터 형식:**
```xml
<description>
  <is_transparent_background>true/false</is_transparent_background>
  <summary>이미지 짧은 설명</summary>
  <mood>전반적인 디자인 컨셉 및 분위기</mood>
  <background_summary>배경 설명</background_summary>
  <primary_element>위치, 방향, 자세한 묘사</primary_element>
  <etc_element>기타 요소 (있는 경우만)</etc_element>
</description>
```

### 7.2 sharp MCP (이미지 처리)

- 정확한 색상 추출
- 배경 제거 (`remove_background`)

---

## 8. 메타데이터 시스템

### 8.1 스키마 v2.0

```yaml
schemaVersion: "2.0"
name: component-name              # 폴더명과 일치 필수
category: hero                    # 21개 카테고리 중 택1

images:
  preview: public/registry/preview/component-name.png

description:
  short: "150자 이내 설명"

tags:
  functional: [animation, carousel]    # 26개 옵션
  style: [modern, dark-theme]          # 22개 옵션
  layout: [centered, full-width]       # 18개 옵션
  industry: [saas, startup]            # 23개 옵션

freeformKeywords: [custom1, custom2]   # 자유 키워드

fontFamily: [Inter, Satoshi]

source:
  type: url | image | manual | framer
  url: "https://..."
  framer:
    detectedAnimations: [...]

createdAt: "2025-01-01T00:00:00Z"
status: draft | stable | deprecated
language: en | ko
```

### 8.2 4차원 태깅 시스템

| 차원 | 개수 | 예시 |
|------|------|------|
| **Functional** | 26 | carousel, animation, email-capture, video |
| **Style** | 22 | dark-theme, modern, minimal, gradient |
| **Layout** | 18 | centered, two-column, full-width, bento |
| **Industry** | 23 | saas, fintech, ai, startup, e-commerce |

---

## 9. 자동화 스크립트

### 9.1 컴포넌트 생성

```bash
python3 scripts/create-registry-component.py \
  --name "my-hero" \
  --category "hero" \
  --image-path "agent-input/hero.jpg" \
  --keywords "hero, landing, dark" \
  --language "en" \
  --tags-functional "animation" \
  --tags-style "modern, dark-theme" \
  --tags-layout "centered" \
  --tags-industry "saas"
```

### 9.2 메타데이터 관리

```bash
pnpm metadata:validate    # 스키마 검증
pnpm metadata:build       # 레지스트리 생성
pnpm metadata:search      # 검색
pnpm metadata:stats       # 통계
```

### 9.3 스크린샷 자동화

```bash
pnpm docker:screenshot:build   # Docker 이미지 빌드
pnpm docker:screenshot:run     # 증분 캡처
pnpm docker:screenshot:all     # 전체 재캡처
```

---

## 10. 기존 프로젝트 적용 단계

### Step 1: 디렉토리 구조 생성

```bash
mkdir -p .claude/agents .claude/skills prompt scripts
```

### Step 2: 첫 번째 에이전트 작성

```markdown
# .claude/agents/code-reviewer.md
---
name: code-reviewer
description: Expert code reviewer. Use PROACTIVELY after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is simple and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider)
```

### Step 3: 프로젝트별 에이전트 추가

| 프로젝트 유형 | 권장 에이전트 |
|--------------|--------------|
| **웹 프론트엔드** | img-to-component, a11y-checker, component-reviewer |
| **백엔드/API** | api-designer, db-migrator, security-auditor |
| **AI/ML** | data-preprocessor, model-evaluator, pipeline-orchestrator |
| **자동화** | build-runner, deploy-manager, doc-generator |

### Step 4: 자동화 스크립트 작성

```
scripts/
├── create-{domain}-component.py   # 컴포넌트 생성
├── validate-{domain}.ts           # 검증
└── generate-{domain}.ts           # 빌드
```

### Step 5: 메타데이터 스키마 정의

프로젝트에 맞는 YAML 스키마 정의:
- 필수 필드
- 유효값 열거
- 검증 로직

---

## 11. 핵심 설계 원칙

### 11.1 명시적 제약이 승리한다

```markdown
## 주의사항 (절대 하지 말 것):
- 절대 playwright-mcp를 사용하지 마세요
- 절대 npm run build를 테스트하지 마세요
- index.tsx 외의 다른 tsx 파일은 생성하지 마세요
```

### 11.2 검증 먼저, 실행 나중

```
1. 메타데이터 검증 → pnpm metadata:validate
2. 타입 체크 → tsc --noEmit
3. 린트 → pnpm lint
4. 빌드 (마지막) → pnpm build
```

### 11.3 에러→수정 매핑 테이블 제공

모든 예상 가능한 에러에 대해:
- 에러 메시지
- 원인 분석
- 수정 방법
- 재시도 횟수 제한 (최대 3회)

### 11.4 템플릿이 실행을 가속화

- YAML 메타데이터 템플릿
- 컴포넌트 보일러플레이트
- 에이전트 템플릿

### 11.5 유효값 열거로 추측 방지

```
ComponentCategory (21개): hero, stats, testimonial, feature, pricing...
FunctionalTags (26개): carousel, slider, tabs, accordion, modal...
StyleTags (22개): dark-theme, light-theme, minimal, modern...
```

---

## 12. 참조 파일 경로

```
에이전트:
- .claude/agents/brand-logo-finder.md
- .claude/agents/build-and-screenshot.md
- .claude/agents/img-to-component.md

스킬:
- .claude/skills/subagent-creator/SKILL.md
- .claude/skills/subagent-creator/references/available-tools.md
- .claude/skills/subagent-creator/references/examples.md

프롬프트:
- prompt/init.md
- prompt/url-to-page.md
- prompt/img-to-component.md

스크립트:
- scripts/create-registry-component.py
- scripts/validate-metadata.ts
- scripts/generate-registry.ts
- scripts/scrape/scrape-website.ts

문서:
- docs/api.md
- docs/customization-guide.md
- docs/url-to-registry-pipeline.md
```

---

## 13. AITMPL 검증된 템플릿 활용

> 출처: https://www.aitmpl.com/ | 설치: `npx claude-code-templates@latest`

### 13.1 AITMPL 개요

커뮤니티에서 검증된 Claude Code 템플릿 레지스트리입니다.

| 카테고리 | 개수 | 용도 |
|----------|------|------|
| **Agents** | 27 카테고리 | AI 에이전트 템플릿 |
| **Commands** | 20 카테고리 | 슬래시 커맨드 |
| **Hooks** | 10 카테고리 | 자동화 훅 (pre/post) |
| **MCPs** | 11 카테고리 | Model Context Protocol |
| **Skills** | 14 카테고리 (72개 스킬) | 재사용 가능한 스킬 |
| **Settings** | 12 카테고리 | 환경 설정 |

### 13.2 주요 Agent 카테고리

| 카테고리 | 포함 에이전트 |
|----------|--------------|
| **development-tools** | code-reviewer, debugger, test-engineer, performance-profiler |
| **security** | security-auditor, penetration-tester, incident-responder |
| **data-ai** | data-scientist, ml-engineer, nlp-engineer, computer-vision-engineer |
| **devops-infrastructure** | DevOps/인프라 전문가 |
| **database** | 데이터베이스 전문가 |

### 13.3 AITMPL Agent 구조 분석

#### code-reviewer (development-tools)
```yaml
---
name: code-reviewer
description: Expert code review specialist for quality, security, maintainability.
              Use PROACTIVELY after writing or modifying code.
tools: Read, Write, Edit, Bash, Grep
model: sonnet
---
```

**워크플로우:**
1. `git diff`로 최근 변경 확인
2. 변경된 파일에 집중 분석
3. 8가지 평가 영역 체크 (명확성, 네이밍, 중복, 에러처리, 보안, 검증, 테스트, 성능)

**피드백 3단계:**
- Critical (즉시 수정 필요)
- Warnings (중요 개선)
- Suggestions (선택적 개선)

#### debugger (development-tools)
```yaml
---
name: debugger
description: Debugging specialist for errors, test failures, unexpected behavior.
tools: Read, Write, Edit, Bash, Grep
---
```

**5단계 디버깅:**
1. 에러 메시지 & 스택 트레이스 수집
2. 재현 방법 파악
3. 실패 위치 특정
4. 최소 수정 적용
5. 해결책 검증

#### security-auditor (security)
```yaml
---
name: security-auditor
description: Reviews code for vulnerabilities, implements secure authentication.
tools: Read, Write, Edit, Bash
model: opus  # 보안은 opus 모델 사용
---
```

**보안 영역:** JWT, OAuth2, OWASP Top 10, CORS/CSP, SQL 인젝션, 암호화

### 13.4 Hook 구조 (JSON 형식)

Monet에는 없는 Hook 시스템을 AITMPL에서 가져올 수 있습니다.

#### Pre-Tool Hook (수정 전 백업)
```json
{
  "type": "PreToolUse",
  "matcher": "Edit",
  "hooks": [{
    "command": "if [[ -f \"$FILE\" ]]; then cp \"$FILE\" \"$FILE.backup.$(date +%s)\"; fi"
  }]
}
```

#### Post-Tool Hook (보안 스캔)
```json
{
  "type": "PostToolUse",
  "matcher": ["Edit", "Write"],
  "hooks": [{
    "command": "semgrep scan $FILE 2>/dev/null || true; bandit $FILE 2>/dev/null || true; gitleaks detect --source $FILE 2>/dev/null || true"
  }]
}
```

**주요 Hook 카테고리:**
| 카테고리 | 용도 |
|----------|------|
| pre-tool | 도구 실행 전 (백업, 검증) |
| post-tool | 도구 실행 후 (스캔, 알림) |
| security | 보안 스캔, 파일 보호 |
| git | Git 워크플로우 자동화 |
| testing | 테스트 자동 실행 |

### 13.5 MCP 구조 (JSON 형식)

#### PostgreSQL 연동
```json
{
  "mcpServers": {
    "postgresql": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost:5432/db"
      }
    }
  }
}
```

#### Supabase 연동
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server@latest", "--read-only", "--project-ref", "YOUR_PROJECT_REF"],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "YOUR_ACCESS_TOKEN"
      }
    }
  }
}
```

**주요 MCP 카테고리:**
| 카테고리 | 포함 MCP |
|----------|----------|
| database | PostgreSQL, MySQL, Supabase, Neon |
| browser_automation | 브라우저 자동화 |
| filesystem | 파일 시스템 작업 |
| web | 웹 관련 기능 |
| productivity | 생산성 도구 |

### 13.6 Skill 구조 (폴더 기반)

AITMPL 스킬은 Monet과 유사하지만 scripts 폴더를 포함합니다.

```
skill-name/
├── SKILL.md           # YAML frontmatter + 문서
├── references/        # 참조 자료
└── scripts/           # 자동화 스크립트 (AITMPL 특징)
```

#### test-driven-development 스킬
```yaml
---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code
---
```

**핵심 원칙:**
> "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"

**Red-Green-Refactor 사이클:**
1. **RED**: 실패하는 테스트 작성
2. **Verify RED**: 실패 확인 (필수!)
3. **GREEN**: 테스트 통과하는 최소 코드
4. **Verify GREEN**: 통과 확인
5. **REFACTOR**: 코드 정리 (green 유지)

---

## 14. Monet + AITMPL 통합 전략

### 14.1 두 접근 방식 비교

| 측면 | Monet | AITMPL |
|------|-------|--------|
| **복잡도** | 높음 (287줄 에이전트) | 중간 (간결한 정의) |
| **특화** | 이미지→컴포넌트 | 범용 개발 도구 |
| **Hook** | 없음 | JSON 기반 pre/post |
| **MCP** | nanobanana, sharp | DB, 브라우저, 웹 (11종) |
| **Skill** | references 중심 | scripts 포함 |
| **강점** | 도메인 특화 상세 가이드 | 검증된 범용 패턴 |

### 14.2 통합 활용 방법

**원칙:** Monet 스타일로 도메인 특화 에이전트 작성 + AITMPL에서 범용 도구 가져오기

#### Step 1: AITMPL 기본 도구 설치
```bash
# 필수 에이전트
npx claude-code-templates@latest --agent development-tools/code-reviewer
npx claude-code-templates@latest --agent development-tools/debugger
npx claude-code-templates@latest --agent security/security-auditor

# 필수 훅
npx claude-code-templates@latest --hook pre-tool/backup-before-edit
npx claude-code-templates@latest --hook security/security-scanner

# 필수 스킬
npx claude-code-templates@latest --skill development/test-driven-development
```

#### Step 2: 프로젝트별 MCP 설치
```bash
# 데이터베이스 프로젝트
npx claude-code-templates@latest --mcp database/postgresql-integration
npx claude-code-templates@latest --mcp database/supabase

# 웹 프로젝트
npx claude-code-templates@latest --mcp web
npx claude-code-templates@latest --mcp browser_automation
```

#### Step 3: Monet 스타일로 도메인 특화 에이전트 작성

AITMPL 에이전트를 기반으로 프로젝트에 맞게 확장:

```markdown
# .claude/agents/my-domain-specialist.md
---
name: my-domain-specialist
description: [프로젝트 특화 설명]. Use PROACTIVELY when [사용 시점].
tools: Read, Write, Edit, Bash, Grep
model: inherit
---

[Monet 스타일의 상세한 시스템 프롬프트]

## 참조 파일
- src/types/my-schema.ts
- docs/my-conventions.md

## 유효값
[프로젝트 특화 enum 목록]

## 단계별 프로세스
1. [상세 단계]
2. [상세 단계]
...

## 에러 자동수정
| 에러 | 수정 방법 |
|------|----------|
| ... | ... |

## 주의사항
- 절대 하지 말 것 목록
```

### 14.3 프로젝트 유형별 추천 조합

#### 웹 프론트엔드
```bash
# AITMPL
--agent development-tools/code-reviewer
--agent development-tools/performance-profiler
--hook pre-tool/backup-before-edit
--skill development/test-driven-development

# + Monet 스타일 커스텀
.claude/agents/component-builder.md (img-to-component 참조)
```

#### 백엔드/API
```bash
# AITMPL
--agent security/api-security-audit
--agent development-tools/debugger
--mcp database/postgresql-integration
--hook security/security-scanner

# + Monet 스타일 커스텀
.claude/agents/api-designer.md
```

#### 데이터/AI
```bash
# AITMPL
--agent data-ai/data-scientist
--agent data-ai/ml-engineer
--mcp database/supabase
--skill development/test-driven-development

# + Monet 스타일 커스텀
.claude/agents/pipeline-orchestrator.md
```

### 14.4 결합된 디렉토리 구조

```
your-project/
├── .claude/
│   ├── agents/
│   │   ├── code-reviewer.md      # AITMPL에서 설치
│   │   ├── debugger.md           # AITMPL에서 설치
│   │   └── my-specialist.md      # Monet 스타일로 직접 작성
│   ├── skills/
│   │   └── test-driven-development/  # AITMPL에서 설치
│   ├── hooks.json                # AITMPL Hook 통합
│   └── settings.json
├── .mcp.json                     # AITMPL MCP 설정
├── prompt/                       # Monet 스타일 워크플로우
│   └── init.md
└── scripts/                      # Monet 스타일 자동화
    └── create-*.py
```

---

## 15. AITMPL CLI 명령어 레퍼런스

### 15.1 컴포넌트 설치
```bash
# 에이전트
npx claude-code-templates@latest --agent <category>/<name>
npx claude-code-templates@latest --agent security/security-auditor

# 커맨드
npx claude-code-templates@latest --command <category>/<name>

# MCP
npx claude-code-templates@latest --mcp <category>/<name>

# 훅
npx claude-code-templates@latest --hook <category>/<name>

# 스킬
npx claude-code-templates@latest --skill <category>/<name>

# 설정
npx claude-code-templates@latest --setting <category>
```

### 15.2 유틸리티
```bash
# 분석 대시보드
npx claude-code-templates@latest --analytics

# 헬스 체크
npx claude-code-templates@latest --health-check

# 스킬 매니저
npx claude-code-templates@latest --skills-manager

# 플러그인 대시보드
npx claude-code-templates@latest --plugins

# 설치된 에이전트 목록
npx claude-code-templates@latest --list-agents
```

### 15.3 고급 옵션
```bash
# 특정 디렉토리에 설치
npx claude-code-templates@latest --agent code-reviewer -d ./my-project

# 드라이런 (실제 설치 없이 확인)
npx claude-code-templates@latest --agent code-reviewer --dry-run

# 여러 컴포넌트 한번에 설치
npx claude-code-templates@latest --agent code-reviewer,debugger --hook security-scanner
```

---

## 16. AITMPL 자동화 도구 구현

### 16.1 자동 인덱싱 스크립트

Git clone 방식으로 rate limit 없이 전체 템플릿 목록을 가져오는 스크립트입니다.

#### scripts/sync_aitmpl_index.py

```python
#!/usr/bin/env python3
"""
AITMPL 템플릿 자동 인덱싱 스크립트
Git clone 방식으로 rate limit 없이 전체 목록 가져오기
"""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

REPO_URL = "https://github.com/davila7/claude-code-templates.git"
COMPONENTS_PATH = "cli-tool/components"
OUTPUT_FILE = ".claude/aitmpl-index.json"
CATEGORIES = ["agents", "commands", "hooks", "mcps", "skills", "settings"]

def clone_repo(temp_dir: str) -> bool:
    """Git clone (shallow) - no rate limit!"""
    try:
        print("Cloning repository (shallow)...")
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, temp_dir],
            check=True, capture_output=True, text=True
        )
        print("Clone complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git clone failed: {e}")
        return False

def scan_category(base_path: Path, category: str) -> dict:
    """Scan local directory for templates"""
    items = {}
    category_path = base_path / COMPONENTS_PATH / category
    if not category_path.exists():
        return items

    for subdir in sorted(category_path.iterdir()):
        if subdir.is_dir():
            templates = []
            for file in sorted(subdir.iterdir()):
                if file.is_file() and file.suffix in [".md", ".json"]:
                    templates.append({"name": file.stem, "file": file.name})
                elif file.is_dir():  # Handle nested skill folders
                    skill_file = file / "SKILL.md"
                    if skill_file.exists():
                        templates.append({"name": file.name, "file": f"{file.name}/SKILL.md"})
            if templates:
                items[subdir.name] = templates
    return items

def build_index_from_clone() -> dict:
    """Build index using git clone"""
    index = {"version": "1.0", "updated_at": datetime.now().isoformat(),
             "source": "https://github.com/davila7/claude-code-templates",
             "method": "git-clone", "categories": {}}

    temp_dir = tempfile.mkdtemp(prefix="aitmpl_")
    try:
        if clone_repo(temp_dir):
            for category in CATEGORIES:
                print(f"Scanning {category}...")
                index["categories"][category] = scan_category(Path(temp_dir), category)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    return index

if __name__ == "__main__":
    index = build_index_from_clone()
    # save index...
```

#### 사용법
```bash
# 수동 실행 (토큰 불필요!)
python scripts/aitmpl_manager.py sync

# cron으로 주기적 실행 (매주 일요일)
0 0 * * 0 cd /path/to/project && python scripts/aitmpl_manager.py sync
```

#### GitHub Actions 워크플로우
```yaml
# .github/workflows/sync-aitmpl.yml
name: Sync AITMPL Index

on:
  schedule:
    - cron: '0 0 * * 0'  # 매주 일요일 자정
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Sync AITMPL index (no token needed)
        run: python scripts/aitmpl_manager.py sync

      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add .claude/aitmpl-index.json
          git diff --staged --quiet || git commit -m "chore: sync AITMPL index"
          git push
```

---

### 16.2 태그 기반 검색 스크립트

용도별로 템플릿을 빠르게 찾는 검색 도구입니다.

#### scripts/search_aitmpl.py

```python
#!/usr/bin/env python3
"""
AITMPL 템플릿 태그 기반 검색
용도별로 적절한 템플릿을 빠르게 찾기
"""

import json
import argparse
from pathlib import Path

INDEX_FILE = ".claude/aitmpl-index.json"

# 태그 → 템플릿 매핑
TAG_MAPPINGS = {
    # 용도별 태그
    "review": ["agents/development-tools/code-reviewer", "agents/development-tools/code-simplifier"],
    "debug": ["agents/development-tools/debugger", "agents/development-tools/error-detective"],
    "test": ["agents/development-tools/test-engineer", "skills/development/test-driven-development"],
    "security": ["agents/security/security-auditor", "agents/security/api-security-audit", "hooks/security/security-scanner"],
    "git": ["commands/git/feature", "commands/git/hotfix", "hooks/git"],
    "database": ["mcps/database/postgresql-integration", "mcps/database/supabase", "agents/database"],
    "ai": ["agents/data-ai/data-scientist", "agents/data-ai/ml-engineer", "agents/data-ai/nlp-engineer"],
    "devops": ["agents/devops-infrastructure", "commands/deployment"],
    "docs": ["agents/documentation", "commands/documentation"],
    "performance": ["agents/development-tools/performance-profiler", "hooks/performance"],

    # 프로젝트 유형별
    "frontend": ["review", "test", "performance"],
    "backend": ["security", "database", "debug"],
    "fullstack": ["frontend", "backend", "git"],
    "ml": ["ai", "database", "test"],
}

def load_index() -> dict:
    """인덱스 파일 로드"""
    index_path = Path(INDEX_FILE)
    if not index_path.exists():
        print(f"Error: Index file not found. Run sync_aitmpl_index.py first.")
        return {}

    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)

def resolve_tags(tags: list) -> set:
    """태그를 실제 템플릿 경로로 확장"""
    resolved = set()

    for tag in tags:
        if tag in TAG_MAPPINGS:
            for item in TAG_MAPPINGS[tag]:
                if item in TAG_MAPPINGS:
                    # 중첩 태그 해결
                    resolved.update(resolve_tags([item]))
                else:
                    resolved.add(item)
        else:
            resolved.add(tag)

    return resolved

def search_templates(query: str, index: dict) -> list:
    """쿼리로 템플릿 검색"""
    results = []
    query_lower = query.lower()

    for category, subcats in index.get("categories", {}).items():
        for subcat, templates in subcats.items():
            for tmpl in templates:
                name = tmpl.get("name", "").lower()
                if query_lower in name or query_lower in subcat.lower():
                    results.append({
                        "category": category,
                        "subcategory": subcat,
                        "name": tmpl["name"],
                        "install_cmd": f"npx claude-code-templates@latest --{category.rstrip('s')} {subcat}/{tmpl['name']}"
                    })

    return results

def search_by_tags(tags: list) -> list:
    """태그로 검색"""
    resolved = resolve_tags(tags)
    results = []

    for path in resolved:
        parts = path.split("/")
        if len(parts) >= 2:
            category = parts[0]
            rest = "/".join(parts[1:])
            cmd_type = category.rstrip("s")  # agents -> agent
            results.append({
                "path": path,
                "install_cmd": f"npx claude-code-templates@latest --{cmd_type} {rest}"
            })

    return results

def print_results(results: list, format_type: str = "table"):
    """결과 출력"""
    if not results:
        print("No results found.")
        return

    if format_type == "commands":
        # 설치 명령어만 출력
        for r in results:
            print(r.get("install_cmd", ""))
    elif format_type == "json":
        print(json.dumps(results, indent=2))
    else:
        # 테이블 형식
        print(f"\n{'Template':<50} {'Category':<15}")
        print("-" * 70)
        for r in results:
            name = r.get("name") or r.get("path", "")
            cat = r.get("category", "")
            print(f"{name:<50} {cat:<15}")
        print(f"\nTotal: {len(results)} templates")

def main():
    parser = argparse.ArgumentParser(description="Search AITMPL templates by tag or keyword")
    parser.add_argument("query", nargs="*", help="Search query or tags")
    parser.add_argument("-t", "--tags", nargs="+", help="Search by tags (e.g., -t review security)")
    parser.add_argument("-f", "--format", choices=["table", "commands", "json"], default="table")
    parser.add_argument("--list-tags", action="store_true", help="List available tags")

    args = parser.parse_args()

    if args.list_tags:
        print("Available tags:")
        for tag, items in sorted(TAG_MAPPINGS.items()):
            print(f"  {tag}: {', '.join(items[:3])}{'...' if len(items) > 3 else ''}")
        return

    if args.tags:
        results = search_by_tags(args.tags)
        print_results(results, args.format)
    elif args.query:
        index = load_index()
        for q in args.query:
            results = search_templates(q, index)
            print(f"\n=== Results for '{q}' ===")
            print_results(results, args.format)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

#### 사용법
```bash
# 태그로 검색
python scripts/search_aitmpl.py -t review security
python scripts/search_aitmpl.py -t frontend
python scripts/search_aitmpl.py -t ml database

# 키워드로 검색
python scripts/search_aitmpl.py debugger
python scripts/search_aitmpl.py "code-reviewer"

# 설치 명령어만 출력
python scripts/search_aitmpl.py -t security -f commands

# 사용 가능한 태그 목록
python scripts/search_aitmpl.py --list-tags
```

#### 출력 예시
```
$ python scripts/search_aitmpl.py -t security

Template                                           Category
----------------------------------------------------------------------
agents/security/security-auditor                   agents
agents/security/api-security-audit                 agents
hooks/security/security-scanner                    hooks

Total: 3 templates

$ python scripts/search_aitmpl.py -t security -f commands
npx claude-code-templates@latest --agent security/security-auditor
npx claude-code-templates@latest --agent security/api-security-audit
npx claude-code-templates@latest --hook security/security-scanner
```

---

### 16.3 커스텀 조합 저장 (프로젝트별 템플릿 세트)

프로젝트 유형별로 미리 정의된 템플릿 세트를 저장하고 한번에 설치합니다.

#### .claude/template-sets.yaml

```yaml
# 프로젝트별 템플릿 세트 정의
version: "1.0"

sets:
  # 웹 프론트엔드 프로젝트
  frontend:
    description: "React/Vue/Next.js 프론트엔드 프로젝트용"
    agents:
      - development-tools/code-reviewer
      - development-tools/performance-profiler
      - development-tools/debugger
    hooks:
      - pre-tool/backup-before-edit
      - testing/auto-test
    skills:
      - development/test-driven-development
      - development/code-reviewer
    commands:
      - git/feature
      - git/hotfix

  # 백엔드 API 프로젝트
  backend:
    description: "Node.js/Python/Go 백엔드 API 프로젝트용"
    agents:
      - development-tools/code-reviewer
      - development-tools/debugger
      - security/security-auditor
      - security/api-security-audit
    hooks:
      - pre-tool/backup-before-edit
      - security/security-scanner
    mcps:
      - database/postgresql-integration
    skills:
      - development/test-driven-development

  # 풀스택 프로젝트
  fullstack:
    description: "프론트엔드 + 백엔드 통합 프로젝트"
    extends:
      - frontend
      - backend
    agents:
      - devops-infrastructure/deployment-engineer

  # 데이터/AI 프로젝트
  data-ai:
    description: "ML/AI/데이터 분석 프로젝트용"
    agents:
      - data-ai/data-scientist
      - data-ai/ml-engineer
      - data-ai/nlp-engineer
      - development-tools/debugger
    mcps:
      - database/postgresql-integration
      - database/supabase
    skills:
      - development/test-driven-development

  # DevOps 프로젝트
  devops:
    description: "인프라/배포 자동화 프로젝트용"
    agents:
      - devops-infrastructure/deployment-engineer
      - devops-infrastructure/terraform-specialist
      - security/security-auditor
    commands:
      - deployment/docker-deploy
      - deployment/kubernetes-deploy
    hooks:
      - security/security-scanner

  # 최소 필수 세트
  minimal:
    description: "모든 프로젝트에 필요한 최소 필수 템플릿"
    agents:
      - development-tools/code-reviewer
      - development-tools/debugger
    hooks:
      - pre-tool/backup-before-edit
    skills:
      - development/test-driven-development
```

#### scripts/install_template_set.py

```python
#!/usr/bin/env python3
"""
프로젝트별 템플릿 세트 설치 스크립트
.claude/template-sets.yaml에서 정의된 세트를 한번에 설치
"""

import yaml
import subprocess
import argparse
from pathlib import Path

SETS_FILE = ".claude/template-sets.yaml"

def load_sets() -> dict:
    """템플릿 세트 정의 로드"""
    sets_path = Path(SETS_FILE)
    if not sets_path.exists():
        print(f"Error: {SETS_FILE} not found")
        return {}

    with open(sets_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def resolve_set(sets_data: dict, set_name: str, resolved: set = None) -> dict:
    """세트 확장 (extends 처리)"""
    if resolved is None:
        resolved = set()

    if set_name in resolved:
        return {}  # 순환 참조 방지

    resolved.add(set_name)

    set_def = sets_data.get("sets", {}).get(set_name, {})
    result = {
        "agents": list(set_def.get("agents", [])),
        "commands": list(set_def.get("commands", [])),
        "hooks": list(set_def.get("hooks", [])),
        "mcps": list(set_def.get("mcps", [])),
        "skills": list(set_def.get("skills", [])),
        "settings": list(set_def.get("settings", [])),
    }

    # extends 처리
    for parent in set_def.get("extends", []):
        parent_result = resolve_set(sets_data, parent, resolved)
        for key in result:
            result[key].extend(parent_result.get(key, []))

    # 중복 제거
    for key in result:
        result[key] = list(dict.fromkeys(result[key]))

    return result

def generate_install_commands(templates: dict) -> list:
    """설치 명령어 생성"""
    commands = []

    type_map = {
        "agents": "agent",
        "commands": "command",
        "hooks": "hook",
        "mcps": "mcp",
        "skills": "skill",
        "settings": "setting",
    }

    for category, items in templates.items():
        if items:
            cmd_type = type_map.get(category, category)
            for item in items:
                commands.append(f"npx claude-code-templates@latest --{cmd_type} {item}")

    return commands

def install_set(set_name: str, dry_run: bool = False):
    """템플릿 세트 설치"""
    sets_data = load_sets()

    if set_name not in sets_data.get("sets", {}):
        print(f"Error: Set '{set_name}' not found")
        print(f"Available sets: {', '.join(sets_data.get('sets', {}).keys())}")
        return

    set_def = sets_data["sets"][set_name]
    print(f"\n📦 Installing template set: {set_name}")
    print(f"   {set_def.get('description', '')}\n")

    templates = resolve_set(sets_data, set_name)
    commands = generate_install_commands(templates)

    if not commands:
        print("No templates to install.")
        return

    print(f"Templates to install ({len(commands)}):")
    for cmd in commands:
        print(f"  • {cmd.split('--')[1]}")

    if dry_run:
        print("\n[DRY RUN] Commands that would be executed:")
        for cmd in commands:
            print(f"  {cmd}")
        return

    print("\n🚀 Installing...")
    for cmd in commands:
        print(f"\n> {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Failed: {e}")

    print("\n✅ Installation complete!")

def list_sets():
    """사용 가능한 세트 목록"""
    sets_data = load_sets()

    print("\n📋 Available Template Sets:\n")
    for name, set_def in sets_data.get("sets", {}).items():
        desc = set_def.get("description", "No description")

        # 템플릿 수 계산
        templates = resolve_set(sets_data, name)
        total = sum(len(v) for v in templates.values())

        print(f"  {name:<15} ({total} templates)")
        print(f"    └─ {desc}")

        # extends 표시
        if set_def.get("extends"):
            print(f"    └─ extends: {', '.join(set_def['extends'])}")
        print()

def main():
    parser = argparse.ArgumentParser(description="Install AITMPL template sets")
    parser.add_argument("set_name", nargs="?", help="Template set to install")
    parser.add_argument("-l", "--list", action="store_true", help="List available sets")
    parser.add_argument("--dry-run", action="store_true", help="Show commands without executing")
    parser.add_argument("-d", "--details", help="Show details of a specific set")

    args = parser.parse_args()

    if args.list:
        list_sets()
    elif args.details:
        sets_data = load_sets()
        templates = resolve_set(sets_data, args.details)
        print(f"\n📦 Set: {args.details}")
        print(yaml.dump(templates, default_flow_style=False))
    elif args.set_name:
        install_set(args.set_name, args.dry_run)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

#### 사용법
```bash
# 사용 가능한 세트 목록
python scripts/install_template_set.py --list

# 세트 상세 내용 확인
python scripts/install_template_set.py -d frontend

# 드라이런 (실제 설치 없이 확인)
python scripts/install_template_set.py frontend --dry-run

# 실제 설치
python scripts/install_template_set.py frontend
python scripts/install_template_set.py backend
python scripts/install_template_set.py fullstack
```

#### 출력 예시
```
$ python scripts/install_template_set.py --list

📋 Available Template Sets:

  frontend        (8 templates)
    └─ React/Vue/Next.js 프론트엔드 프로젝트용

  backend         (9 templates)
    └─ Node.js/Python/Go 백엔드 API 프로젝트용

  fullstack       (18 templates)
    └─ 프론트엔드 + 백엔드 통합 프로젝트
    └─ extends: frontend, backend

  data-ai         (8 templates)
    └─ ML/AI/데이터 분석 프로젝트용

  minimal         (4 templates)
    └─ 모든 프로젝트에 필요한 최소 필수 템플릿

$ python scripts/install_template_set.py frontend --dry-run

📦 Installing template set: frontend
   React/Vue/Next.js 프론트엔드 프로젝트용

Templates to install (8):
  • agent development-tools/code-reviewer
  • agent development-tools/performance-profiler
  • agent development-tools/debugger
  • hook pre-tool/backup-before-edit
  • hook testing/auto-test
  • skill development/test-driven-development
  • command git/feature
  • command git/hotfix

[DRY RUN] Commands that would be executed:
  npx claude-code-templates@latest --agent development-tools/code-reviewer
  npx claude-code-templates@latest --agent development-tools/performance-profiler
  ...
```

---

### 16.4 통합 CLI 래퍼 (선택적)

위 3가지 기능을 하나의 CLI로 통합할 수 있습니다.

#### scripts/aitmpl_manager.py

```python
#!/usr/bin/env python3
"""
AITMPL 템플릿 매니저 - 통합 CLI
"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description="AITMPL Template Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sync                    # 인덱스 업데이트
  %(prog)s search -t security      # 태그로 검색
  %(prog)s search debugger         # 키워드로 검색
  %(prog)s install frontend        # 세트 설치
  %(prog)s install frontend --dry-run
  %(prog)s list-sets               # 세트 목록
  %(prog)s list-tags               # 태그 목록
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # sync 명령
    subparsers.add_parser("sync", help="Sync index from GitHub")

    # search 명령
    search_parser = subparsers.add_parser("search", help="Search templates")
    search_parser.add_argument("query", nargs="*")
    search_parser.add_argument("-t", "--tags", nargs="+")
    search_parser.add_argument("-f", "--format", choices=["table", "commands", "json"])

    # install 명령
    install_parser = subparsers.add_parser("install", help="Install template set")
    install_parser.add_argument("set_name")
    install_parser.add_argument("--dry-run", action="store_true")

    # list 명령
    subparsers.add_parser("list-sets", help="List available template sets")
    subparsers.add_parser("list-tags", help="List available search tags")

    args = parser.parse_args()

    if args.command == "sync":
        from sync_aitmpl_index import build_index, save_index
        index = build_index()
        save_index(index)
    elif args.command == "search":
        from search_aitmpl import search_by_tags, search_templates, print_results, load_index
        if args.tags:
            results = search_by_tags(args.tags)
        else:
            index = load_index()
            results = search_templates(" ".join(args.query), index)
        print_results(results, args.format or "table")
    elif args.command == "install":
        from install_template_set import install_set
        install_set(args.set_name, args.dry_run)
    elif args.command == "list-sets":
        from install_template_set import list_sets
        list_sets()
    elif args.command == "list-tags":
        from search_aitmpl import TAG_MAPPINGS
        for tag, items in sorted(TAG_MAPPINGS.items()):
            print(f"{tag}: {', '.join(items[:3])}...")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

#### 단축 alias 설정
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
alias aitmpl="python scripts/aitmpl_manager.py"

# 사용
aitmpl sync
aitmpl search -t security
aitmpl install frontend
```

---

## 17. 참고 링크

**Monet Registry:**
- GitHub: https://github.com/[monet-registry]

**AITMPL:**
- 공식 사이트: https://www.aitmpl.com/
- 문서: https://docs.aitmpl.com/
- GitHub: https://github.com/davila7/claude-code-templates
- Discord: https://discord.gg/dyTTwzBhwY

**인덱스 문서:**
- `C:\source\guide\aitmpl-index.md` - AITMPL 전체 카탈로그

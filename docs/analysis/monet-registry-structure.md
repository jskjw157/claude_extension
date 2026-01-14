# monet-registry 구조 분석: .claude 및 prompt 디렉토리

## 1. 개요
`monet-registry` 프로젝트는 AI 에이전트(`brand-logo-finder`, `img-to-component` 등)와 스킬 시스템을 통해 UI 컴포넌트 생성 및 빌드 자동화를 구현하고 있습니다. 이 문서는 해당 프로젝트의 에이전트 시스템 디렉토리 구조를 분석하고 맵핑합니다.

## 2. 디렉토리 구조 맵핑

### 2.1 .claude/ (에이전트 및 스킬 정의)

`.claude` 디렉토리는 Claude Code CLI가 인식하는 에이전트와 스킬의 정의를 담고 있습니다.

```
.claude/
├── agents/                       # 전문화된 에이전트 정의 (.md)
│   ├── brand-logo-finder.md      # 브랜드 로고 및 자산 검색 에이전트
│   ├── build-and-screenshot.md   # 컴포넌트 빌드, 검증, 스크린샷 캡처 에이전트 (Docker 활용)
│   └── img-to-component.md       # 이미지를 React 컴포넌트 코드로 변환하는 에이전트
│
└── skills/                       # 에이전트가 사용하는 도구(Skill) 모음
    └── subagent-creator/         # 하위 에이전트를 생성하는 메타 스킬
        ├── SKILL.md              # 스킬 정의 및 메타데이터 (YAML Frontmatter)
        ├── assets/               # 스킬 실행에 필요한 템플릿 파일
        │   └── subagent-template.md
        └── references/           # 스킬 실행 시 참조하는 문서
            ├── available-tools.md
            └── examples.md
```

### 2.2 prompt/ (프롬프트 자산)

`prompt` 디렉토리는 에이전트가 작업을 수행할 때 참조하거나, 사용자가 직접 실행할 수 있는 다양한 목적의 프롬프트 파일들을 관리합니다. `img-to-component`와 같은 핵심 기능은 `.claude/agents`와 `prompt` 디렉토리 양쪽에 관련 파일이 존재하여, 에이전트 정의와 실행 프롬프트가 분리되어 관리됨을 알 수 있습니다.

```
prompt/
├── create-check-list.md      # 체크리스트 생성 프롬프트
├── feature-carousel.md       # 기능 카러셀 생성 관련 프롬프트
├── img-to-component.md       # 이미지 -> 컴포넌트 변환 상세 가이드 (에이전트 정의와 별도로 존재)
├── init.md                   # 프로젝트 초기화 가이드 프롬프트
├── url-to-page.md            # URL -> 페이지 변환(스크래핑 포함) 상세 가이드
└── use-existing-images.md    # 기존 이미지 활용 가이드
```

## 3. 구조적 특징 및 시사점

1.  **에이전트와 프롬프트의 분리**: 
    - `.claude/agents/`에는 에이전트의 페르소나, 역할, 사용 도구(Tools) 등 정체성을 정의합니다.
    - `prompt/`에는 구체적인 작업 지시사항, 코드 구현 규칙, 스타일 가이드 등 상세 로직을 정의합니다.
    - 예: `img-to-component`는 에이전트 정의(.claude)와 상세 가이드(prompt)가 짝을 이룹니다.

2.  **스킬의 모듈화**:
    - `.claude/skills/` 하위에 각 스킬별로 독립된 디렉토리를 구성하고, `SKILL.md`를 통해 명세합니다.
    - `subagent-creator`와 같이 복잡한 스킬은 `assets`와 `references`를 두어 필요한 리소스를 체계적으로 관리합니다.

3.  **역할 중심의 에이전트 분할**:
    - 검색(`brand-logo-finder`), 코딩(`img-to-component`), 검증/배포(`build-and-screenshot`)로 역할이 명확히 분리되어 있어 유지보수와 확장이 용이합니다.

# Coordinate Subagents

[English](README.md)

`coordinate-subagents`는 작업을 서브에이전트에게 맡길지 판단하고, 서로 독립적인 작업을 나누며, 공유 상태를 조정하는 Codex 스킬입니다. 위험도가 높은 변경에는 구현 담당자와 다른 검토자를 배정합니다.

이 저장소는 처음부터 여러 스킬을 담을 수 있는 구조로 만들었습니다. 현재 배포 대상은 [`skills/coordinate-subagents`](skills/coordinate-subagents)에 있는 단일 스킬입니다. 나중에 전문 스킬과 오케스트레이터를 추가하더라도 모든 지침을 하나의 거대한 스킬로 합칠 필요가 없습니다.

> **커뮤니티 프로젝트:** 이 저장소는 OpenAI 공식 프로젝트가 아니며 OpenAI의 보증이나 승인을 받지 않았습니다.

## 주요 기능

- 작업을 나누기 전에 독립 작업, 순차 작업, 원자적 작업을 구분합니다.
- 담당 범위, 입력, 제약, 산출물, 완료 조건, 검증 기준을 위임 내용에 포함합니다.
- 같은 파일이나 상태를 여러 에이전트가 다룰 때 쓰기 순서와 소유권을 조정합니다.
- 보안, 권한, 결제, 데이터 손실, 마이그레이션, 배포, 전역 설정 변경에는 별도 검토자를 둡니다.
- 최종 통합과 결과에 대한 책임은 조정 역할을 맡은 에이전트가 유지합니다.
- Luna, Terra, Sol, Astra를 위한 선택형 모델 라우팅 프로필을 제공하되, 현재 호스트가 지원하는 모델과 추론 수준 안에서만 적용합니다.

모델 라우팅 프로필은 관리자가 권장하는 기본값이며 필수 설정이 아닙니다. 사용자 지시, 저장소 규칙, 호스트 기능, 실행 제한이 우선합니다. 자세한 내용은 [`model-routing.md`](skills/coordinate-subagents/references/model-routing.md)를 참고하세요.

## 설치

내장 `$skill-installer`에 GitHub 폴더 URL을 전달합니다.

```text
$skill-installer install https://github.com/jaeseongs95/coordinate-subagents/tree/main/skills/coordinate-subagents
```

위 내용은 셸 명령어가 아니라 Codex 프롬프트로 입력합니다.

`v0.1.0`이 공개된 뒤 해당 버전으로 고정하려면 다음과 같이 설치합니다.

```text
$skill-installer install https://github.com/jaeseongs95/coordinate-subagents/tree/v0.1.0/skills/coordinate-subagents
```

Codex는 새로 설치한 스킬을 보통 자동으로 감지합니다. 목록에 나타나지 않으면 Codex를 다시 시작하세요. 로컬 설치와 스킬 탐색 방식은 [OpenAI 공식 스킬 문서](https://learn.chatgpt.com/docs/build-skills)에서 확인할 수 있습니다.

## 사용법

작업에 위임을 명시적으로 적용하려면 프롬프트에서 스킬을 호출합니다.

```text
$coordinate-subagents 이 작업을 독립 실행 단위로 나누고, 안전한 작업은 병렬로 진행한 뒤 검증된 결과를 통합해줘.
```

자동 호출도 허용합니다. 요청이 병렬 위임, 쓰기 소유권 조정, 고위험 작업의 독립 검토와 분명히 맞으면 Codex가 이 스킬을 선택할 수 있습니다. 자동 선택 여부는 스킬 설명과 현재 호스트의 스킬 설정에 따라 달라집니다.

이 스킬을 설치하거나 호출해도 권한이 추가되거나 승인이 생략되지는 않습니다. 사용자가 요청한 작업 범위도 넓어지지 않으며, 사용할 수 없던 도구나 모델이 새로 활성화되지 않습니다. 모든 서브에이전트에는 사용자 지시, 저장소 규칙, 실행 모드, 샌드박스, 권한, 도구 접근 제한이 그대로 적용됩니다.

## 저장소 구조

```text
coordinate-subagents/
├── skills/
│   └── coordinate-subagents/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── references/
├── tests/
├── README.md
├── README.ko.md
└── LICENSE
```

새 워크플로는 `skills/<skill-name>/` 아래에 역할이 분명한 독립 스킬로 추가합니다. 여러 워크플로를 한 번에 다룰 진입점이 필요하면 오케스트레이터 스킬을 별도로 둡니다. 오케스트레이터는 요청을 분류하고 필요한 스킬을 고른 뒤, 입출력 순서와 중간 검증을 관리하고 최종 결과를 합치는 역할만 맡습니다.

## 플러그인 확장 계획

앞으로 다음과 같은 구조로 확장할 수 있습니다.

```text
coordinate-subagents/
├── plugin.json                  # 플러그인 패키징을 시작할 때 추가
├── skills/
│   ├── workflow-orchestrator/   # 분기와 통합
│   ├── coordinate-subagents/    # 위임과 검토 정책
│   ├── requirements/            # 향후 전문 스킬
│   ├── design/                  # 향후 전문 스킬
│   ├── validation/              # 향후 전문 스킬
│   └── packaging/               # 향후 전문 스킬
└── ...
```

현재 릴리스에는 `plugin.json`을 넣지 않습니다. 지금은 `coordinate-subagents`만 독립 스킬로 배포합니다. 여러 스킬이 준비되면 저장소 루트에 이식 가능한 플러그인 매니페스트를 추가하고, 기존 `skills/` 구조를 옮기지 않은 채 하나의 플러그인으로 묶을 수 있습니다. 자세한 형식은 OpenAI 공식 [스킬 제작 문서](https://learn.chatgpt.com/docs/build-skills)와 [플러그인 패키징 문서](https://developers.openai.com/plugins/build/plugins)를 참고하세요.

## 라이선스

[MIT](LICENSE)

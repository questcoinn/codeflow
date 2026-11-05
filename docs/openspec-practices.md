## OpenSpec에 SDD 방안 적용하기

[spec-driven-development.md](spec-driven-development.md)에서 정리한 SDD의 문제점과 방안을 OpenSpec에서 어떻게 적용하는지 정리한 문서입니다. git으로 관리하는 방법은 [openspec-git-workflow.md](openspec-git-workflow.md)에 따로 있습니다.

### 용어 대응

| 일반 용어 | OpenSpec |
|---|---|
| 스펙 변경 | change (`openspec/changes/<이름>/`) |
| 현재 스펙 | main specs (`openspec/specs/<capability>/spec.md`) |
| 바뀌는 부분만 적은 스펙 | delta spec (change 안의 `specs/`) |
| 제안서 / 설계 / 작업 목록 | `proposal.md` / `design.md` / `tasks.md` |
| 변경 기록 | `openspec/changes/archive/YYYY-MM-DD-<이름>/` |
| 요구사항 + 시나리오 | Requirement + Scenario (WHEN/THEN) |
| 변경 진행 순서 | propose → apply → archive |

OpenSpec은 처음부터 change 단위로 delta spec만 쓰는 점진적 방식이라, 문제점 1(워터폴)은 도구가 아니라 하나의 change에 너무 많은 범위를 담을 때 생깁니다.

### 기본 스키마에 이미 들어 있는 규칙

기본 `spec-driven` 스키마(`schemas/spec-driven/schema.yaml`)의 artifact 지침은 스킬이 `openspec instructions`로 받아 와 에이전트에게 매번 전달합니다. 아래 내용은 config.yaml에 다시 넣으면 중복입니다.

- **spec 형식**: requirement는 `### Requirement: <이름>`과 SHALL/MUST로, scenario는 `#### Scenario: <이름>`과 **WHEN/THEN**으로 적습니다(GIVEN은 쓰지 않음). requirement마다 scenario가 최소 하나 있어야 합니다. scenario 제목의 `#`이 4개가 아니면 경고 없이 실패합니다.
- **spec에 넣지 않을 것**: 내부 클래스·함수 이름, 라이브러리 선택, 구현 단계. 기준은 "구현을 바꿔도 외부 동작이 바뀌지 않으면 spec에 넣지 않는다"입니다.
- **design.md**: 아키텍처 변경, 새 의존성, 보안·마이그레이션 이슈 등이 있을 때만 만듭니다.
- **tasks.md**: task마다 완료를 확인하는 방법(테스트, 명령, 관찰 가능한 동작)을 적습니다. 각 scenario는 잠재적인 테스트 케이스로 봅니다.

config.yaml에는 스키마에 없는 규칙만 넣습니다. 원본과 조금이라도 다르게 다시 적으면 에이전트가 어느 쪽을 따를지 헷갈립니다.

### 방안별 적용

| 방안 | OpenSpec에서 |
|---|---|
| 1. Tracer Bullet | 핵심 기능 하나를 관통하는 작업을 프로젝트의 첫 번째 change로 진행 |
| 2. 의도·동작·구조 분리 | 의도는 `proposal.md`, 동작은 delta spec의 Requirement + Scenario(스키마가 이미 강제), 구조는 스키마 파일을 참조 |
| 3. 기능 단위 스펙 경계 | `openspec/specs/` 아래 capability 디렉터리로 나누고, 공용 계약은 별도 capability로 둠 |
| 4. 스펙 먼저 | propose로 delta spec을 먼저 만들고, apply로 구현하고, archive로 main specs에 병합 |
| 5. 스펙 검증 | apply 전에 change artifact를 리뷰. 관련 main specs와의 충돌을 proposal에 명시 |
| 6. 변경 크기 제한 | change 하나의 task 수에 상한을 두고, 테스트 task를 먼저 배치 |

### 문서가 늘어날 때

- 파일이 쌓이는 곳은 `changes/archive/`이고, 의미 충돌이 문제 되는 곳은 `openspec/specs/`입니다.
- `openspec validate`는 문서 형식만 검사합니다. 서로 다른 spec 사이의 모순은 잡지 못합니다.
- design.md를 필요할 때만 만드는 것, scenario를 테스트로 연결하는 것은 기본 스키마가 이미 안내합니다(위 "기본 스키마에 이미 들어 있는 규칙").
- 에이전트가 archive의 오래된 design.md를 현재 결정으로 참고하지 않도록 `context`에 규칙을 둡니다(아래 예시).

### archive 때 tasks.md를 보존하는 이유

archive는 delta spec을 main specs에 병합하고, change 폴더 전체(proposal, design, tasks, delta spec)를 그대로 `changes/archive/`로 옮깁니다. 공식 문서는 이를 이력(audit trail) 보존이라고만 설명합니다.

- design.md는 "왜 이렇게 만들었나"를 남기는 ADR 역할을 하므로 보존 가치가 분명합니다.
- 모든 task가 체크된 tasks.md는 체크박스가 자기 보고이고 git 이력과 겹치므로 이후 개발에 주는 정보가 거의 없습니다.
- 실질적인 가치는 **미완료 task가 남은 채 archive된 경우**입니다. OpenSpec은 경고만 하고 archive를 허용하므로, main specs에는 적혀 있지만 구현이나 검증이 안 된 간극이 생깁니다. 이 간극을 기록한 곳은 tasks.md뿐입니다. 그래서 미완료 task에 남긴 이유와 후속 change를 적는 규칙을 둡니다(아래 예시).

### config.yaml로 규칙 강제하기

위 방안 중 일부는 `openspec/config.yaml`에 넣어 두면, AI 에이전트가 artifact를 만들거나 apply/archive를 할 때 자동으로 따르게 할 수 있습니다. 설정은 세 가지로 나뉩니다.

| 키 | 용도 | 언제 쓰나 |
|---|---|---|
| `context` | 프로젝트 전반의 제약 | 코드만 읽어서는 알 수 없는 조건 (예: 지원 OS, artifact 작성 언어) |
| `rules.<artifact>` | 특정 artifact를 쓸 때의 규칙 | artifact 이름은 스키마를 따른다. 기본 `spec-driven` 스키마는 `proposal`, `specs`, `design`, `tasks` |
| `operations.<apply\|archive>.guidance` | 구현·archive 작업 방식 | artifact 내용이 아니라 작업 절차에 대한 지침 |

예시 (주석은 [spec-driven-development.md](spec-driven-development.md)의 해당 항목):

```yaml
schema: spec-driven

# 문서가 늘어날 때의 문제: 변경 기록
context: |
  changes/archive/는 과거 기록이므로 현재 결정의 근거로 쓰지 않는다. 현재 동작은 specs/를 기준으로 한다.

rules:
  proposal:
    - 범위 밖인 것(Out of scope)을 반드시 명시한다            # 방안 5
    - 관련 main specs를 먼저 찾고, 겹치거나 모순되는 requirement가 있으면 proposal에 명시한다  # 충돌 대책 3
  specs:
    # Requirement + Scenario 형식과 "외부 동작만 적기"는 스키마가 이미 강제하므로 넣지 않음
    - 인터페이스와 데이터 구조는 스키마 파일을 참조한다         # 방안 2
    - 다른 spec에 이미 있는 규칙은 복사하지 않고 해당 spec을 참조한다  # 충돌 대책 1
  tasks:
    - 테스트 작성 task를 해당 구현 task보다 먼저 배치한다       # 방안 6
    - change 하나의 task는 10개 이하로 유지하고, 넘으면 나눈다  # 방안 6

operations:
  apply:
    guidance:
      - '커밋 메시지에 change 이름을 포함한다 (예: "feat(add-dark-mode): ...")'
  archive:
    guidance:
      - 미완료 task가 남은 채 archive할 때는 남긴 이유와 후속 change 이름을 적는다
```

주의할 점:

- `context`와 `rules`는 에이전트가 따르는 제약일 뿐, artifact 본문에 복사되지 않습니다.
- 코드나 README를 읽으면 알 수 있는 사실은 넣지 않습니다. 매번 컨텍스트로 들어가므로 짧게 유지합니다.
- **YAML 문법이 틀리면 config 전체가 무시됩니다.** OpenSpec은 경고 한 줄만 띄우고 기본값으로 동작하므로 알아채기 어렵습니다.
  - 값 안에 `: `(콜론+공백)가 들어가면 따옴표로 감싸야 합니다.
  - `context: |` 같은 블록 안에서는 `#`도 주석이 아니라 값의 일부가 됩니다. 주석은 블록 밖에 둡니다.
  - 수정한 뒤에는 `openspec doctor`로 경고가 없는지 확인합니다.

### 출처

- [OpenSpec docs/concepts.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)
- OpenSpec 1.15.0 기본 스키마 (`schemas/spec-driven/schema.yaml`)

## OpenSpec 문서를 git으로 관리하는 워크플로

OpenSpec은 git을 직접 다루지 않습니다. `openspec/` 아래의 Markdown 파일을 읽고 쓸 뿐이므로, 이 폴더 전체를 일반 소스코드처럼 커밋합니다. 아래는 공식 문서(team-workflow)의 권장 흐름과, 그에 대한 판단 기준을 정리한 내용입니다.

> 출처의 docs 폴더는 "legacy, 일부 내용이 오래됐을 수 있음"으로 표시되어 있습니다. 현행 사이트(openspec.dev/docs)에는 git 워크플로를 다룬 페이지가 따로 없습니다.

### 무엇을 커밋하나

- `openspec/` 폴더 전체: `config.yaml`, `specs/`(main specs), `changes/`(진행 중인 change), `changes/archive/`(완료된 change)
- 진행 중인 change의 artifact(proposal, delta spec, design, tasks)도 코드와 같이 커밋합니다. 리뷰어가 PR에서 계획과 구현을 함께 봐야 하기 때문입니다.

### 기본 흐름

```
main ──●──────────────────────────────●── (archive 커밋) ──●
        \                            /
         add-dark-mode: propose → apply → PR
```

1. **change 하나당 브랜치 하나**를 만듭니다. 브랜치 이름은 change 이름과 맞춥니다(예: `add-dark-mode`).
2. 그 브랜치에서 `/opsx:propose`로 proposal, delta spec, design, tasks를 만듭니다.
3. **코드를 쓰기 전에 계획을 리뷰**합니다. 이 단계에서 방향이 틀린 것을 잡는 게 가장 저렴합니다.
4. `/opsx:apply`로 구현합니다. 코드와 tasks.md 체크가 함께 바뀝니다.
5. **PR 하나에 delta spec과 코드를 같이** 올립니다. 스펙만 따로 올리는 PR은 공식 흐름에 없습니다.
6. archive합니다(시점은 아래 참고).

### PR 리뷰 순서

1. `proposal.md`: 해결하려는 문제와 범위가 맞는가
2. `specs/` 아래 delta spec: "완료"의 정의가 맞는가
3. 코드 diff: delta spec의 요구사항을 실제로 구현했는가

리뷰어가 코드부터 보지 않도록, PR 설명 맨 위에 delta spec 요약이나 change 폴더 링크를 둡니다.

### archive 시점

공식 문서는 두 방식을 모두 허용하고, **하나를 정해 일관되게 쓰라**고 합니다.

| | merge 후 main에서 archive (공식 권장) | 같은 PR 안에서 archive |
|---|---|---|
| 방법 | PR이 merge된 뒤 main에서 작은 후속 커밋으로, 또는 주기적으로 모아서 | PR merge 전에 브랜치에서 `/opsx:archive`까지 실행 |
| 장점 | main specs에 배포된 작업만 반영됨 | 한 번에 끝나서 단순함. 작업 맥락이 남아 있을 때 archive함 |
| 단점 | 후속 커밋을 빠뜨리면 끝난 change가 `changes/`에 쌓임. main 브랜치가 보호되어 있으면 archive용 PR이 또 필요함 | PR이 지저분해짐(파일 이동 + main specs 변경). merge가 거절되면 archive를 되돌려야 함 |
| 맞는 경우 | 여러 사람이 동시에 작업하고 main 브랜치가 보호된 팀 | 혼자 또는 소수, 브랜치 보호가 느슨한 경우 |

미완료 task가 남은 채 archive할 때 이유를 적는 규칙을 쓴다면, 같은 PR 안에서 archive하는 쪽이 지키기 쉽습니다. merge 후 따로 archive하면 기억이 흐려진 뒤에 적게 됩니다.

### 병렬 작업과 충돌

- change마다 폴더가 따로 있으므로, **archive 전까지는 서로 충돌하지 않습니다.**
- **change 하나는 한 사람이 맡습니다.** 두 사람이 같은 change를 고치면 같은 파일을 동시에 고치는 것과 똑같이 충돌합니다. 같이 해야 한다면 change를 나눕니다.
- 충돌은 archive할 때 `openspec/specs/…/spec.md`에서 생깁니다. 두 change가 같은 requirement를 바꿨기 때문입니다.
  - 일반 merge 충돌처럼 풀되, **실제 시스템 동작에 맞는 requirement를 남깁니다.**
  - 공식 문서는 이 충돌을 "두 change가 시스템 동작에 대해 서로 다르게 생각했다"는 신호로 봅니다. 기계적으로 한쪽을 고르지 말고, 두 change의 proposal을 보고 어느 쪽이 맞는지 판단합니다.

### 커밋 메시지

커밋 메시지에 change 이름을 넣어 두면(예: `feat(add-dark-mode): 토글 버튼 추가`), 나중에 `git log --grep add-dark-mode`로 그 change의 실제 변경을 모두 찾을 수 있습니다. archive된 tasks.md는 체크박스(자기 보고)일 뿐이고, 실제 증거는 git 이력에 있으므로 둘을 이어 주는 역할을 합니다.

이 규칙은 `openspec/config.yaml`의 `operations.apply.guidance`에 넣어 에이전트가 따르게 할 수 있습니다. 설정 방법은 [openspec-practices.md](openspec-practices.md)의 "config.yaml로 규칙 강제하기"를 참고합니다.

### 출처

- [OpenSpec docs/team-workflow.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/team-workflow.md)
- [OpenSpec docs/concepts.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md)

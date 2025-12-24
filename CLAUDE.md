# CLAUDE.md

## 1. MCP 우선사용

DB 조회 시 반드시 MCP 도구를 우선 사용할 것.

| MCP | 용도 | 주요 도구 |
|:--|:--|:--|
| `mcp__ubuntu-server__*` | 원격 서버 명령 (mysql 포함) | `exec`, `sudo-exec` |
| `mcp__mysql__*` | 로또 데이터 조회 | `run_select_query`, `read_records` |
| `mcp__lottoda_wp__*` | lottoda_wp DB 전용 | `run_select_query`, `read_records` |

```bash
# MCP 사용 예시: mcp__ubuntu-server__exec
mysql -e "USE lottoda_wp; SELECT 회차, ord1, ord2, ord3, ord4, ord5, ord6 FROM lotto_data WHERE ord1 IS NOT NULL ORDER BY 회차 DESC LIMIT 10;"
```

## 2. 목표

**우분투 DB의 ord1-ord6를 분석하여 가중치를 적용하고 백테스팅을 해서 TOP10에 최대한 많은 수가 포함되는 모델 구축**

- **DB**: `lottoda_wp` → **Table**: `lotto_data`
- **Columns**: `회차`(PK), `ord1`~`ord6`(오름차순 당첨번호)
- **Data**: 826회차 ~ 현재

### 백테스팅 방식

- 50회차 슬라이딩 윈도우 학습 → 다음 회차 예측
- TOP10 예측번호 중 실제 당첨번호 적중 개수 측정
- 목표: 평균 적중률 최대화

## 3. 분석 요소 (하나씩 추가하며 비교)

현재 적용된 스코어링 요소:

| # | 요소 | 설명 | 최대점 |
|:--:|:--|:--|:--:|
| 1 | 빈도 | 위치별 출현횟수 | ~6 |
| 2 | 주기 | 평균주기 대비 미출현 | 10 |
| 3 | 최근감점 | 최근 출현시 감점 | -4 |
| 4 | 소수 | 소수번호 가산점 | 3 |
| 5 | 소수위치 | 소수의 주요 출현 위치 | 2 |
| 6 | 콜드 | 미출현 > 평균주기 | 3 |
| 7 | 위치빈도 | 위치별 출현 패턴 | ~3 |
| 8 | 이월 | 직전회차 번호 | 2 |
| 9 | 연속 | 연속수 참여 빈도 | ~2 |
| 10 | 끝수 | 위치별 끝수 선호도 | ~0.5 |

### 현재 백테스트 결과 (328회차)

- 평균 적중: **1.31개/회**
- 1개↑ 적중률: 82.3%
- 2개↑ 적중률: 40.8%

### 핵심 상수

```python
PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43}
```

## 파일 구조

- `backtest.py` - 백테스팅 스크립트
- `docs/backtesting.md` - 백테스트 결과
- `docs/position-analysis.md` - 위치별 분석
- `docs/prime-count-distribution.md` - 소수 개수별 분포

## Style Guide

- 간결한 발췌형 작성
- 중복 제거, 핵심만 유지

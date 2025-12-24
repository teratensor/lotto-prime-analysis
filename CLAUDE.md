# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

로또 당첨번호(ord1-ord6)에서 **소수(Prime Number)** 패턴을 중심으로 분석하고 예측하는 프로젝트.

### 핵심 전략

1. **소수 위치 선정** - 어느 위치(ord1~6)에서 소수가 출현할지 예측
2. **소수 개수 선택** - 1개, 2개, 3개 중 선택 (2개가 33.1%로 최다)
3. **연속출현 제외** - 같은 위치에서 2회 연속 출현한 소수는 제외

### 소수 목록

```
2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43
```

### 분석 문서

- [docs/prime-count-distribution.md](docs/prime-count-distribution.md) - 소수 개수별 분포
- [docs/position-analysis.md](docs/position-analysis.md) - 위치별 소수 출현률
- [docs/round-1203-analysis.md](docs/round-1203-analysis.md) - 1203회차 예측 검증

## Database

- **DB**: `lottoda_wp` → **Table**: `lotto_data`
- **Columns**: `회차`(PK), `ord1`~`ord6`(오름차순), `ball1`~`ball6`(추첨순서), `bonus`
- **Data**: 826회차 ~ 현재 (ord 값이 NULL이면 추첨 전)

## Commands

```bash
# 전체 데이터 조회
mysql -u root -e "USE lottoda_wp; SELECT 회차, ord1, ord2, ord3, ord4, ord5, ord6 FROM lotto_data WHERE ord1 IS NOT NULL ORDER BY 회차;"

# 최근 10회차
mysql -u root -e "USE lottoda_wp; SELECT * FROM lotto_data WHERE ord1 IS NOT NULL ORDER BY 회차 DESC LIMIT 10;"

# 소수 개수별 분포
mysql -u root -e "USE lottoda_wp; SELECT (CASE WHEN ord1 IN (2,3,5,7,11,13,17,19,23,29,31,37,41,43) THEN 1 ELSE 0 END + CASE WHEN ord2 IN (2,3,5,7,11,13,17,19,23,29,31,37,41,43) THEN 1 ELSE 0 END + CASE WHEN ord3 IN (2,3,5,7,11,13,17,19,23,29,31,37,41,43) THEN 1 ELSE 0 END + CASE WHEN ord4 IN (2,3,5,7,11,13,17,19,23,29,31,37,41,43) THEN 1 ELSE 0 END + CASE WHEN ord5 IN (2,3,5,7,11,13,17,19,23,29,31,37,41,43) THEN 1 ELSE 0 END + CASE WHEN ord6 IN (2,3,5,7,11,13,17,19,23,29,31,37,41,43) THEN 1 ELSE 0 END) as cnt, COUNT(*) FROM lotto_data WHERE ord1 IS NOT NULL GROUP BY cnt;"
```

## Key Statistics

| 항목 | 값 |
|:--|:--|
| 소수 개수 | 평균 1.9개, 최다 2개(33.1%) |
| 위치별 출현률 | ord1: 42.3%, ord6: 24.6% |
| 합계 범위 | 101-160 (70%), 평균 136 |
| 이월수 | 평균 0.84개 |
| 연속수 | 평균 0.68쌍 |

## Analysis Methods

- **소수 분석**: 회차당 평균 1.9개, 위치별 패턴 (ord1,ord3: 6.3회 간격 / ord2,ord4: 9회 간격)
- **콜드넘버**: 미출현 > 평균주기인 번호
- **이월수**: 직전 회차 번호 재출현 (0개:39%, 1개:41%, 2개↑:20%)
- **연속수**: 인접번호 쌍(n,n+1) 출현 (0쌍:46%, 1쌍:41%)
- **스코어링**: 빈도 + 주기 + 콜드 + 소수 + 위치 + 이월 + 연속 가중치

## 예측 상세표 생성

예측 시 다음 컬럼을 포함한 45개 번호 전체 상세표 생성:

| 컬럼 | 설명 | 최대점 |
|:--|:--|:--:|
| 빈도 | 위치별 출현횟수 기반 | ~6 |
| 주기 | 평균주기 대비 미출현 기간 | 10 |
| 최근 | 최근 출현시 감점 | -4 |
| 소수 | 소수번호 가산점 | 3 |
| 소수위치 | 해당 소수의 주요 출현 위치 (ord1~6) | - |
| 위치빈도 | 해당 위치에서의 출현 횟수 | - |
| 합계 | 101-160 범위 적합도 | 1 |
| 콜드 | 미출현 > 평균주기 | 3 |
| 위치 | 위치별 출현 패턴 | ~3 |
| 이월 | 직전회차 번호 | 2 |
| 연속 | 연속수 참여 빈도 | ~2 |

## MCP Servers (최우선 사용)

**DB 조회 시 Bash(mysql) 대신 MCP 도구를 우선 사용할 것.**

| MCP | 용도 | 주요 도구 |
|:--|:--|:--|
| `mcp__mysql__*` | 로또 데이터 조회 | `run_select_query`, `read_records` |
| `mcp__lottoda_wp__*` | lottoda_wp DB 전용 | `run_select_query`, `read_records` |
| `mcp__ubuntu-server__*` | 원격 서버 명령 | `exec`, `sudo-exec` |
| `mcp__n8n__*` | 워크플로우 자동화 | `list_workflows`, `call_webhook_*` |

## Style Guide

- 간결한 발췌형 작성
- 중복 제거, 핵심만 유지
- 긴 목록은 한 줄로 압축

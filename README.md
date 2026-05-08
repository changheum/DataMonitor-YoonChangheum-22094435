# DataMonitor-YoonChangheum-22094435

반도체 시료 생산주문관리 시스템 **SampleOrderSystem**의 PoC 모듈 중 하나.  
현재 저장된 데이터 상태를 콘솔에서 실시간 조회할 수 있는 **데이터 모니터링 관리자 도구**입니다.

---

## 프로젝트 개요

### SampleOrderSystem PoC 구조

| 모듈 | 역할 |
|------|------|
| ConsoleMVC | 콘솔 기반 MVC 패턴 구현 PoC |
| DataPersistence | 데이터 저장/불러오기 처리 PoC |
| **DataMonitor** | **데이터 모니터링/조회 PoC (이 저장소)** |
| DummyDataGenerator | 테스트용 더미 데이터 생성 PoC |

### 이 모듈의 역할

담당자가 시스템 현황을 한눈에 파악할 수 있도록 두 가지 정보를 콘솔에 출력합니다.

1. **주문 현황** — 상태별 주문 건수 (RESERVED / PRODUCING / CONFIRMED / RELEASE)
2. **재고 현황** — 시료별 재고 수량 및 상태 (여유 / 부족 / 고갈)

> REJECTED 주문은 유효하지 않은 주문으로 모니터링에서 제외됩니다.

---

## 기술 스택

- **언어:** Python 3.10+
- **테스트:** pytest + pytest-cov
- **개발 방식:** TDD (Red → Green → Refactor)

---

## 프로젝트 구조

```
DataMonitor-YoonChangheum-22094435/
│
├── domain/                         # 도메인 모델
│   ├── order.py                    # Order, OrderStatus enum, MONITORED_STATUSES
│   ├── sample.py                   # Sample
│   └── inventory.py                # InventoryItem
│
├── repository/                     # 데이터 접근 레이어
│   ├── order_repository.py         # OrderRepository (ABC) + JsonOrderRepository
│   ├── sample_repository.py        # SampleRepository (ABC) + JsonSampleRepository
│   └── inventory_repository.py     # InventoryRepository (ABC) + JsonInventoryRepository
│
├── service/                        # 비즈니스 로직
│   ├── order_monitor_service.py    # 주문 상태별 건수 집계
│   └── inventory_monitor_service.py # 재고 상태 판정 (여유/부족/고갈)
│
├── display/
│   └── monitor_display.py          # 콘솔 출력 (MonitorDisplay)
│
├── tests/
│   ├── test_domain.py              # 도메인 모델 단위 테스트 (24개)
│   ├── test_repository.py          # Repository 단위 테스트 (20개)
│   ├── test_monitor_service.py     # 서비스 단위 테스트 (19개)
│   ├── test_display.py             # 출력 단위 테스트 (16개)
│   └── test_main.py                # 통합 테스트 (7개)
│
├── data/
│   ├── orders.json                 # 주문 데이터
│   ├── samples.json                # 시료 데이터
│   └── inventory.json              # 재고 데이터
│
├── main.py                         # 진입점
├── pytest.ini                      # pytest / coverage 설정
├── PRD.md                          # 요구사항 정의서 + Phase 계획
└── CLAUDE.md                       # AI 협업 가이드
```

---

## 설치 및 실행

### 요구사항

```bash
pip install pytest pytest-cov
```

### 실행

```bash
python main.py
```

`data/` 폴더의 JSON 파일을 읽어 콘솔에 모니터링 화면을 출력합니다.  
파일이 없으면 빈 상태(건수 0, 시료 없음)로 출력됩니다.

### 출력 예시

```
=== 주문 현황 ===
  상태             건수
  ------------------
  RESERVED           1
  PRODUCING          1
  CONFIRMED          1
  RELEASE            1

=== 재고 현황 ===
  시료명           재고  상태
  --------------------------
  시료A               5  부족
  시료B               0  고갈
  시료C             100  여유
```

---

## 데이터 파일 형식

### `data/orders.json`

```json
[
  {
    "order_id": "O001",
    "sample_id": "S001",
    "customer": "고객A",
    "quantity": 10,
    "status": "RESERVED"
  }
]
```

`status` 허용값: `RESERVED` / `REJECTED` / `PRODUCING` / `CONFIRMED` / `RELEASE`

### `data/samples.json`

```json
[
  {
    "sample_id": "S001",
    "name": "시료A",
    "avg_production_time": 2.0,
    "yield_rate": 0.9
  }
]
```

`yield_rate`: 수율 (0 초과 ~ 1.0 이하). 예) 0.9 = 90%

### `data/inventory.json`

```json
[
  {
    "sample_id": "S001",
    "stock_quantity": 50
  }
]
```

---

## 테스트

### 전체 테스트 실행

```bash
python -m pytest
```

### 커버리지 포함 실행

```bash
python -m pytest --cov=. --cov-report=term-missing
```

### 특정 테스트 파일 실행

```bash
python -m pytest tests/test_domain.py -v
```

### 특정 테스트 케이스 실행

```bash
python -m pytest tests/test_monitor_service.py::TestInventoryMonitorService::test_status_is_depleted_when_stock_is_zero -v
```

### 테스트 현황

| 파일 | 테스트 수 | 대상 |
|------|-----------|------|
| `test_domain.py` | 24개 | Order, Sample, InventoryItem, OrderStatus |
| `test_repository.py` | 20개 | JsonOrderRepository, JsonSampleRepository, JsonInventoryRepository |
| `test_monitor_service.py` | 19개 | OrderMonitorService, InventoryMonitorService |
| `test_display.py` | 16개 | MonitorDisplay |
| `test_main.py` | 7개 | 전체 파이프라인 통합 |
| **합계** | **86개** | |

**커버리지: 100%**

---

## 도메인 설계

### 주문 상태 (OrderStatus)

```
RESERVED  → 주문 접수
REJECTED  → 주문 거절 (모니터링 제외)
PRODUCING → 재고 부족, 생산 중
CONFIRMED → 출고 대기 중
RELEASE   → 출고 완료
```

### 재고 상태 판정 로직

| 조건 | 상태 |
|------|------|
| `stock == 0` | 고갈 |
| `stock < 활성 주문 총량` | 부족 |
| `stock >= 활성 주문 총량` | 여유 |

**활성 주문:** `RESERVED` + `PRODUCING` + `CONFIRMED`  
`RELEASE`(출고 완료)와 `REJECTED`(거절)는 활성 수량 계산에서 제외됩니다.

### 아키텍처

```
main.py
  └── JsonOrderRepository      ─┐
  └── JsonSampleRepository      ├─ JSON 파일에서 데이터 로드
  └── JsonInventoryRepository  ─┘
        │
  OrderMonitorService          ← 상태별 주문 건수 집계
  InventoryMonitorService      ← 시료별 재고 상태 판정
        │
  MonitorDisplay               ← 콘솔 테이블 출력
```

Repository 계층은 ABC 추상 클래스로 인터페이스를 정의하여, JSON 외 다른 저장소(DB 등)로 교체 시 서비스/출력 코드 수정 없이 구현체만 교체하면 됩니다.

---

## 개발 이력 (Phase)

| Phase | 내용 | 커버리지 |
|-------|------|----------|
| Phase 1 | 환경 설정 + 도메인 모델 (Order, Sample, InventoryItem) | 100% |
| Phase 2 | Repository 레이어 (JSON 파일 기반 데이터 읽기) | 100% |
| Phase 3 | 모니터링 서비스 비즈니스 로직 | 100% |
| Phase 4 | 콘솔 UI + 진입점 (main.py) | 100% |
| Phase 5 | 통합 검증 + 코드 품질 개선 | 100% |

---

## 저자

- **윤창흠 (Yoon Changheum)** — 22094435



#1. 사육 및 분뇨 관련 계산식
WASTE_KG_PER_HEAD_DAY=5.1 #배출 원단위 ## 변경
DAYS_PER_MONTH = 30  # 월 기준 일수
SLUDGE_CONVERSION_RATE= 0.2 # 슬러지 전환율


#2.태양광 발전 및 에어지 관련 계산식
PERFORMANCE_RATIO = 0.80  # 태양광 성능계수
# 태양광 용량 모를 때 비교 시나리오 (kW)
DEFAULT_SOLAR_CAPACITIES = [50.0, 100.0, 300.0]

# 잉여전력 활용 가능률 시나리오
SURPLUS_RATE = {
    "보수": 0.30,
    "기준": 0.50,
    "낙관": 0.70,
}


#3. 건조 성능 및 경제성 진단 계산식
DEFAULT_COST_PER_TON = 132_000.0  # 톤당 처리비 기본값 (원) -> 경산시 기준
KWH_PER_TON_DRYING = 380.0  # 슬러지 1톤 건조 필요 전력 (kWh/ton)
DEFAULT_SAVING_FACTOR = 0.80  # 절감 계수 기본값
COST_PER_KW= 4_000_000# 1kw당 기계 비용


SOLAR_CAPACITY_MATRIX = {
"소형": {
"min_kw": 50.0,
"max_kw": 99.0,
"separator_motor_kw": 1.5,       # 1톤급 탈수기 스펙
"machine_capex": 32000000,       # 탈수기 700만 + 건조기 2500만
"construction_capex": 6000000,   # 소형 토목/기본 인입 공사비
},
"중형": {
"min_kw": 100.0,
"max_kw": 299.0,
"separator_motor_kw": 3.7,       # 2톤급 탈수기 스펙
"machine_capex": 50000000,       # 탈수기 1000만 + 건조기 4000만
"construction_capex": 10000000,  # 표준 배관/동력 공사비
},
"대형": {
"min_kw": 300.0,
"max_kw": float('inf'),
"separator_motor_kw": 5.5,       # 3톤급 탈수기 스펙
"machine_capex": 62000000,       # 탈수기 1200만 + 건조기 5000만
"construction_capex": 15000000,  # 대형 토목/배관/한전대행 공사비
}
}
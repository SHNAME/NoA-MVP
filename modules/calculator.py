"""
SolarSludge 계산 엔진
=====================
수식 기반 경제성 진단 함수 모음
"""

from config.constant_config import (
    PERFORMANCE_RATIO,
    KWH_PER_TON_DRYING,
    DEFAULT_COST_PER_TON,
    DEFAULT_SAVING_FACTOR,
    DAYS_PER_MONTH,
    DEFAULT_SOLAR_CAPACITIES,
    SURPLUS_RATE,
    WASTE_KG_PER_HEAD_DAY,
    SLUDGE_CONVERSION_RATE,
    SOLAR_CAPACITY_MATRIX
)
from modules.solar_api_service import get_monthly_solarEnergy


# 1. 사육 및 분뇨 관련 계산식


#월 분뇨 발생량 계산
def calc_monthly_manure_ton(
    head_count: float
) -> float:
    """
    월 분뇨 발생량 (톤)
    = 사육두수 × 분뇨 배출 원단위(kg/두·일) × 일수 / 1000
    """
    return head_count * WASTE_KG_PER_HEAD_DAY * DAYS_PER_MONTH / 1000


#월 건조 대상 슬러지
def calc_target_sludge_ton(
    monthly_manure_ton: float,
) -> float:
    """
    월 건조 대상 슬러지량 (톤)
    = 월 분뇨 발생량 × 슬러지 전환율
    """
    return monthly_manure_ton * SLUDGE_CONVERSION_RATE



# 2. 태양광 발전 및 에너지 관련 계산식


#월 태양광 발전량 계산
def calc_monthly_generation_kwh(
    solar_capacity_kw: float | None,
    monthly_irradiation_kwh_m2: float,
) -> float | dict[float, float]:
    """
    월 태양광 발전량 (kWh)
    = 태양광 용량(kW) × 성능계수(PR) × 월 누적 일사량(kWh/m²)

    solar_capacity_kw가 None이면 DEFAULT_SOLAR_CAPACITIES 각각에 대해 계산해
    {용량(kW): 발전량(kWh)} dict 반환
    """
    #만약 패널 용량을 알 수 없다면 3가지 기본 값으로 임의 계산
    if solar_capacity_kw is None:
        return {
            cap: cap * PERFORMANCE_RATIO * monthly_irradiation_kwh_m2
            for cap in DEFAULT_SOLAR_CAPACITIES
        }
    return solar_capacity_kw * PERFORMANCE_RATIO * monthly_irradiation_kwh_m2


#월 잉여전력 계산
def calc_surplus_kwh(
    monthly_generation_kwh: float,
) -> dict[str, float]:
    """
    월 잉여전력 (kWh) - 보수 / 기준 / 낙관 전 시나리오 계산
    = 월 태양광 발전량 × 잉여전력 활용 가능률

    Returns: {"보수": float, "기준": float, "낙관": float}
    """
    return {
        scenario: monthly_generation_kwh * rate
        for scenario, rate in SURPLUS_RATE.items()
    }



# 3. 건조 성능 및 경제성 진단 계산식


#건조 가능 슬러지량
def calc_dryable_ton(
    surplus_kwh: float,
) -> float:
    """
    태양광으로 건조 가능한 슬러지량 (톤)
    = 월 잉여전력 / 슬러지 1톤 건조 필요 전력
    """
    return surplus_kwh / KWH_PER_TON_DRYING


#실제 건조량
def calc_actual_dried_ton(
    dryable_ton: float,
    target_sludge_ton: float,
) -> float:
    """
    실제 건조량 (톤)
    = min(건조 가능량, 건조 대상 슬러지량)
    """
    return min(dryable_ton, target_sludge_ton)


def calc_treatment_cost_per_ton(
    monthly_treatment_cost: float | None,
    target_sludge_ton: float,
    default_cost_per_ton: float = DEFAULT_COST_PER_TON,
) -> tuple[float, float, bool]:
    """
    톤당 처리비 및 기존 월 처리비 계산

    Returns:
        cost_per_ton      : 톤당 처리비 (원)
        existing_cost     : 기존 월 처리비 (원)
        is_estimated      : True이면 기본값 사용 (화면에 "가정값" 표시 필요)
    """
    # 사용자가 입력을 한 경우
    if monthly_treatment_cost and monthly_treatment_cost > 0:
        cost_per_ton = monthly_treatment_cost / target_sludge_ton
        return cost_per_ton, monthly_treatment_cost, False
    # 사용자가 입력을 하지 않은 경우
    else:
        cost_per_ton = default_cost_per_ton
        existing_cost = target_sludge_ton * default_cost_per_ton
        return cost_per_ton, existing_cost, True

#월 예상 절감액 계산
def calc_monthly_saving(
    actual_dried_ton: float,
    cost_per_ton: float,
    saving_factor: float = DEFAULT_SAVING_FACTOR,
) -> float:
    """
    월 예상 절감액 (원)
    = 실제 건조량 × 톤당 처리비 × 절감 계수
    """
    return actual_dried_ton * cost_per_ton * saving_factor


#사용자가 솔루션을 도입했을 때, 기존 대비 몇 % 아낄 수 있는지를 계산
def calc_saving_rate(
    monthly_saving: float,
    existing_cost: float,
) -> float:
    """
    절감률 (0.0 ~ 1.0)
    = 월 예상 절감액 / 기존 월 처리비
    """
    if existing_cost <= 0:
        return 0.0
    return monthly_saving / existing_cost


# 솔루션 도입 후 실제로 지불할 최종 금액 계산
def calc_new_cost(
    existing_cost: float,
    monthly_saving: float,
) -> float:
    """
    개선 후 월 처리비 (원)
    = 기존 월 처리비 - 월 예상 절감액
    """
    return max(existing_cost - monthly_saving, 0.0)

def calc_roi_months(
    capacity: float,
    monthly_saving: float,
) -> float | None:
    """
    투자 회수 기간 (개월)
    = (machine_capex + construction_capex) × 0.3 / 월 예상 절감액

    capacity에 해당하는 SOLAR_CAPACITY_MATRIX 구간(소형/중형/대형)을 찾아 투자비 산정.
    절감액이 0 이하이거나 해당 구간이 없으면 None 반환
    """
    if monthly_saving <= 0:
        return None

    tier = next(
        (spec for spec in SOLAR_CAPACITY_MATRIX.values()
         if spec["min_kw"] <= capacity < spec["max_kw"]),
        None,
    )
    if tier is None:
        return None

    total_capex = (tier["machine_capex"] + tier["construction_capex"]) * 0.6
    return total_capex / monthly_saving


#패널 용량 포함 진단 로직
def diagnose_with_capacity(
    region_code: str,
    head_count: float,
    solar_capacity_kw: float,
    monthly_treatment_cost: int |float|None,
) -> dict[str, dict]:
    """
    태양광 용량을 아는 경우의 통합 진단 함수.

    보수 / 기준 / 낙관 3개 시나리오 결과를 dict로 반환:
    {"보수": {...}, "기준": {...}, "낙관": {...}}
    """
    if head_count <= 0:
        raise ValueError("사육 두수는 0보다 커야 합니다.")
    # 1. 월 누적 일사량 조회
    monthly_irradiation = get_monthly_solarEnergy(region_code)
    if monthly_irradiation is None:
        raise ValueError(f"일사량 데이터를 가져올 수 없습니다. (지역 코드: {region_code})")

    # 2. 월 분뇨 발생량 계산  / 월 건조 대상 슬러지량
    monthly_manure_ton = calc_monthly_manure_ton(head_count)
    target_sludge_ton = calc_target_sludge_ton(monthly_manure_ton)

    # 3. 월 태양광 발전량
    monthly_generation_kwh = calc_monthly_generation_kwh(solar_capacity_kw, monthly_irradiation)

    # 4. 잉여전력 — 보수 / 기준 / 낙관 3개
    surplus_by_scenario = calc_surplus_kwh(monthly_generation_kwh)

    # 5. 톤당 처리비 계산
    cost_per_ton, existing_cost, is_estimated = calc_treatment_cost_per_ton(
        monthly_treatment_cost, target_sludge_ton
    )

    results = {}
    for scenario, surplus_kwh in surplus_by_scenario.items():
        #건조 가능 슬러지량
        dryable_ton = calc_dryable_ton(surplus_kwh)
        #실제 건조 가능 건조량
        actual_dried_ton = calc_actual_dried_ton(dryable_ton, target_sludge_ton)
        #월 예상 절감액 계산
        monthly_saving = calc_monthly_saving(actual_dried_ton, cost_per_ton)
        #기존 비용 대비 효율 계산
        saving_rate = calc_saving_rate(monthly_saving, existing_cost)
        #솔루션 후 지불할 최종 비용 계산
        new_cost = calc_new_cost(existing_cost, monthly_saving)
        #ROI 계산
        roi_months = calc_roi_months(solar_capacity_kw, monthly_saving)

        results[scenario] = {
            # 분뇨 / 슬러지
            "monthly_manure_ton": round(monthly_manure_ton, 2),
            "target_sludge_ton": round(target_sludge_ton, 2),
            # 발전 / 월 잉여전력
            "monthly_generation_kwh": round(monthly_generation_kwh, 1),
            "surplus_kwh": round(surplus_kwh, 1),
            # 건조
            "dryable_ton": round(dryable_ton, 2),
            "actual_dried_ton": round(actual_dried_ton, 2),
            # 경제성
            "cost_per_ton": round(cost_per_ton, 0),
            "existing_cost": round(existing_cost, 0),
            "monthly_saving": round(monthly_saving, 0),
            "new_cost": round(new_cost, 0),
            "saving_rate_pct": round(saving_rate * 100, 1),
            "roi_months": round(roi_months, 1) if roi_months else None,
            "is_cost_estimated": is_estimated
        }

    return results


#패널 용량 미포함 진단 로직
def diagnose_without_capacity(
    region_code: str,
    head_count: float,
    monthly_treatment_cost: int | float | None,
) -> dict[float, dict[str, dict]]:
    """
    태양광 용량을 모르는 경우의 통합 진단 함수.

    DEFAULT_SOLAR_CAPACITIES(50 / 100 / 200 kW) 각각에 대해
    보수 / 기준 / 낙관 3개 시나리오 결과를 dict로 반환:
    {용량(kW): {"보수": {...}, "기준": {...}, "낙관": {...}}}
    """
    if head_count <= 0:
        raise ValueError("사육 두수는 0보다 커야 합니다.")

    # 1. 월 누적 일사량 조회
    monthly_irradiation = get_monthly_solarEnergy(region_code)
    if monthly_irradiation is None:
        raise ValueError(f"일사량 데이터를 가져올 수 없습니다. (지역 코드: {region_code})")

    # 2. 월 분뇨 발생량 계산 / 월 건조 대상 슬러지량
    monthly_manure_ton = calc_monthly_manure_ton(head_count)
    target_sludge_ton = calc_target_sludge_ton(monthly_manure_ton)

    # 3. 톤당 처리비 계산
    cost_per_ton, existing_cost, is_estimated = calc_treatment_cost_per_ton(
        monthly_treatment_cost, target_sludge_ton
    )

    # 4. 용량별 월 태양광 발전량 — {50kW: kWh, 100kW: kWh, 200kW: kWh}
    generation_by_capacity = calc_monthly_generation_kwh(None, monthly_irradiation)

    # 5. 용량별 × 시나리오별 경제성 계산
    results = {}
    for capacity, monthly_generation_kwh in generation_by_capacity.items():
        # 잉여전력 — 보수 / 기준 / 낙관 3개
        surplus_by_scenario = calc_surplus_kwh(monthly_generation_kwh)

        scenario_results = {}
        for scenario, surplus_kwh in surplus_by_scenario.items():
            #건조 가능 슬러지량
            dryable_ton = calc_dryable_ton(surplus_kwh)
            #실제 건조 가능 건조량
            actual_dried_ton = calc_actual_dried_ton(dryable_ton, target_sludge_ton)
            #월 예상 절감액 계산
            monthly_saving = calc_monthly_saving(actual_dried_ton, cost_per_ton)
            #기존 비용 대비 효율 계산
            saving_rate = calc_saving_rate(monthly_saving, existing_cost)
            #솔루션 후 지불할 최종 비용 계산
            new_cost = calc_new_cost(existing_cost, monthly_saving)
            #ROI 계산
            roi_months = calc_roi_months(capacity, monthly_saving)

            scenario_results[scenario] = {
                # 분뇨 / 슬러지
                "monthly_manure_ton": round(monthly_manure_ton, 2),
                "target_sludge_ton": round(target_sludge_ton, 2),
                # 발전 / 월 잉여전력
                "monthly_generation_kwh": round(monthly_generation_kwh, 1),
                "surplus_kwh": round(surplus_kwh, 1),
                # 건조
                "dryable_ton": round(dryable_ton, 2),
                "actual_dried_ton": round(actual_dried_ton, 2),
                # 경제성
                "cost_per_ton": round(cost_per_ton, 0),
                "existing_cost": round(existing_cost, 0),
                "monthly_saving": round(monthly_saving, 0),
                "new_cost": round(new_cost, 0),
                "saving_rate_pct": round(saving_rate * 100, 1),
                "roi_months": round(roi_months, 1) if roi_months else None,
                "is_cost_estimated": is_estimated,
            }

        results[capacity] = scenario_results

    return results


if __name__ == "__main__":
    from unittest.mock import patch

    MOCK_IRRADIATION = 150.0  # kWh/m²/month (API 모킹용 고정값)
    REGION = "TEST_CODE"
    PATCH_TARGET = f"{__name__}.get_monthly_solarEnergy"

    def run_test(name, fn):
        print(f"\n{'='*50}")
        print(f"[테스트] {name}")
        print('='*50)
        try:
            fn()
            print(">> PASS")
        except AssertionError as e:
            print(f">> FAIL: {e}")
        except Exception as e:
            print(f">> ERROR: {type(e).__name__}: {e}")

    # ── 1. 반환 구조 검증 ──────────────────────────────────
    def test_returns_three_scenarios():
        with patch(PATCH_TARGET, return_value=MOCK_IRRADIATION):
            result = diagnose_with_capacity(REGION, 1000, 100, None)
        assert set(result.keys()) == {"보수", "기준", "낙관"}, f"시나리오 키 불일치: {result.keys()}"

        required_keys = {
            "monthly_manure_ton", "target_sludge_ton",
            "monthly_generation_kwh", "surplus_kwh",
            "dryable_ton", "actual_dried_ton",
            "cost_per_ton", "existing_cost",
            "monthly_saving", "new_cost",
            "saving_rate_pct", "roi_months",
            "is_cost_estimated",
        }
        for scenario, data in result.items():
            missing = required_keys - set(data.keys())
            assert not missing, f"{scenario} 시나리오에 키 누락: {missing}"

    # ── 2. 수치 계산 검증 (기준 시나리오) ─────────────────
    def test_numeric_values():
        with patch(PATCH_TARGET, return_value=MOCK_IRRADIATION):
            result = diagnose_with_capacity(REGION, 1000, 100, None)

        base = result["기준"]
        # 월 분뇨 발생량: 1000두 × 5.1kg × 30일 / 1000 = 153.0톤
        assert base["monthly_manure_ton"] == 153.0, f"분뇨량 오류: {base['monthly_manure_ton']}"
        # 월 태양광 발전량: 100kW × 0.80 × 150 = 12000 kWh
        assert base["monthly_generation_kwh"] == 12000.0, f"발전량 오류: {base['monthly_generation_kwh']}"
        # 기준 잉여전력: 12000 × 0.50 = 6000 kWh
        assert base["surplus_kwh"] == 6000.0, f"잉여전력 오류: {base['surplus_kwh']}"
        # 건조 가능량: 6000 / 380 = 15.79톤
        assert base["dryable_ton"] == 15.79, f"건조 가능량 오류: {base['dryable_ton']}"
        print(f"  분뇨: {base['monthly_manure_ton']}톤 / 발전: {base['monthly_generation_kwh']}kWh"
              f" / 잉여: {base['surplus_kwh']}kWh / 건조: {base['dryable_ton']}톤")

    # ── 3. 시나리오 순서 검증 (보수 ≤ 기준 ≤ 낙관) ────────
    def test_scenario_order():
        with patch(PATCH_TARGET, return_value=MOCK_IRRADIATION):
            result = diagnose_with_capacity(REGION, 1000, 100, None)
        assert result["보수"]["surplus_kwh"] < result["기준"]["surplus_kwh"] < result["낙관"]["surplus_kwh"], \
            "잉여전력 순서 오류"
        assert result["보수"]["monthly_saving"] <= result["기준"]["monthly_saving"] <= result["낙관"]["monthly_saving"], \
            "절감액 순서 오류"
        print(f"  절감액 — 보수: {result['보수']['monthly_saving']:,.0f}원 /"
              f" 기준: {result['기준']['monthly_saving']:,.0f}원 /"
              f" 낙관: {result['낙관']['monthly_saving']:,.0f}원")

    # ── 4. 처리비 None/0 → DEFAULT_COST_PER_TON 기본값 적용 ──────────────
    def test_default_cost_when_none():
        expected_sludge_ton = round(1000 * WASTE_KG_PER_HEAD_DAY * DAYS_PER_MONTH / 1000 * SLUDGE_CONVERSION_RATE, 2)
        expected_existing_cost = round(expected_sludge_ton * DEFAULT_COST_PER_TON, 0)
        with patch(PATCH_TARGET, return_value=MOCK_IRRADIATION):
            result_none = diagnose_with_capacity(REGION, 1000, 100, None)
            result_zero = diagnose_with_capacity(REGION, 1000, 100, 0)
        for scenario in result_none:
            assert result_none[scenario]["existing_cost"] == expected_existing_cost, \
                f"{scenario}: None 시 existing_cost 오류"
            assert result_zero[scenario]["existing_cost"] == expected_existing_cost, \
                f"{scenario}: 0 시 existing_cost 오류"
            assert result_none[scenario]["is_cost_estimated"] is True, \
                f"{scenario}: is_cost_estimated가 True여야 함"
        print(f"  None/0 입력 시 DEFAULT_COST_PER_TON 기본값 적용, existing_cost={expected_existing_cost:,.0f}원, is_cost_estimated=True 확인")

    # ── 5. 처리비 직접 입력 ────────────────────────────────
    def test_user_provided_cost():
        monthly_cost = 5_000_000.0
        with patch(PATCH_TARGET, return_value=MOCK_IRRADIATION):
            result = diagnose_with_capacity(REGION, 1000, 100, monthly_treatment_cost=monthly_cost)
        for scenario, data in result.items():
            assert data["is_cost_estimated"] is False, f"{scenario}: is_cost_estimated 오류"
            assert data["existing_cost"] == monthly_cost, \
                f"{scenario}: existing_cost 오류 ({data['existing_cost']} != {monthly_cost})"
        print(f"  입력 처리비 {monthly_cost:,.0f}원 그대로 반영 확인")

    # ── 6. actual_dried_ton 상한 (건조 가능량 > 슬러지량) ──
    def test_actual_dried_ton_capped_at_target():
        with patch(PATCH_TARGET, return_value=MOCK_IRRADIATION):
            result = diagnose_with_capacity(REGION, 1000, 100_000, None)  # 용량을 100배로 키움
        for scenario, data in result.items():
            assert data["actual_dried_ton"] <= data["target_sludge_ton"], \
                f"{scenario}: actual_dried_ton이 target_sludge_ton 초과"
        print(f"  target: {result['기준']['target_sludge_ton']}톤 /"
              f" actual(낙관): {result['낙관']['actual_dried_ton']}톤 — 상한 적용 확인")

    # ── 7. new_cost 음수 방지 ──────────────────────────────
    def test_new_cost_non_negative():
        with patch(PATCH_TARGET, return_value=MOCK_IRRADIATION):
            result = diagnose_with_capacity(REGION, 1000, 100, None)
        for scenario, data in result.items():
            assert data["new_cost"] >= 0, f"{scenario}: new_cost 음수 ({data['new_cost']})"

    # ── 8. roi_months=None (일사량 0 → 절감액 0) ──────────
    def test_roi_none_when_no_saving():
        with patch(PATCH_TARGET, return_value=0.0):
            result = diagnose_with_capacity(REGION, 1000, 100, None)
        for scenario, data in result.items():
            assert data["roi_months"] is None, f"{scenario}: roi_months가 None이어야 함"
        print("  일사량 0 → 절감액 0 → roi_months=None 확인")

    # ── 9. API 실패 → ValueError ───────────────────────────
    def test_raises_on_api_failure():
        with patch(PATCH_TARGET, return_value=None):
            try:
                diagnose_with_capacity(REGION, 1000, 100, None)
                assert False, "ValueError가 발생해야 함"
            except ValueError as e:
                print(f"  ValueError 정상 발생: {e}")

    # ── 실행 ──────────────────────────────────────────────
    run_test("반환 구조 (3개 시나리오 + 필수 키)", test_returns_three_scenarios)
    run_test("수치 계산 (기준 시나리오)", test_numeric_values)
    run_test("시나리오 순서 (보수 ≤ 기준 ≤ 낙관)", test_scenario_order)
    run_test("처리비 None/0 → DEFAULT_COST_PER_TON 기본값 적용", test_default_cost_when_none)
    run_test("처리비 직접 입력", test_user_provided_cost)
    run_test("actual_dried_ton 상한 (슬러지량 초과 방지)", test_actual_dried_ton_capped_at_target)
    run_test("new_cost 음수 방지", test_new_cost_non_negative)
    run_test("roi_months=None (절감액 0)", test_roi_none_when_no_saving)
    run_test("API 실패 → ValueError", test_raises_on_api_failure)

    print(f"\n{'='*50}")
    print("[diagnose_without_capacity 테스트]")
    print('='*50)

    # ── 10. 반환 구조 검증 (3용량 × 3시나리오) ────────────
    def test_without_capacity_structure():
        with patch(PATCH_TARGET, return_value=MOCK_IRRADIATION):
            result = diagnose_without_capacity(REGION, 1000, None)
        assert set(result.keys()) == set(DEFAULT_SOLAR_CAPACITIES), \
            f"용량 키 불일치: {result.keys()}"
        for capacity, scenarios in result.items():
            assert set(scenarios.keys()) == {"보수", "기준", "낙관"}, \
                f"{capacity}kW 시나리오 키 불일치"
        print(f"  {sorted(result.keys())}kW × 3시나리오 구조 확인")

    # ── 11. 용량별 발전량 비례 검증 ───────────────────────
    def test_without_capacity_generation_scales():
        with patch(PATCH_TARGET, return_value=MOCK_IRRADIATION):
            result = diagnose_without_capacity(REGION, 1000, None)
        gen_50  = result[50.0]["기준"]["monthly_generation_kwh"]
        gen_100 = result[100.0]["기준"]["monthly_generation_kwh"]
        gen_300 = result[300.0]["기준"]["monthly_generation_kwh"]
        assert gen_100 == gen_50 * 2, "100kW 발전량이 50kW의 2배여야 함"
        assert gen_300 == gen_50 * 6, "300kW 발전량이 50kW의 6배여야 함"
        print(f"  발전량 — 50kW: {gen_50}kWh / 100kW: {gen_100}kWh / 300kW: {gen_300}kWh")

    # ── 12. API 실패 → ValueError ─────────────────────────
    def test_without_capacity_raises_on_api_failure():
        with patch(PATCH_TARGET, return_value=None):
            try:
                diagnose_without_capacity(REGION, 1000, None)
                assert False, "ValueError가 발생해야 함"
            except ValueError as e:
                print(f"  ValueError 정상 발생: {e}")

    run_test("반환 구조 (3용량 × 3시나리오)", test_without_capacity_structure)
    run_test("용량별 발전량 비례 (50 / 100 / 200kW)", test_without_capacity_generation_scales)
    run_test("API 실패 → ValueError", test_without_capacity_raises_on_api_failure)

    print(f"\n{'='*50}")
    print("전체 테스트 완료")
    print('='*50)

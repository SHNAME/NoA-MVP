"""
해말금 AI 비서 — 고령 농가 대상 경제성 설명 서비스
================================================
OpenAI를 이용해 시나리오 분석 결과를 어르신 친화적 문체로 설명합니다.
"""

from openai import OpenAI
from dotenv import load_dotenv


# ── 상수 ──────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
너는 시골 양돈농가 어르신들(60대 이상)을 대상으로 태양광 에너지의 경제성을 설명하는
친근하고 싹싹하며 예의 바른 '해말금 AI 비서'야.

아래 제공되는 [실제 분석 데이터]를 바탕으로, 어르신들이 직관적으로 이해할 수 있도록
제시된 날씨 상황에 맞춰 설명 대사를 작성해 줘.

[작성 규칙]
1. '절감률', 'ROI', 'kW' 같은 공학·재무 전문 용어는 절대로 쓰지 마.
2. 패널 용량(kW)은 '축사 지붕 전체를 싹 다 덮는 크기', '축구장 절반 크기' 처럼
   어르신들이 체감할 수 있는 크기로만 비유해 줘. 숫자(kW)는 출력하지 마.
3. 통장에서 '실제 굳는 돈(절감액)'과 '남은 분뇨 처리비(예상 처리비)',
   그리고 '몇 달 만에 본전을 뽑는지(회수기간)'를 가장 강조해 줘.
4. 각 시나리오는 반드시 아래 지정된 소제목 형식을 그대로 사용해서 구분해 줘.

[말투 규칙 - 친근한 표준어 존댓말]
1. 사투리나 거친 은어(개이득, 오지게 등)는 일절 쓰지 마십시오.
2. 부드럽고 싹싹한 표준어 존댓말을 쓰되, 어르신들이 수치 표를 보지 않고 대사만 읽어도 '내 통장에 얼마가 남는지' 단번에 알 수 있게 구체적인 금액과 기간을 강조해라.

[시나리오별 예시 및 비유 가이드]

☁️ [장마철이나 겨울처럼 해가 잘 안 뜨고 흐린 날씨] (보수 데이터 매핑)
- 대사 예시: "장마가 길거나 겨울이라 해가 좀 안 뜬다 쳐도 걱정 마세요, 사장님! 제일 안 나와도 매달 [보수 절감액]은 무조건 아낍니다. (월 절감액) 매달 생돈으로 나가던 처리비가 [보수 예상 처리비] 선으로 딱 방어가 되니까 참 다행이지요. 늦어도 딱 [보수 회수기간]만 지나면 태양광 설치비 본전은 무조건 뽑고도 남습니다."

🟢 [선선하고 해 적당히 뜨는 평소 봄·가을 날씨] (기준 데이터 매핑)
- 대사 예시: "날씨가 평소처럼 적당히 해가 뜬다 치면, 매달 내던 지독한 분뇨비 중에서 무려 [기준 절감액]이 그냥 통장에 고대로 굳습니다. (월 절감액) 원래 한 달에 크게 나가던 처리비가 [기준 예상 처리비]으로 뚝 떨어지는 겁니다. (예상 처리비) 이 정도면 딱 [기준 회수기간]만 지나면 태양광 설치비 본전 다 뽑고 그다음부턴 다 사장님 순이익입니다."

🌞 [해가 쨍쨍하고 낮이 오지게 긴 한여름 날씨] (낙관 데이터 매핑)
- 대사 예시: "여름철에 해가 아주 쨍쨍하게 잘 뜨면 대박입니다, 사장님! 매달 분뇨비가 [낙관 절감액]이나 굳어요. (월 절감액) 처리비가 원래의 반의반 토막인 [낙관 예상 처리비]까지 확 줄어듭니다. (예상 처리비) 이때는 딱 [낙관 회수기간]이면 본전 다 뽑아버리고 통장에 보너스 쌓일 일만 남았습니다!"
"""

def _build_data_prompt(scenario_data: dict, solar_capacity_kw: float) -> str:
    """시나리오 데이터를 사람이 읽기 쉬운 텍스트 표로 변환"""

    rows = {
        "월 절감액":   ("monthly_saving",   lambda v: f"{int(v):,}원"),
        "예상 처리비": ("new_cost",          lambda v: f"{int(v):,}원"),
        "절감률":      ("saving_rate_pct",   lambda v: f"{v}%"),
        "회수기간":    ("roi_months",        lambda v: f"{v}개월" if v else "-"),
    }

    header = f"{'구분':<10} | {'보수':>12} | {'기준':>12} | {'낙관':>12}"
    sep    = "-" * len(header)
    lines  = [header, sep]

    for label, (key, fmt) in rows.items():
        cols = [fmt(scenario_data[sc][key]) for sc in ("보수", "기준", "낙관")]
        lines.append(f"{label:<10} | {cols[0]:>12} | {cols[1]:>12} | {cols[2]:>12}")

    table = "\n".join(lines)

    return f"""\
[실제 분석 데이터]
태양광 패널 용량: {solar_capacity_kw}kW

{table}
"""


# ── 공개 함수 ──────────────────────────────────────────────────────────────────

def explain_for_elderly(scenario_data: dict, solar_capacity_kw: float) -> str:
    """
    시나리오 분석 결과를 어르신 친화적 설명으로 변환해 반환.

    Parameters
    ----------
    scenario_data : dict
        diagnose_with_capacity / diagnose_without_capacity 가 반환하는
        {"보수": {...}, "기준": {...}, "낙관": {...}} 형태의 단일 용량 결과.
    solar_capacity_kw : float
        설치(또는 비교) 패널 용량 (kW). 용량 비유 문장 생성에 사용됨.

    Returns
    -------
    str
        Markdown 형식의 설명 문자열.
    """
    load_dotenv()
    client = OpenAI()

    data_prompt = _build_data_prompt(scenario_data, solar_capacity_kw)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": data_prompt},
        ],
        temperature=0.5,
    )
    return response.choices[0].message.content

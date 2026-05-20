import os
import requests
import xmltodict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
SOLAR_API_KEY = os.getenv("SOLAR_EXPOSURE_API_KEY")


def get_monthly_solarEnergy(region_code):
    url = "https://apis.data.go.kr/1390802/AgriWeather/WeatherObsrInfo/V3/GnrlWeather/getWeatherYearMonList3"

    # 날짜 계산
    now = datetime.now()
    last_year = now.year - 1
    current_month = now.month

    findItem = f"{last_year}-{current_month:02d}"

    # 파라미터 설정
    params = {
        "serviceKey": SOLAR_API_KEY,
        "Page_No": "1",
        "Page_Size": "12",
        "Search_Year": str(last_year),
        "obsr_Spot_Cd": region_code
    }

    try:
        # API 호출
        response = requests.get(url, params=params)
        response.raise_for_status()

        # XML -> Dictionary 변환
        data_dict = xmltodict.parse(response.text)

        # 데이터 추출
        items = data_dict.get('response', {}).get('body', {}).get('items', {})
        if not items or 'item' not in items:
            print(f"데이터 응답이 비어있습니다. (결과 코드: {data_dict.get('response', {}).get('header', {}).get('result_Msg')})")
            return None

        items_list = items['item']


        for item in items_list:
            if item.get('date') == findItem:
                sr_value = item.get('srqty')
                # 단위 변환해서 반환
                return float(sr_value) /3.6 if sr_value and sr_value.strip() else 0.0

        print(f"{findItem}에 해당하는 데이터를 찾을 수 없습니다.")
        return None

    except Exception as e:
        print(f"오류 발생: {e}")
        return None


if __name__ == "__main__":
    # 실제 존재하는 코드로 테스트해보세요
    res = get_monthly_solarEnergy("323891D002")
    print(f"결과 일사량: {res}")
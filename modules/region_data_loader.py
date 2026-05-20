from pathlib import Path

import pandas as pd
import streamlit as st


# 초기 loading 시 데이터 초기화 셋
@st.cache_data
def load_region_code(file_path):
    df= pd.read_csv(file_path,header=0)

    region_map={}

    for _,row in df.iterrows():
        province = row['도구분']
        city = row['지점명']
        code =row['지점코드']

        if province not in region_map:
            region_map[province]= {}

        region_map[province][city]= code

    return region_map


if __name__ == "__main__":
    # 파일 경로 (noa 폴더 기준)
    BASE_DIR = Path(__file__).resolve().parent.parent
    FILE_PATH = BASE_DIR / "data" / "region_code.csv"

    try:
        print("\n" + "=" * 50)
        print("CSV 데이터 전수 조사 시작...")

        # 1. 데이터 로드
        region_map = load_region_code(FILE_PATH)

        # 2. 총 지점 코드(시/군/구) 개수 계산
        total_provinces = len(region_map)
        total_codes = sum(len(cities) for cities in region_map.values())
        print(f"등록된 '도' 개수: {total_provinces}개")
        print(f"총 지점 코드 개수: {total_codes}개")

        print("-" * 50)

        # 3. 도별 상세 개수 출력
        print("도별 세부 지점 수:")
        for province, cities in region_map.items():
            print(f"   - {province:5}: {len(cities):3}개 지점")

    except FileNotFoundError:
        print(f"에러: '{FILE_PATH}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"에러 발생: {e}")

    print("=" * 50 + "\n")
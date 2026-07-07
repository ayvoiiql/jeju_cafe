from pathlib import Path

import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="제주도 카페 분석", page_icon="☕", layout="wide")

CSV_PATH = "제주상권.csv"
CSS_PATH = Path(__file__).parent / "style.css"
JEJU_CENTER = [33.38, 126.55]


def load_css():
    st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


load_css()


@st.cache_data
def load_cafes():
    df = pd.read_csv(CSV_PATH, encoding="cp949", low_memory=False)
    df = df[df["상권업종소분류명"] == "카페"].copy()
    df = df.dropna(subset=["경도", "위도"])
    df["주소"] = df["도로명주소"].fillna(df["지번주소"])
    cols = ["상호명", "시군구명", "행정동명", "주소", "경도", "위도"]
    return df[cols].reset_index(drop=True)


cafes = load_cafes()

with st.container(key="hero"):
    st.markdown("<h1>☕ 제주도 카페 분석 지도</h1>", unsafe_allow_html=True)
    st.markdown("<p>제주상권 데이터 기반 카페 위치 시각화 · 지도를 축소하면 위치별로 묶여서 표시됩니다</p>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🔎 필터")

    sigungu_options = sorted(cafes["시군구명"].unique())
    selected_sigungu = st.multiselect("시군구", sigungu_options, default=sigungu_options)

    dong_pool = cafes[cafes["시군구명"].isin(selected_sigungu)]
    dong_options = sorted(dong_pool["행정동명"].dropna().unique())
    selected_dong = st.multiselect("행정동 (비워두면 전체)", dong_options)

    keyword = st.text_input("카페 이름 검색")

filtered = cafes[cafes["시군구명"].isin(selected_sigungu)]
if selected_dong:
    filtered = filtered[filtered["행정동명"].isin(selected_dong)]
if keyword:
    filtered = filtered[filtered["상호명"].str.contains(keyword, case=False, na=False)]

with st.container(key="stats"):
    col1, col2, col3 = st.columns(3)
    col1.metric("☕ 검색된 카페 수", f"{len(filtered):,}")
    col2.metric("🏙️ 시군구", f"{filtered['시군구명'].nunique()}개")
    col3.metric("📍 행정동", f"{filtered['행정동명'].nunique()}개")

m = folium.Map(location=JEJU_CENTER, zoom_start=11, tiles="CartoDB positron")
cluster = MarkerCluster().add_to(m)

for _, row in filtered.iterrows():
    folium.Marker(
        location=[row["위도"], row["경도"]],
        tooltip=row["상호명"],
        popup=folium.Popup(
            f"<b>{row['상호명']}</b><br>{row['주소']}",
            max_width=250,
        ),
        icon=folium.Icon(color="darkred", icon="coffee", prefix="fa"),
    ).add_to(cluster)

with st.container(key="map_card"):
    st_folium(m, width=None, height=650, returned_objects=[])

with st.expander("데이터 보기"):
    st.dataframe(filtered, width="stretch")

st.markdown('<p class="jeju-footer">제주상권 데이터 기반 · Streamlit + Folium</p>', unsafe_allow_html=True)

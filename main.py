import streamlit as st

st.set_page_config(page_title="CEO Craft - 메인", layout="wide")

company_name = st.session_state.get("company_name")
if not company_name:
    st.warning("회사 이름이 설정되지 않았습니다. 시작 화면으로 이동합니다.")
    st.switch_page("load.py")

st.markdown(f"## {company_name}")

st.markdown("\n")
st.markdown("### 메인 대시보드")

# 하단 버튼 영역을 화면 아래로 밀기 위한 여백
st.markdown("<div style='height: 55vh;'></div>", unsafe_allow_html=True)

st.markdown("---")
cols = st.columns(5)

with cols[0]:
    if st.button("자산"):
        st.switch_page("pages/asset.py")
with cols[1]:
    if st.button("매출"):
        st.switch_page("pages/sales.py")
with cols[2]:
    if st.button("손익"):
        st.switch_page("pages/profit.py")
with cols[3]:
    if st.button("현금"):
        st.switch_page("pages/cash.py")
with cols[4]:
    if st.button("재고"):
        st.switch_page("pages/inventory.py")

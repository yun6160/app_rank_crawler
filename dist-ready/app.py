# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
from crawler import login_and_get_titles

st.set_page_config(page_title="📊 앱 순위 크롤링 도구", layout="centered")

st.title("📊 UPUP 앱 순위 크롤링 도구")
st.markdown("URL을 입력하면 해당 페이지에서 **앱 순위 및 정보**를 가져옵니다(자동 로그인됨!)")

url = st.text_input("🔗 크롤링할 URL을 입력하세요")

if st.button("크롤링 시작"):
    if url:
        with st.spinner("⏳ 앱 정보 크롤링 중..."):
            try:
                results = login_and_get_titles(url)
                st.success(f"✅ 총 {len(results)}개 앱 정보를 가져왔습니다.")

                # 📄 DataFrame 변환
                df = pd.DataFrame(results)

                # 📊 테이블 형태로 출력
                st.dataframe(df, use_container_width=True)

                # 📥 Excel 다운로드 버튼 생성
                def to_excel(dataframe):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        dataframe.to_excel(writer, index=False, sheet_name='App Rankings')
                    return output.getvalue()

                excel_data = to_excel(df)

                st.download_button(
                    label="📥 엑셀로 다운로드",
                    data=excel_data,
                    file_name="app_rankings.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
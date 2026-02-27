import streamlit as st
import sqlite3
import os
import io
import pandas as pd
from database import create_integrated_sales_view, get_view_data


def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output) as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


def main():
    st.set_page_config(page_title="Sales Data Integrator", layout="wide")
    st.title("판매 데이터 통합 View")

    uploaded_file = st.sidebar.file_uploader(
        "SQLite DB 파일 업로드",
        type=["db", "sqlite", "sqlite3"]
    )

    if uploaded_file:

        temp_db_path = "temp_sales_data.db"

        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)

        with open(temp_db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            conn = sqlite3.connect(temp_db_path)

            create_integrated_sales_view(conn)
            df = get_view_data(conn)

            conn.close()

            if df.empty:
                st.warning("데이터가 없습니다.")
                return

            # =========================
            # 1️⃣ 결과 테이블
            # =========================
            st.subheader("📊 통합 판매 데이터")
            st.dataframe(df, use_container_width=True)

            # =========================
            # 2️⃣ 엑셀 다운로드 버튼
            # =========================
            excel_data = convert_df_to_excel(df)

            st.download_button(
                label="📂 엑셀 다운로드",
                data=excel_data,
                file_name="integrated_sales_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # =========================
            # 3️⃣ 기타 설명 (접기)
            # =========================
            with st.expander("ℹ️ 상세 정보 보기"):
                st.write(f"총 데이터 건수: {len(df)}")
                st.write(f"컬럼 수: {len(df.columns)}")
                st.write("데이터는 sales_plan_data + sales_actual_data를 통합한 View입니다.")

        except Exception as e:
            st.error(f"오류 발생: {e}")

    else:
        st.info("왼쪽에서 DB 파일을 업로드하세요.")


if __name__ == "__main__":
    main()

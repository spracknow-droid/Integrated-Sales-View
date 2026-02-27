import streamlit as st
import sqlite3
import pandas as pd
import os
# database.py에서 함수 불러오기
from database import create_integrated_sales_view

def main():
    st.set_page_config(page_title="Sales Data Integrator", layout="wide")
    st.title("📊 판매 데이터 표준화 통합 뷰")

    # 1. 사이드바에서 DB 파일 업로드
    st.sidebar.header("데이터 업로드")
    uploaded_file = st.sidebar.file_uploader("SQLite DB 파일을 업로드하세요", type=["db", "sqlite", "sqlite3"])

    if uploaded_file is not None:
        temp_db_path = "temp_sales_data.db"
        with open(temp_db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            conn = sqlite3.connect(temp_db_path)
            
            # 분리된 파일의 함수 호출
            create_integrated_sales_view(conn)
            st.sidebar.success("✅ 통합 View 생성 완료")

            st.subheader("📋 통합 판매 데이터 (view_integrated_sales)")
            
            try:
                df_integrated = pd.read_sql_query("SELECT * FROM view_integrated_sales", conn)
                if not df_integrated.empty:
                    st.dataframe(df_integrated, use_container_width=True)
                    st.write(f"총 데이터: {len(df_integrated)} 건")
                else:
                    st.info("데이터가 존재하지 않습니다.")
            except Exception as e:
                st.warning(f"View 조회 오류: {e}")
            
            conn.close()
        except Exception as e:
            st.error(f"DB 연결 오류: {e}")
    else:
        st.info("사이드바에서 DB 파일을 업로드해주세요.")

if __name__ == "__main__":
    main()

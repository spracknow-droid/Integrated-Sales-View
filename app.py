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
    st.title("Integrated Sales View")

    uploaded_file = st.sidebar.file_uploader(
        "SQLite DB 파일 업로드",
        type=["db", "sqlite", "sqlite3"]
    )

    if uploaded_file:
        temp_db_path = "temp_sales_data.db"

        # 새 파일 업로드 시 기존 임시 파일 제거
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except:
                pass

        with open(temp_db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # 1. DB 연결 및 뷰 생성
            conn = sqlite3.connect(temp_db_path)
            create_integrated_sales_view(conn)
            
            # 2. 데이터 불러오기
            df = get_view_data(conn)
            
            # 3. 중요: 연결을 닫아야 파일에 최종 기록됩니다.
            conn.close()

            if df.empty:
                st.warning("데이터가 없습니다.")
                return

            # =========================
            # 1️⃣ 결과 테이블 표시
            # =========================
            st.subheader("📊 통합 판매 데이터")
            st.dataframe(df, use_container_width=True)

            # =========================
            # 2️⃣ 다운로드 섹션
            # =========================
            col1, col2 = st.columns(2)
            
            with col1:
                excel_data = convert_df_to_excel(df)
                st.download_button(
                    label="📂 엑셀 다운로드",
                    data=excel_data,
                    file_name="integrated_sales_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            with col2:
                # 파일 연결이 완전히 끊긴 상태에서 binary 읽기
                with open(temp_db_path, "rb") as f:
                    db_binary = f.read()
                
                st.download_button(
                    label="🗄️ 통합 View 포함 DB 다운로드",
                    data=db_binary,
                    file_name="integrated_sales_with_view.db",
                    mime="application/octet-stream",
                    use_container_width=True
                )

            with st.expander("ℹ️ 상세 정보 보기"):
                st.write(f"총 데이터 건수: {len(df)}")
                st.write("SQLite 툴에서 확인 시 'Tables'가 아닌 'Views' 카테고리를 확인해주세요.")

        except Exception as e:
            st.error(f"오류 발생: {e}")

    else:
        st.info("왼쪽에서 DB 파일을 업로드하세요.")


if __name__ == "__main__":
    main()

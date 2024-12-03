import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import json

# 데이터베이스 연결 정보
db_host = "56.155.9.34"  # PostgreSQL 서버 주소 (로컬호스트 또는 원격 IP)
db_port = "5432"       # PostgreSQL 포트 (기본값 5432)
db_name = "card"       # 데이터베이스 이름
db_user = "postgres"      # 데이터베이스 사용자 이름
db_password = "0714"  # 사용자 비밀번호

# JSON 파일 읽기
json_file_path = "./data/Cardinfo.json"  # JSON 파일 경로
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 데이터베이스 연결
try:
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    cursor = conn.cursor()

    # 테이블에 데이터 삽입 SQL 정의
    insert_query = """
    INSERT INTO cardinfo (cardName, annualFee, prevSales, cardApplyUrl)
    VALUES (%s, %s, %s, %s)
    """

    # JSON 데이터 삽입하기
    for item in data:
        card_name = item.get("cardName")
        annual_fee = item.get("annualFee")
        prev_sales = item.get("prevSales")
        card_apply_url = item.get("cardApplyUrl")

        # 데이터 삽입 실행
        cursor.execute(insert_query, (card_name, annual_fee, prev_sales, card_apply_url))

    # 변경사항 커밋
    conn.commit()
    print("JSON 데이터가 Cardinfo 테이블에 성공적으로 저장되었습니다.")


except Exception as e:
    print(f"오류가 발생했습니다: {e}")

finally:
    # 연결 종료
    if conn:
        cursor.close()
        conn.close()
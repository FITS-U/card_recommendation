import pandas as pd
from pymongo import MongoClient

# MongoDB 서버 연결 정보
# 형식: "mongodb://<username>:<password>@<host>:<port>/<database>"
mongo_uri = "mongodb://root:example@56.155.9.34:27017/Image"

# MongoDB 클라이언트 설정
client = MongoClient(mongo_uri)

# 데이터베이스와 컬렉션 설정
db = client["Image"]  # 데이터베이스 이름
collection = db["cardImage"]  # 컬렉션 이름

# CSV 파일을 읽어 데이터프레임 생성
csv_file_path = "./data/CardImage.csv"  # CSV 파일 경로
df = pd.read_csv(csv_file_path)

# 데이터프레임의 각 행을 딕셔너리로 변환하여 MongoDB에 저장
data = df.to_dict(orient="records")  # 데이터프레임의 각 행을 딕셔너리 리스트로 변환
collection.insert_many(data)  # 여러 개의 문서를 MongoDB에 삽입

# 성공적인 데이터 삽입 확인
print("CSV 데이터가 MongoDB에 성공적으로 저장되었습니다.")

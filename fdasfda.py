import pandas as pd
import json

# JSON 파일 경로 설정
json_file_path = "./data/CardInfo.json"  # 기존 JSON 파일 경로
csv_file_path = "./data/CardInfo.csv"  # 생성할 CSV 파일 경로

# JSON 파일 읽기
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Pandas DataFrame으로 변환
df = pd.DataFrame(data)

# CSV 파일로 저장
df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

print(f"CSV 파일이 {csv_file_path}에 성공적으로 저장되었습니다.")

from dotenv import load_dotenv
load_dotenv()
import json
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import openai

file_path = "./data/card_data_benefits.json"

# JSON 파일 로드 (리스트 형태)
with open(file_path, "r", encoding="utf-8") as file:
    card_data = json.load(file)

db_path = "./chromaDB"
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)

# 리스트 형태의 card_data 순회
for card in card_data:
    # cardId는 JSON 데이터에서 직접 가져옴
    cardId = card["cardId"]

    # 문서 생성
    document = f"Card ID: {cardId}\nCard Name: {card['Card Name']}\nAnnual Fee: {card['Annual_fee']}\nBase Record: {card['Base Record']}\nBenefits: {card['Benefits']}"
    metadata = {"Card Name": card["Card Name"], "cardId": cardId}

    # 벡터스토어에 문서 추가
    vectorstore.add_texts([document], metadatas=[metadata])

# 벡터스토어 저장
vectorstore.persist()
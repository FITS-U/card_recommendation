from dotenv import load_dotenv
load_dotenv()
import json
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import openai

file_path = "C:/Users/user/Desktop/langchain-kr/hk-project/data/card_data456.json"

with open(file_path, "r", encoding="utf-8") as file:
    card_data = json.load(file)

db_path = "C:/Users/user/Desktop/langchain-kr/hk-project/chromaDB1"
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)

cardId = 1
for index, card in card_data.items():

    document = f"Card ID: {cardId}\nCard Name: {card['Card Name']}\nAnnual Fee: {card['Annual_fee']}\nBase Record: {card['Base Record']}\nBenefits: {card['Benefits']}"
    metadata = {"Card Name": card["Card Name"], "Index": index, "CardId": cardId}

    vectorstore.add_texts([document], metadatas=[metadata])
    
    cardId += 1
vectorstore.persist()
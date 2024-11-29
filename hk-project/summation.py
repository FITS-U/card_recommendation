from langchain.embeddings.openai import OpenAIEmbeddings 
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()
import openai
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

# ChromaDB 초기화
db_path = "C:/Users/user/Desktop/langchain-kr/hk-project/chromaDB1"
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)

# 사용자 입력 받기 (cardId 입력)
card_id = input("카드 ID를 입력하세요 (예: 16): ")

# Retriever 설정
retriever = vectorstore.as_retriever(
    search_type='mmr',
    search_kwargs={'k': 3, 'lambda_mult': 0.5}
)

# Prompt Template 수정 (cardId 기반 설명)
prompt_template = ChatPromptTemplate.from_template(
    """
    시스템 역할:
    당신은 카드 혜택 요약 전문가입니다.
    아래의 지시사항을 따르세요:
    - 입력받는 cardId에 해당하는 혜택을 요약하여 설명하세요.
    - cardID와 카드명은 필수로 제시하세요.
    - json 형식으로 응답하세요.
 
    예시 형식:
    {{
        "cardId" : 16,
        "CardName" : "우리 K-패스",
        "summation" : "주유비 최대 5% 할인과 대중교통 이용 시 최대 10% 적립 혜택 제공!"
    }}

    유저 역할:
    cardId: {question}

    카드 데이터:
    {context}

    위 데이터를 기반으로 cardId와 연결된 카드의 혜택을 요약하여 설명하세요.
    """
)

# Language Model 설정
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)

# RAG 체인 생성
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=False,
    chain_type_kwargs={"prompt": prompt_template, "document_variable_name": "context"}
)

# RAG 실행 (cardId를 query로 사용)
response = rag_chain({"query": str(card_id)})

# 결과 출력
print("카드 혜택 요약:")
print(response["result"])

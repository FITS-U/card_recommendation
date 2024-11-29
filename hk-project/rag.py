from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv
load_dotenv()
import openai
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

db_path = "C:/Users/user/Desktop/langchain-kr/hk-project/chromaDB1"
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)

query = input("사용자 소비 내역을 입력하세요 (예: 식당: 80000, 카페: 45000): ")

retriever = vectorstore.as_retriever(
    search_type='mmr',
    search_kwargs={'k': 5, 'lambda_mult': 0.5}
)

prompt_template = ChatPromptTemplate.from_template(
    """
    시스템 역할:
    당신은 카드 추천 매니저입니다.
    아래의 지시사항을 따르세요:
    - 각 카드에 대해 소비 내역과 연결된 구체적인 혜택과 이유를 간단히 설명하세요.
    - 혜택의 할인 한도를 초과하지 않도록 추천하세요.
    - 혜택 할인 한도를 알 수 없는 경우는 정확한 할인 금액은 제시하지 마세요.

    예시 형식:
        - 카드명 : 현대카드M
        - 연회비 : 국내 3만원, 해외 3만원, 가족 1만원
        - 기준 실적 : 직전 1개월 합계 50만원 이상
        혜택
        - 혜택 범위 : 주유, 통신, 대중교통 등
        - 혜택 상세 : 혜택 요약된 결과

        - 카드명 : 신한카드 처음
        - 연회비 : 국내 1만5천원, 해외 1만8천원
        - 기준 실적 : 직전 1개월 합계 30만원 이상
        혜택
        - 혜택 범위 : 통신, 외식, 편의점 등
        - 혜택 상세 : 혜택 요약된 결과

        - 카드명 : LOCA Professional
        - 연회비 : 국내 30만원, 해외 30만원, 가족 5만원
        - 기준 실적 : 조건없음
        혜택
        - 혜택 범위 : 영화, 쇼핑, 대형마트 등
        - 혜택 상세 : 혜택 요약된 결과

    유저 역할:
    사용자 소비 내역:
    {question}

    카드 데이터:
    {context}

    위 데이터를 기반으로 가장 적합한 카드 3개를 추천하고, 각 카드의 설명을 위의 형식에 맞게 작성하세요.
    """
)

llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=False,
    chain_type_kwargs={"prompt": prompt_template, "document_variable_name": "context"}
)

response = rag_chain({"query": query})

# 결과 출력
print("추천 카드:")
print(response["result"])

# 참고 문서도 보고 싶으면 return_source_documents=True로 설정 후 아래 코드 활성화
# print("\n참고 문서:")
# for doc in response["source_documents"]:
#     print(doc.page_content)

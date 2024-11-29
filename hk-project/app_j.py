from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI

app = Flask(__name__)

# LangChain 초기화
db_path = "C:/Users/user/Desktop/langchain-kr/hk-project/chromaDB1"
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)

retriever = vectorstore.as_retriever(
    search_type='mmr',
    search_kwargs={'k': 5, 'lambda_mult': 0.5}
)

# JSON 데이터를 다룰 수 있도록 프롬프트 수정
prompt_template = ChatPromptTemplate.from_template(
    """
    시스템 역할:
    당신은 카드 추천 매니저입니다. 친절한 말투로 응답하세요.
    아래의 지시사항을 따르세요:
    - *json 객체* 형식으로 제시하세요.
    - 각 카드에 대해 소비 내역과 연결된 혜택과 이유를 간단히 설명하세요.
    - cardID는 필수로 제시하세요.
    - 예시 형식 이외의 내용은 넣지 마세요.

    예시 형식:

    "cardId" : 27,
    "ment" : 온라인 쇼핑 10% 적립! 신한편편 카드를 사용하시고 혜택 받아보세요!,
    "details" : 이세연님의 경우 이 카드를 사용하셨다면 쇼핑에서 약 5,600원의 절약 가능!,

    "cardId" : 164,
    "ment" : 대형마트 3% 할인! 농협 하나로 카드를 사용하시고 혜택 받아보세요!,
    "details" : 이세연님의 경우 이 카드를 사용하셨다면 대형마트에서 약 5,600원의 절약 가능!,

    "cardId" : 59,
    "ment" : 편의점 5% 적립! 국민 미니 카드를 사용하시고 혜택 받아보세요!,
    "details" : 이세연님의 경우 이 카드를 사용하셨다면 쇼핑에서 약 5,600원의 절약 가능!

    유저 역할:
    사용자 소비 내역(JSON 형식):
    {question}

    카드 데이터:
    {context}

    위 데이터를 기반으로 가장 적합한 카드 3개를 추천하고, 각 카드의 설명을 위의 형식에 맞게 작성하세요.
    """
)

llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.3)

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=False,
    chain_type_kwargs={"prompt": prompt_template}
)

@app.route('/recommend', methods=['POST'])
def recommend():
    # 사용자 JSON 데이터 받아오기
    user_data = request.json

    # JSON 데이터를 문자열로 변환 (프롬프트에 넣기 위함)
    query_json_str = str(user_data)
    
    # RAG 실행
    response = rag_chain({"query": query_json_str})
    
    # 결과 반환
    return jsonify({"recommended_cards": response["result"]})

if __name__ == '__main__':
    app.run(debug=True, port=9090)
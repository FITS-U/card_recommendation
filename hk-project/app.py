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
    search_kwargs={'k': 5, 'lambda_mult': 0.7}
)

prompt_template = ChatPromptTemplate.from_template(
    """
    시스템 역할:
    당신은 카드 추천 매니저입니다. 친절한 말투로 응답하세요.
    아래의 지시사항을 따르세요:
    - json 형식으로 제시하세요.
    - 각 카드에 대해 소비 내역과 연결된 혜택과 이유를 간단히 설명하세요.
    - cardID는 필수로 제시하세요.
    - details에는 지출내역을 기반으로 할인받을 수 있는 금액을 대략적으로 계산하여 제시하되 할인한도를 초과하지 않는 내에서 제시해주세요.
    - 한 혜택에 집중하지 말고  골고루 추천해주세요.
    - 예시 형식 이외의 내용은 넣지 마세요.
 
    예시 형식:
    "cardId" : 27,
    "ment" : 온라인 쇼핑 10% 적립! 신한편편 카드를 사용하시고 혜택 받아보세요!,
    "details" : 이세연님의 경우 이 카드를 사용하셨다면 쇼핑에서 약 5,600원의 절약 가능!,
    "cardId : 156,
    "ment" : 주유비1% 청구할인! 롯데어디로든 카드를 사용하시고 주유혜택 받아요세요!,
    "details" : 이세연님의 경우 이 카드를 사용하셨다면 주유비 약 4,200원의 절약 가능!,
    "cardId" : 68,
    "ment" : 스타벅스, 이디야 등 카페 5% 할인! 삼성goodgood 카드를 사용하시고 통신요금 낮춰보세요!,
    "details" : 이세연님의 경우 이 카드를 사용하셨다면 카페/베이커리 약 7,500원의 절약 가능!,

    유저 역할:
    사용자 소비 내역:
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
    chain_type_kwargs={"prompt": prompt_template, "document_variable_name": "context"}
)

@app.route('/recommend', methods=['POST'])
def recommend():
    # 사용자 입력 데이터 받아오기
    user_data = request.json
    query = user_data.get('query', None)
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # RAG 실행
    response = rag_chain({"query": query})
    
    # 결과 반환
    return jsonify({"recommended_cards": response["result"]})

if __name__ == '__main__':
    app.run(debug=True, port=9090)

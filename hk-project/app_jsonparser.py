from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import json

# Flask 앱 초기화
app = Flask(__name__)

# LangChain 초기화
db_path = "C:/Users/user/Desktop/langchain-kr/hk-project/chromaDB1"
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)

retriever = vectorstore.as_retriever(
    search_type='mmr',
    search_kwargs={'k': 5, 'lambda_mult': 0.7}
)

# 프롬프트 템플릿 정의
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    시스템 역할:
    당신은 카드 추천 매니저입니다. 다음의 규칙에 따라 JSON 형식으로 응답하세요:
    1. 응답은 반드시 JSON 배열 형식으로 작성하세요.
    2. 각 항목은 `cardId`, `ment`, `details` 필드를 포함해야 합니다.
    3. 소비금액이 큰 카테고리 상위 3개 각각 가장 좋은 혜택을 주는 카드를 찾으세요.
    4. ```json 코드 블록 태그를 절대 사용하지 마세요.
    5. 예시 형식을 따르세요:
    [
        {{"cardId": 154, "ment": "카페에서 10% 할인! 신한카드 Shopping으로 커피를 즐기세요!", "details": "홍길동님의 경우 이 카드를 사용하셨다면 카페에서 약 10,000원의 절약 가능!"}},
        {{"cardId": 268, "ment": "온라인 쇼핑에서 20% 할인! 참! 좋은 kt wiz 카드로 스마트한 소비를!", "details": "홍길동님의 경우 온라인 쇼핑에서 260,000원을 사용하셨다면 약 52,000원의 절약 가능!"}},
        {{"cardId": 165, "ment": "스타벅스에서 2,000원 할인! 쇼핑앤조이 카드로 커피를 즐기세요!", "details": "홍길동님의 경우 스타벅스에서 4,000원 이상 결제 시 2,000원의 절약 가능!"}}
    ]

    사용자 소비 내역(JSON 형식):
    {question}

    카드 데이터:
    {context}

    위 데이터를 기반으로 가장 적합한 카드 3개를 추천하고, 각 카드의 설명을 JSON 형식으로 작성하세요.
    """
)

# LLMChain 정의
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.3)
llm_chain = LLMChain(llm=llm, prompt=prompt_template)

@app.route('/recommend', methods=['POST'])
def recommend():
    # 사용자 입력 데이터 받아오기
    user_data = request.json
    question = json.dumps(user_data, ensure_ascii=False)

    # 벡터스토어에서 문서 검색
    context_docs = retriever.get_relevant_documents(question)
    context = "\n".join([doc.page_content for doc in context_docs])

    # LLMChain 실행
    try:
        response = llm_chain.run({"context": context, "question": question})

        # JSON 변환
        response_json = json.loads(response)
        return jsonify({"recommended_cards": response_json})
    except json.JSONDecodeError:
        return jsonify({"error": "응답이 올바른 JSON 형식이 아닙니다."}), 500
    except Exception as e:
        return jsonify({"error": f"예기치 않은 오류: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=False, port=9090)

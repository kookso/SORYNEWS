from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages import BaseMessage

import os
from dotenv import load_dotenv

# 메시지 직렬화/역직렬화 유틸
def serialize_message(msg: BaseMessage):
    return {
        "type": msg.__class__.__name__.replace("Message", "").lower(),
        "content": msg.content
    }

def deserialize_message(msg_dict) -> BaseMessage:
    cls_map = {
        "system": SystemMessage,
        "human": HumanMessage,
        "ai": AIMessage
    }
    return cls_map[msg_dict["type"]](content=msg_dict["content"])

# 환경변수 로드
load_dotenv()

# 뉴스 챗봇
class ChatbotView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        article_id = request.data.get("article_id")
        title = request.data.get("title")
        write_date = request.data.get("write_date")
        content = request.data.get("content")
        question = request.data.get("question")

        if not all([article_id, title, write_date, content, question]):
            return Response({"message": "입력값이 부족합니다."}, status=400)

        session_key = f"chat_history_{request.user.id}_{article_id}"
        raw_messages = request.session.get(session_key, [])
        messages = [deserialize_message(m) for m in raw_messages]

        # 항상 최신 기사 정보로 SystemMessage 재삽입
        messages = [m for m in messages if not isinstance(m, SystemMessage)]
        system_msg = SystemMessage(content=f"""
            너는 건방진 monday 버전 뉴스 비서 <깡통>이야.
            - 아래 기사 내용만 바탕으로 사용자의 질문에 **최대한 구체적으로 대답**해야 해.
            - **기사 내용에 기술 이름, 숫자, 날짜, 고유명사가 나오면 반드시 반영해야 해.**
            - 내용이 없는 경우에만 "꺼져."라고 말해.

            ### 제목: {title}
            ### 작성일: {write_date}
            ### 내용: {content}
        """)
        messages.insert(0, system_msg)

        # 사용자 질문 추가
        messages.append(HumanMessage(content=question))

        # GPT 호출
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        response = llm.invoke(messages[-20:])  # 최근 20개까지만 전달

        # 응답 저장
        messages.append(AIMessage(content=response.content))
        request.session[session_key] = [serialize_message(m) for m in messages]

        return Response({"response": response.content})


# 대화 초기화
class ChatbotResetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, article_id):
        session_key = f"chat_history_{request.user.id}_{article_id}"
        if session_key in request.session:
            del request.session[session_key]
        return Response({"message": "대화가 초기화되었습니다."})

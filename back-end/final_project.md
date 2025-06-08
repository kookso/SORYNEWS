# Django + LangChain (v0.3+) + OpenAI 기반 뉴스 챗봇 구현 문서

> 기사 기반 대화형 챗봇  
> LangChain의 ChatPromptTemplate + ChatOpenAI 사용  
> Django 세션 기반 대화 맥락 기억  
> 명시적 세션 종료 처리 포함  
> 사용자 질문 흐름까지 기억 가능한 구조  
> 최신 LangChain v0.3+ API 반영

---

## 1. 프로젝트 개요

### 목적
- 사용자가 특정 뉴스 기사를 보며 질문을 하면, 해당 기사 내용을 바탕으로 친절하게 답해주는 챗봇을 구현합니다.
- 같은 기사에서 여러 질문을 할 경우, 이전 대화 흐름을 기억하여 맥락 있는 응답이 가능합니다.

---

## 2. 기술 스택

| 구성 요소 | 도구/라이브러리 |
|----------|------------------|
| 백엔드   | Django REST Framework |
| LLM      | LangChain + OpenAI GPT-4o-mini |
| 프롬프트 | ChatPromptTemplate |
| 대화 저장 | Django 세션 (request.session) |
| 메시지 형식 | LangChain SystemMessage, HumanMessage, AIMessage |

---

## 3. 설치

```bash
pip install langchain==0.3.25 langchain-openai==0.3.17
```

---

## 4. LangChain 구성 요소

### 4.1 ChatPromptTemplate

```python
from langchain_core.prompts import ChatPromptTemplate

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", """너는 친절한 뉴스 비서 <뉴비>야.
- 뉴스 기사 내용을 바탕으로 사용자의 질문에 쉽고 친절하게 대답해줘.
- 기사의 내용에 없는 정보는 "죄송해요, 여기 보고계신 기사에서는 찾을 수 없네요."라고 말해줘.

### 제목: {title}
### 작성일: {write_date}
### 내용: {content}
"""),
    ("human", "{question}")
])
```

### 4.2 ChatOpenAI

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")
```

### 4.3 ChatBot Test

```python
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 1. .env 파일 로드
load_dotenv()
# OPENAI_API_KEY가 환경변수로 등록된 상황이라 하면 openai_key를 따로 선언하지 않을 수 있음

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", """너는 친절한 뉴스 비서 <뉴비>야.
- 뉴스 기사 내용을 바탕으로 사용자의 질문에 쉽고 친절하게 대답해줘.
- 기사의 내용에 없는 정보는 "죄송해요, 여기 보고계신 기사에서는 찾을 수 없네요."라고 말해줘.

### 제목: {title}
### 작성일: {write_date}
### 내용: {content}
"""),
    ("human", "{question}")
])

llm = ChatOpenAI(model="gpt-4o-mini")
chain = chat_prompt | llm

test_input = {
    "title": "삼성전자, 인공지능 반도체 신규 공정 발표",
    "write_date": "2025-05-22",
    "content": "삼성전자는 오늘 차세대 인공지능 반도체를 위한 신규 3나노 공정을 발표했다. 이 기술은 기존 대비 성능을 20% 향상시키고 전력 효율을 30% 개선했다. 특히 데이터 센터, 모바일 기기, 자율주행차 등 고성능 컴퓨팅 분야에서 활용이 기대된다.",
    "question": "이 기술은 어떤 분야에 활용될 수 있나요?"
}

response = chain.invoke(test_input)
print(response.content)
```

---

## 5. Django APIView (LangChain 기반 예시 코드)

```python
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ChatbotView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"message": "인증이 필요합니다."}, status=401)

        article_id = request.data.get("article_id")
        title = request.data.get("title")
        write_date = request.data.get("write_date")
        content = request.data.get("content")
        question = request.data.get("question")

        if not all([title, write_date, content, question]):
            return Response({"message": "입력값이 부족합니다."}, status=400)

        session_key = f"chat_history_{request.user.id}_{article_id}"
        if session_key not in request.session:
            prompt = f"너는 친절한 뉴스 비서 <뉴비>야. ... 기사 제목: {article.title}, 작성일: {article.write_date}, 내용: {article.content}"
            request.session[session_key] = [SystemMessage(content=prompt)]

        messages = request.session[session_key]
        messages.append(HumanMessage(content=question))

        llm = ChatOpenAI(model="gpt-4o-mini")
        messages = messages[-20:] # 최근 20개 -> LLM의 context memory를 사용하는 구조 아님
        answer = llm.invoke(messages)
        messages.append(AIMessage(content=answer.content))
        request.session[session_key] = messages

        return Response({"response": answer.content})
```

---

## 6. 대화 초기화

```python
class ChatbotResetView(APIView):
    def post(self, request, article_id):
        if not request.user.is_authenticated:
            return Response({"message": "인증이 필요합니다."}, status=401)
        session_key = f"chat_history_{request.user.id}_{article_id}"
        if session_key in request.session:
            del request.session[session_key]
        return Response({"message": "대화가 초기화되었습니다."})
```

---

## 7. 메시지 구조 예시

```json
[
  {"role": "system", "content": "...기사 내용..."},
  {"role": "user", "content": "요약해줘"},
  {"role": "assistant", "content": "...요약..."},
  {"role": "user", "content": "작성자는 누구야?"}
]
```

---

## 8. 정리

| 항목 | 내용 |
|------|------|
| 기사 기반 대화 | 프롬프트로 설정 |
| 사용자 질문 기억 | 메시지 리스트 누적 |
| LangChain 최신 API 사용 | v0.3+ 구조에 맞춤 |
| Django 기반 REST 구조 | 인증/세션 완비 |

---

## 9. 참고 문서

- https://python.langchain.com/docs/integrations/chat/openai/
- https://python.langchain.com/docs/modules/prompts/chat/
- https://docs.djangoproject.com/en/stable/topics/http/sessions/

# preprocess.py
import os
import ast
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

def preprocess_content(content):
    import tiktoken
    if not content:
        return ""
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(content)
    if len(tokens) > 5000:
        truncated_tokens = tokens[:5000]
        return encoding.decode(truncated_tokens)
    return content

def transform_extract_keywords(text):
    text = preprocess_content(text)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": '다음 뉴스 기사 내용을 분석한 뒤, 핵심 키워드 5개를 한국어로 뽑아서 배열 형식으로 응답해주세요. 예: ["금리", "미국", "인플레이션", "소비", "연준"]'
            },
            {"role": "user", "content": text}
        ],
        max_tokens=100
    )
    keywords_str = response.choices[0].message.content.strip()

    try:
        keywords = ast.literal_eval(keywords_str)
    except Exception:
        keywords = []

    return keywords

def transform_to_embedding(text: str) -> list[float]:
    text = preprocess_content(text)

    client = OpenAI()
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding

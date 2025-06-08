# shared/yna.py
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import feedparser, json, re, ssl, time

KAFKA_BROKER = "kafka:9092"
context = ssl._create_unverified_context()
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

#"문화_연예":"https://www.yna.co.kr/rss/entertainment.xml"
RSS_FEEDS = {
    "economy": ("경제", "https://www.yna.co.kr/rss/economy.xml"),
    "politics": ("정치", "https://www.yna.co.kr/rss/politics.xml"),
    "society": ("사회", "https://www.yna.co.kr/rss/society.xml"),
    "industry": ("산업", "https://www.yna.co.kr/rss/industry.xml"),
    "culture": ("문화_연예", "https://www.yna.co.kr/rss/culture.xml"),
    "sports": ("스포츠", "https://www.yna.co.kr/rss/sports.xml"),
    "health": ("건강", "https://www.yna.co.kr/rss/health.xml")
    
}

def extract_journalist(summary, content):
    pattern = r"([가-힣]{2,4})\s?기자"
    match = re.search(pattern, summary or "")
    if not match:
        match = re.search(pattern, content[:150])
    return match.group(1) + " 기자" if match else "작성자 없음"

def crawl(entry, category):
    try:
        res = requests.get(entry.link, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        soup = BeautifulSoup(res.content, 'html.parser')
        origin = soup.select_one('.story-news')
        if not origin:
            return None

        content = " ".join([p.get_text(strip=True) for p in origin.find_all('p') if not p.attrs])
        journalist = extract_journalist(entry.summary, content)

        return {
            "title": entry.title,
            "writer": journalist,
            "write_date": datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%dT%H:%M:%S"),
            "category": category,
            "content": content,
            "url": entry.link,
            "summary": entry.summary,
            "source": "연합뉴스"
        }
    except Exception:
        return None

def run():
    seen = set()
    for topic, (category_kr, url) in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        print(f"가져온 뉴스 수: {len(feed.entries)}")
        if not feed.entries:
            continue
        for entry in feed.entries[:6]:  
            if entry.link in seen:
                continue
            seen.add(entry.link)

            article = crawl(entry, category_kr)
            if article:
                producer.send(topic, article)
                print(f"[연합] {category_kr} - {article['title']}")

    producer.flush()

    ''' 대용량용 (도커 용량 따로 설정하지않으면 터짐 주의)
        for entry in feed.entries:
            if entry.link in seen:
                continue
            seen.add(entry.link)
            article = crawl(entry, category_kr)
            if article:
                producer.send(topic, article)
                print(f"[연합] {category_kr} - {article['title']}")
    producer.flush()
    '''

if __name__ == "__main__":
    run()
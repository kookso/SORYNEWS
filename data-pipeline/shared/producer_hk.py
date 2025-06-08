# shared/hk.py
from bs4 import BeautifulSoup
from datetime import datetime
from kafka import KafkaProducer
import feedparser, json, ssl, requests

KAFKA_BROKER = "kafka:9092"
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8")
)

RSS_FEEDS = {
    "economy": ("경제", "https://www.hankyung.com/feed/economy"),
    "politics": ("정치", "https://www.hankyung.com/feed/politics"),
    "society": ("사회", "https://www.hankyung.com/feed/society"),
    "international": ("국제", "https://www.hankyung.com/feed/international"),
    "finance": ("증권", "https://www.hankyung.com/feed/finance"),
    "real_estate": ("부동산", "https://www.hankyung.com/feed/realestate"),
    "entertainment": ("문화_연예", "https://www.hankyung.com/feed/entertainment"),
    "sports": ("스포츠", "https://www.hankyung.com/feed/sports"),
    "it": ("IT", "https://www.hankyung.com/feed/it"),
}

def crawl(entry, category_kr):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(entry.link, headers=headers, timeout=5)
        soup = BeautifulSoup(res.content, "html.parser")

        content_tag = soup.select_one("#articletxt")
        content = content_tag.get_text(separator="\n").strip() if content_tag else "본문 없음"

        meta_author = soup.find("meta", {"property": "dable:author"})
        writer = meta_author.get("content", "").strip() if meta_author else "작성자 없음"

        return {
            "title": entry.title,
            "writer": writer,
            "write_date": datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S"),
            "category": category_kr,
            "content": content,
            "url": entry.link,
            "summary": getattr(entry, "summary", ""),
            "source": "한국경제"
        }
    except Exception as e:
        print(f"[한경 오류] {entry.link} - {e}")
        return None

def run():
    seen = set()
    for topic, (category_kr, url) in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        print(f"{category_kr} 기사 수: {len(feed.entries)}")
        if not feed.entries:
            continue
        for entry in feed.entries[:6]: 
            if entry.link in seen:
                continue
            seen.add(entry.link)

            article = crawl(entry, category_kr)
            if article:
                producer.send(topic, article)
                print(f"[한경] {category_kr} - {article['title']}")

    producer.flush()

    ''' 대용량용
        for entry in feed.entries:
            if entry.link in seen:
                continue
            seen.add(entry.link)
            article = crawl(entry, category_kr)
            if article:
                producer.send(topic, article)
                print(f"[한경] {category_kr} - {article['title']}")
    producer.flush()
    '''

if __name__ == "__main__":
    run()

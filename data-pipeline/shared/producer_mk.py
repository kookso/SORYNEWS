# shared/mk.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from kafka import KafkaProducer
import feedparser, json, ssl, time

KAFKA_BROKER = "kafka:9092"
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

RSS_FEEDS = {
    "economy": ("경제", "https://www.mk.co.kr/rss/30100041/"),
    "politics": ("정치", "https://www.mk.co.kr/rss/30200030/"),
    "society": ("사회", "https://www.mk.co.kr/rss/50400012/"),
    "international": ("국제", "https://www.mk.co.kr/rss/30300018/"),
    "industry": ("산업", "https://www.mk.co.kr/rss/50100032/"),
    "stock": ("증권", "https://www.mk.co.kr/rss/50200011/"),
    "real_estate": ("부동산", "https://www.mk.co.kr/rss/50300009/"),
    "entertainment": ("문화_연예", "https://www.mk.co.kr/rss/30000023/"),
    "sports": ("스포츠", "https://www.mk.co.kr/rss/71000001/"),
    "game": ("게임", "https://www.mk.co.kr/rss/50700001/")
}

def crawl(entry, category_kr):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(entry.link, headers=headers, timeout=5)
        soup = BeautifulSoup(res.content, 'html.parser')

        content_tags = soup.select('.art_txt p, .art_body p, .art_read p, .news_cnt_detail_wrap p')
        content = "\n".join([p.get_text(strip=True) for p in content_tags if p.get_text(strip=True)]) or "본문 없음"

        writer_tag = soup.select_one("dt.name")
        writer = writer_tag.get_text(strip=True) if writer_tag else "작성자 없음"

        return {
            "title": entry.title,
            "writer": writer,
            "write_date": datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M:%S'),
            "category": category_kr,
            "content": content,
            "url": entry.link,
            "summary": getattr(entry, "summary", ""),
            "source": "매일경제"
        }

    except Exception as e:
        print(f"[매경 오류] {entry.link} - {e}")
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
                print(f"[매경] {category_kr} - {article['title']}")

    producer.flush()

    ''' 대용량용 (간단 테스트용이라면 위의 코드 적용)
        for entry in feed.entries:
            if entry.link in seen:
                continue
            seen.add(entry.link)
            article = crawl(entry, category_kr)
            if article:
                producer.send(topic, article)
                print(f"[매경] {category_kr} - {article['title']}")
    producer.flush()
    '''


if __name__ == "__main__":
    run()

-- pgvector 확장 활성화 (벡터 검색 지원)
CREATE EXTENSION IF NOT EXISTS vector;

-- 뉴스 기사 테이블 생성
CREATE TABLE IF NOT EXISTS news_article (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    writer VARCHAR(255),
    write_date TIMESTAMP,
    category VARCHAR(100),
    content TEXT NOT NULL,
    url VARCHAR(200),
    summary TEXT,
    source VARCHAR(100),
    keywords JSON,
    embedding VECTOR(1536) ,
    updated_at TIMESTAMP DEFAULT now()

);
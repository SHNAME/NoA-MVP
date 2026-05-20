from pathlib import Path

import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


class E5EmbeddingFunction:
    """문서 저장 시 'passage: ', 쿼리 시 'query: ' 접두사를 붙이는 e5 전용 임베딩 함수"""
    def __init__(self):
        self.model = SentenceTransformer("intfloat/multilingual-e5-small")

    def name(self) -> str:
        return "multilingual-e5-small"

    def __call__(self, input: list[str]) -> list[list[float]]:
        prefixed = ["passage: " + text for text in input]
        return self.model.encode(prefixed, normalize_embeddings=True).tolist()

    def encode_query(self, question: str) -> list[float]:
        return self.model.encode("query: " + question, normalize_embeddings=True).tolist()


class RagService:
    def __init__(self):
        load_dotenv()
        self.openai = OpenAI()

        db_path = str(Path(__file__).parent.parent / "vector_db" / "chroma")
        self.client = chromadb.PersistentClient(path=db_path)

        self.embedding_function = E5EmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name="government_docs",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )

    def count_documents(self):
        return self.collection.count()

    #페이지 단위로 추출한 문자열을 줄 단위 chunk 여러 개로 분리
    def split_text(self, text: str, chunk_size: int = 600, overlap_lines: int = 2):
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        chunks = []
        current_lines = []
        current_len = 0

        for line in lines:
            if current_len + len(line) > chunk_size and current_lines:
                chunks.append("\n".join(current_lines))
                current_lines = current_lines[-overlap_lines:]
                current_len = sum(len(l) for l in current_lines)

            current_lines.append(line)
            current_len += len(line)

        if current_lines:
            chunks.append("\n".join(current_lines))

        return chunks

    def ingest_text(self, text: str, metadata: dict):
        chunks = self.split_text(text)

        documents = []
        metadatas = []
        ids = []

        source = metadata.get("source", "unknown")
        page = metadata.get("page", 0)

        for index, chunk in enumerate(chunks):
            chunk_id = f"{source}_p{page}_chunk{index}"
            documents.append(chunk)
            metadatas.append({**metadata, "chunk_index": index})
            ids.append(chunk_id)

        if documents:
            self.collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

    def search(self, question: str, top_k: int = 7):
        query_embedding = self.embedding_function.encode_query(question)
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]

        print(f"\n[검색 결과] 질문: {question}")
        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
            print(f"  [{i}] 거리: {dist:.4f} | {meta.get('source')} {meta.get('page')}p | {doc[:80]}...")

        return [
            {"content": doc, "metadata": meta}
            for doc, meta in zip(documents, metadatas)
        ]

    def ask(self, question: str):
        searched_docs = self.search(question)

        context = "\n\n".join(
            [
                f"[출처: {doc['metadata'].get('source')}"
                for doc in searched_docs
            ]
        )

        prompt = f"""
아래 [문서 내용만] 근거로 사용해서 [질문]에 답변해.
규칙:
1. 문서에 있는 내용만으로 답변을 해 .
2. 문서에서 확인할 수 없는 내용은 "제공된 문서에서는 확인할 수 없습니다."라고 답변해.
3. 가능하면 답변 마지막에 출처를 함께 표시해.
4. 숫자, 날짜, 지원금액, 조건은 문서 표현을 그대로 유지해.
5. 답변은 항상 한국어로 해.


[문서 내용]
{context}

[질문]
{question}
"""
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 문서를 기반으로 답변하는 RAG 챗봇이다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content

from pathlib import Path

from modules.rag_service import RagService
from modules.pdf_parser import get_pdf_pages_text


DOCS_DIR = Path(__file__).parent / "docs"

# docs 디렉터리 안에 있는 pdf 파일을 읽고, 각 페이지 텍스트를 RagService에 전달 후 Vector DB에 저장하는 함수
def ingest_docs(rag_service):
    pdf_files = list(DOCS_DIR.glob("*.pdf"))

    if not pdf_files:
        print("docs 폴더에 PDF 파일이 없습니다.")
        return 0

    saved_count = 0

    for pdf_file in pdf_files:
        pages = get_pdf_pages_text(pdf_file)

        for page in pages:
            text = page["text"]
            page_number = page["page"]

            if not text.strip():
                continue

            # 목차 페이지 건너뛰기 (목 차 헤더 or ··· 패턴이 많은 페이지)
            if "목 차" in text or text.count("·") > 10:
                continue

            rag_service.ingest_text(
                text=text,
                metadata={
                    "source": pdf_file.name,
                    "page": page_number,
                    "type": "pdf"
                }
            )

            saved_count += 1

    return saved_count


def main():
    rag_service = RagService()
    ingest_docs(rag_service)


if __name__ == "__main__":
    main()
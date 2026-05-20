import re
from pathlib import Path

import pdfplumber


def get_pdf_pages_text(pdf_path: str | Path) -> list[dict]:
    pdf_path = Path(pdf_path)
    pages = []

    with pdfplumber.open(pdf_path) as doc:
        for page_index, page in enumerate(doc.pages, start=1):
            raw_text = page.extract_text() or ""
            lines = []
            #페이지의 문자열 노이즈를 제거하기 위해 줄 단위 분리 후 필터링
            for line in raw_text.splitlines():
                line = line.strip()
                if not line:
                    continue
                # 같은 글자가 3번 이상 연속 반복되는 라인 제거 -> 노이즈 제거
                if re.fullmatch(r'[-_=·.•*]{3,}', line):
                    continue
                lines.append(line)

            pages.append({
                "page": page_index,
                "text": "\n".join(lines)
            })

    return pages


if __name__ == "__main__":
    docs_dir = Path(__file__).parent.parent / "docs"
    pdf_files = list(docs_dir.glob("*.pdf"))

    if not pdf_files:
        print("docs 폴더에 PDF 파일이 없습니다.")

    for pdf_file in pdf_files:
        print(f"\n{'='*60}")
        print(f"파일: {pdf_file.name}")
        print(f"{'='*60}")

        pages = get_pdf_pages_text(pdf_file)
        empty_pages = [p for p in pages if not p["text"].strip()]

        print(f"전체 페이지 수: {len(pages)}")
        print(f"텍스트 없는 페이지 수: {len(empty_pages)} (스캔 이미지 의심)")

        for page in pages[:3]:
            text = page["text"].strip()
            print(f"\n--- {page['page']}페이지 (추출 글자 수: {len(text)}) ---")
            print(text[:300] if text else "[텍스트 없음 - 이미지 기반 페이지]")
            print("...")

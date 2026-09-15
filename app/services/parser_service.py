from pathlib import Path
import pymupdf  # The library installed in your pyproject.toml


class ParserService:

    @staticmethod
    def extract_resume(file_path: str) -> str:
        """
        Opens a PDF file from disk and extracts all plain text across all pages.
        
        :param file_path: The local path to the saved PDF file (e.g. 'uploads/uuid.pdf')
        :return: Extracted text as a clean string
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found at: {file_path}")

        extracted_text = []

        # Open the PDF document using PyMuPDF
        with pymupdf.open(path) as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Extract text from this page
                page_text = page.get_text()
                if page_text:
                    extracted_text.append(page_text.strip())

        # Combine all pages with a newline separator
        return "\n\n".join(extracted_text)
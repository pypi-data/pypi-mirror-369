import json
import os
from pathlib import Path
from typing import Any, List
import httpx
from mcp.server.fastmcp import FastMCP
from mistralai import Mistral, OCRResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("lizeur")


class Lizeur:
    def __init__(self):
        if os.getenv("MISTRAL_API_KEY") is None:
            raise ValueError("MISTRAL_API_KEY is not set")
        self.mistral = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.cache_path = (
            Path.home() / ".cache/lizeur"
            if os.getenv("CACHE_PATH") is None
            else Path(os.getenv("CACHE_PATH"))
        )
        self.cache_path.mkdir(parents=True, exist_ok=True)
        # Representing a list of OCR'ed documents. The value being the name of the document situated in the cache_path.
        self.cached_documents: List[str] = [
            file.name for file in self.cache_path.iterdir() if file.is_file()
        ]

    def read_document(self, path: Path) -> OCRResponse | None:
        """Read a document and return the OCRResponse."""
        logging.info(f"read_document: Reading document {path.name}")
        # Check if the document is already cached
        cached_document_path = self.cache_path / path.name
        if cached_document_path.exists():
            logging.info(f"read_document: Document {path.name} is already cached.")
            try:
                with open(cached_document_path, "r") as f:
                    cached_json = f.read()
                    # Parse JSON and reconstruct OCRResponse
                    cached_data = json.loads(cached_json)
                    return OCRResponse.model_validate(cached_data)
            except (json.JSONDecodeError, ValueError) as e:
                logging.warning(f"Failed to load cached document {path.name}: {e}")
                # Remove corrupted cache file
                cached_document_path.unlink(missing_ok=True)

        # OCR the document
        ocr_response = self._ocr_document(path)
        if ocr_response is None:
            return None

        # Cache the document using model_dump_json() for direct JSON serialization
        try:
            with open(cached_document_path, "w") as f:
                f.write(ocr_response.model_dump_json(indent=2))
            logging.info(f"Successfully cached document {path.name}")
        except Exception as e:
            logging.error(f"Failed to cache document {path.name}: {e}")

        return ocr_response

    def _ocr_document(self, path: Path) -> OCRResponse | None:
        """OCR a document and return the OCRResponse."""
        try:
            # Upload the file to MistralAI
            uploaded_file = self.mistral.files.upload(
                file={
                    "file_name": path.stem,
                    "content": path.read_bytes(),
                },
                purpose="ocr",
            )

            # Process the uploaded file with OCR
            ocr_response = self.mistral.ocr.process(
                document={
                    "type": "file",
                    "file_id": uploaded_file.id,
                },
                model="mistral-ocr-latest",
                include_image_base64=True,
            )

            # Clean up the uploaded file
            try:
                self.mistral.files.delete(uploaded_file.id)
            except Exception as e:
                logging.warning(
                    f"Failed to delete uploaded file {uploaded_file.id}: {e}"
                )

            return ocr_response

        except Exception as e:
            logging.error(f"OCR processing failed for {path}: {e}")
            return None


@mcp.tool()
def read_pdf(absolute_path: str) -> str:
    return Lizeur().read_document(Path(absolute_path)).pages[0].markdown


def main():
    mcp.run("stdio")


if __name__ == "__main__":
    main()

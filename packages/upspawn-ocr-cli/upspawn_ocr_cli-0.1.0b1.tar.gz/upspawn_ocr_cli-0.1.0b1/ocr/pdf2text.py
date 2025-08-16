import os
from typing import Optional

from mistralai import Mistral


class OCRError(Exception):
    """Custom exception for OCR-related errors."""

    pass


def get_api_key() -> str:
    """Get API key from environment variables or module attribute."""
    # First check if it's set via the CLI module
    api_key = globals().get("API_KEY")  # settable by caller; deprecated path

    # Fallback to environment variable
    if not api_key:
        api_key = os.getenv("MISTRAL_API_KEY")

    if not api_key:
        raise OCRError(
            "Mistral API key not found. Set MISTRAL_API_KEY environment variable or configure it via the CLI."
        )

    return api_key


def pdf_to_text(pdf_path: str, api_key: Optional[str] = None) -> str:
    """
    Convert a PDF file to text using Mistral's OCR API.

    Args:
        pdf_path (str): Path to the PDF file
        api_key (str, optional): Mistral API key. If not provided,
                                will attempt to get from environment or global variable.

    Returns:
        str: Extracted text from the PDF

    Raises:
        OCRError: If API key is missing or API call fails
        FileNotFoundError: If PDF file doesn't exist
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not api_key:
        api_key = get_api_key()

    try:
        client = Mistral(api_key=api_key)

        # Upload the PDF file
        with open(pdf_path, "rb") as pdf_file:
            uploaded_pdf = client.files.upload(
                file={
                    "file_name": os.path.basename(pdf_path),
                    "content": pdf_file,
                },
                purpose="ocr",
            )

        # Get signed URL for the uploaded file
        signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)

        # Process OCR
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": signed_url.url,
            },
        )

        # Extract text from all pages
        full_text = ""
        for page in ocr_response.pages:
            if hasattr(page, "markdown") and page.markdown:
                full_text += page.markdown + "\n\n"
            elif hasattr(page, "text") and page.text:
                full_text += page.text + "\n\n"

        if not full_text.strip():
            raise OCRError("No text could be extracted from the PDF")

        return full_text.strip()

    except Exception as e:
        if "api_key" in str(e).lower() or "authentication" in str(e).lower():
            raise OCRError(f"Authentication failed: {e}") from e
        elif "file" in str(e).lower() and "upload" in str(e).lower():
            raise OCRError(f"File upload failed: {e}") from e
        elif "ocr" in str(e).lower():
            raise OCRError(f"OCR processing failed: {e}") from e
        else:
            raise OCRError(f"Unexpected error during OCR processing: {e}") from e


def main() -> None:
    """
    Legacy command-line interface.

    Note: This is maintained for backward compatibility.
    For the modern CLI experience, use: ocr extract <file>
    """
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m ocr.pdf2text <pdf_path>")
        print("\nFor the modern CLI experience, install the package and use:")
        print("  ocr extract <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    try:
        text = pdf_to_text(pdf_path)
        print(text)
    except (OCRError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

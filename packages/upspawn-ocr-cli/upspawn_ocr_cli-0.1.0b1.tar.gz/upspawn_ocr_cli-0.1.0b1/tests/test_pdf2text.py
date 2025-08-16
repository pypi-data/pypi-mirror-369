import pytest

from ocr.pdf2text import OCRError, pdf_to_text


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        pdf_to_text("/no/such/file.pdf", api_key="dummy")


def test_missing_api_key(monkeypatch, tmp_path):
    pdf_path = tmp_path / "a.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n...")

    # Ensure no env
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    # Remove any global API_KEY
    from ocr import pdf2text as mod

    if hasattr(mod, "API_KEY"):
        delattr(mod, "API_KEY")

    with pytest.raises(OCRError):
        pdf_to_text(str(pdf_path))

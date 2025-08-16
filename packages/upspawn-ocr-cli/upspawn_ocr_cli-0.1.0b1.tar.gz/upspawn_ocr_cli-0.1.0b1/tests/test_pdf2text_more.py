from __future__ import annotations

import types
from pathlib import Path

import pytest

import ocr.pdf2text as pdf2


class _Obj:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _make_pdf(tmp_path: Path, name: str = "s.pdf") -> Path:
    p = tmp_path / name
    p.write_bytes(b"%PDF-1.4\n...")
    return p


def _fake_client_with_pages(pages: list[object]):
    class FakeFiles:
        def upload(self, file: dict, purpose: str):  # type: ignore[no-untyped-def]
            return _Obj(id="file_123")

        def get_signed_url(self, file_id: str):  # type: ignore[no-untyped-def]
            return _Obj(url="https://example.com/doc.pdf")

    class FakeOCR:
        def process(self, model: str, document: dict):  # type: ignore[no-untyped-def]
            return _Obj(pages=pages)

    class FakeClient:
        def __init__(self, api_key: str):  # type: ignore[no-untyped-def]
            self.api_key = api_key
            self.files = FakeFiles()
            self.ocr = FakeOCR()

    return FakeClient


def test_pdf_to_text_success_markdown_and_text(monkeypatch, tmp_path: Path):
    pdf_path = _make_pdf(tmp_path)

    pages = [
        _Obj(markdown="# Title\n\nContent"),
        _Obj(text="Plain text page"),
    ]
    FakeClient = _fake_client_with_pages(pages)
    monkeypatch.setattr(pdf2, "Mistral", FakeClient)

    out = pdf2.pdf_to_text(str(pdf_path), api_key="k")
    assert "Title" in out and "Plain text page" in out


def test_pdf_to_text_no_text_raises(monkeypatch, tmp_path: Path):
    pdf_path = _make_pdf(tmp_path)
    FakeClient = _fake_client_with_pages([_Obj(markdown=""), _Obj(text="")])
    monkeypatch.setattr(pdf2, "Mistral", FakeClient)

    with pytest.raises(pdf2.OCRError, match="No text could be extracted"):
        pdf2.pdf_to_text(str(pdf_path), api_key="k")


@pytest.mark.parametrize(
    "exc_msg,expected",
    [
        ("Authentication error: bad api_key", "Authentication failed"),
        ("file upload blew up", "File upload failed"),
        ("ocr processing borked", "OCR processing failed"),
        ("totally unrelated", "Unexpected error during OCR processing"),
    ],
)
def test_pdf_to_text_error_mapping(
    monkeypatch, tmp_path: Path, exc_msg: str, expected: str
):
    pdf_path = _make_pdf(tmp_path)

    class FakeFiles:
        def upload(self, file: dict, purpose: str):  # type: ignore[no-untyped-def]
            raise Exception(exc_msg)

    class FakeClient:
        def __init__(self, api_key: str):  # type: ignore[no-untyped-def]
            self.files = FakeFiles()
            self.ocr = types.SimpleNamespace(process=lambda **_: None)

    monkeypatch.setattr(pdf2, "Mistral", FakeClient)

    with pytest.raises(pdf2.OCRError, match=expected):
        pdf2.pdf_to_text(str(pdf_path), api_key="k")


def test_get_api_key_prefers_global(monkeypatch):
    # Ensure env does not interfere
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    # Set module global API_KEY
    monkeypatch.setattr(pdf2, "API_KEY", "GLOBKEY", raising=False)
    assert pdf2.get_api_key() == "GLOBKEY"


def test_get_api_key_from_env(monkeypatch):
    # Remove any global override
    if hasattr(pdf2, "API_KEY"):
        delattr(pdf2, "API_KEY")
    monkeypatch.setenv("MISTRAL_API_KEY", "ENVKEY")
    assert pdf2.get_api_key() == "ENVKEY"


def test_main_success_and_error_paths(monkeypatch, tmp_path, capsys):
    # Success
    pdf = _make_pdf(tmp_path, "ok.pdf")

    def fake_ok(path: str, api_key: str | None = None) -> str:  # type: ignore[override]
        return "ok"

    import sys as _sys

    monkeypatch.setattr(pdf2, "pdf_to_text", fake_ok)
    monkeypatch.setenv("MISTRAL_API_KEY", "K")
    monkeypatch.setattr(_sys, "argv", ["prog", str(pdf)], raising=False)
    pdf2.main()
    out = capsys.readouterr().out
    assert "ok" in out

    # Usage error (no args)
    monkeypatch.setattr(_sys, "argv", ["prog"], raising=False)
    with pytest.raises(SystemExit) as se:
        pdf2.main()
    assert se.value.code == 1

    # OCR error maps to exit 1
    def fake_err(path: str, api_key: str | None = None) -> str:  # type: ignore[override]
        raise pdf2.OCRError("bad")

    monkeypatch.setattr(pdf2, "pdf_to_text", fake_err)
    monkeypatch.setattr(_sys, "argv", ["prog", str(pdf)], raising=False)
    with pytest.raises(SystemExit) as se2:
        pdf2.main()
    assert se2.value.code == 1

    # KeyboardInterrupt -> exit 130
    def fake_kb(path: str, api_key: str | None = None) -> str:  # type: ignore[override]
        raise KeyboardInterrupt

    monkeypatch.setattr(pdf2, "pdf_to_text", fake_kb)
    monkeypatch.setattr(_sys, "argv", ["prog", str(pdf)], raising=False)
    with pytest.raises(SystemExit) as se3:
        pdf2.main()
    assert se3.value.code == 130

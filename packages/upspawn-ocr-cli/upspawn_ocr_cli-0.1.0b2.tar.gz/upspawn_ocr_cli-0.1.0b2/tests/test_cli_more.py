from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

import ocr.cli as ocr_cli
from ocr.cli import cli


def _make_pdf(path: Path) -> None:
    path.write_bytes(b"%PDF-1.4\n...")


def test_no_valid_files_exits(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        # No such file
        result = runner.invoke(
            cli, ["extract", "missing.pdf"], env={"MISTRAL_API_KEY": "x"}
        )
        assert result.exit_code == 1
        assert "No valid files to process" in result.output


def test_verbose_and_quiet_options(monkeypatch):
    runner = CliRunner()

    def fake_pdf_to_text(_p: str, api_key: str | None = None) -> str:  # type: ignore[override]
        return "ok"

    with runner.isolated_filesystem():
        pdf = Path("a.pdf")
        _make_pdf(pdf)
        monkeypatch.setattr(ocr_cli, "pdf_to_text", fake_pdf_to_text)

        # verbose
        res_v = runner.invoke(
            cli, ["extract", str(pdf), "-v"], env={"MISTRAL_API_KEY": "k"}
        )
        assert res_v.exit_code == 0

        # quiet
        res_q = runner.invoke(
            cli, ["extract", str(pdf), "-q"], env={"MISTRAL_API_KEY": "k"}
        )
        assert res_q.exit_code == 0


def test_single_file_all_fail_exits(monkeypatch):
    runner = CliRunner()

    def boom(_p: str, api_key: str | None = None) -> str:  # type: ignore[override]
        raise RuntimeError("boom")

    with runner.isolated_filesystem():
        pdf = Path("a.pdf")
        _make_pdf(pdf)
        monkeypatch.setattr(ocr_cli, "pdf_to_text", boom)
        res = runner.invoke(cli, ["extract", str(pdf)], env={"MISTRAL_API_KEY": "k"})
        assert res.exit_code == 1
        assert "No files were processed successfully" in res.output


def test_batch_shows_failures(monkeypatch):
    runner = CliRunner()

    def boom(_p: str, api_key: str | None = None) -> str:  # type: ignore[override]
        raise RuntimeError("boom")

    with runner.isolated_filesystem():
        f1 = Path("a.pdf")
        f2 = Path("b.pdf")
        _make_pdf(f1)
        _make_pdf(f2)
        monkeypatch.setattr(ocr_cli, "pdf_to_text", boom)

        res = runner.invoke(
            cli,
            ["extract", str(f1), str(f2), "--batch", "--jobs", "1"],
            env={"MISTRAL_API_KEY": "k"},
        )
        assert res.exit_code == 0
        assert "Failed:" in res.output

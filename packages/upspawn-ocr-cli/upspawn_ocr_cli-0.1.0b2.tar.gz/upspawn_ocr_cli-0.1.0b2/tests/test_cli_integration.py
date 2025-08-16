from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from ocr.cli import cli


def _make_pdf(path: Path) -> None:
    path.write_bytes(b"%PDF-1.4\n...")


def test_extract_single_file_stdout(monkeypatch):
    runner = CliRunner()

    def fake_pdf_to_text(_p: str, api_key: str | None = None) -> str:  # type: ignore[override]
        assert api_key == "key"
        return "hello world"

    with runner.isolated_filesystem():
        # Create dummy PDF
        pdf = Path("a.pdf")
        _make_pdf(pdf)

        # Stub OCR call
        import ocr.cli as ocr_cli

        monkeypatch.setattr(ocr_cli, "pdf_to_text", fake_pdf_to_text)

        result = runner.invoke(
            cli, ["extract", str(pdf)], env={"MISTRAL_API_KEY": "key"}
        )
        assert result.exit_code == 0
        assert "hello world" in result.output


def test_extract_single_file_json_output(monkeypatch):
    runner = CliRunner()

    def fake_pdf_to_text(_p: str, api_key: str | None = None) -> str:  # type: ignore[override]
        return "alpha beta"

    with runner.isolated_filesystem():
        pdf = Path("b.pdf")
        _make_pdf(pdf)
        out = Path("out.json")

        import ocr.cli as ocr_cli

        monkeypatch.setattr(ocr_cli, "pdf_to_text", fake_pdf_to_text)

        result = runner.invoke(
            cli,
            ["extract", str(pdf), "-o", str(out), "-f", "json"],
            env={"MISTRAL_API_KEY": "k"},
        )
        assert result.exit_code == 0
        assert out.exists()
        data = json.loads(out.read_text())
        assert data == {"text": "# b.pdf\n\nalpha beta"}


def test_extract_multiple_files_concat(monkeypatch):
    runner = CliRunner()

    def fake_pdf_to_text(p: str, api_key: str | None = None) -> str:  # type: ignore[override]
        return Path(p).stem

    with runner.isolated_filesystem():
        f1 = Path("f1.pdf")
        f2 = Path("f2.pdf")
        _make_pdf(f1)
        _make_pdf(f2)

        import ocr.cli as ocr_cli

        monkeypatch.setattr(ocr_cli, "pdf_to_text", fake_pdf_to_text)

        result = runner.invoke(
            cli, ["extract", str(f1), str(f2)], env={"MISTRAL_API_KEY": "k"}
        )
        assert result.exit_code == 0
        # Should contain headers and both file contents
        assert "# f1.pdf" in result.output
        assert "# f2.pdf" in result.output
        assert "f1" in result.output and "f2" in result.output


def test_extract_batch_output_dir_markdown(monkeypatch):
    runner = CliRunner()

    def fake_pdf_to_text(p: str, api_key: str | None = None) -> str:  # type: ignore[override]
        return f"text for {Path(p).name}"

    with runner.isolated_filesystem():
        f1 = Path("a.pdf")
        f2 = Path("b.pdf")
        _make_pdf(f1)
        _make_pdf(f2)
        out_dir = Path("out")

        import ocr.cli as ocr_cli

        monkeypatch.setattr(ocr_cli, "pdf_to_text", fake_pdf_to_text)

        result = runner.invoke(
            cli,
            [
                "extract",
                str(f1),
                str(f2),
                "--batch",
                "--output-dir",
                str(out_dir),
                "--jobs",
                "1",
                "--format",
                "markdown",
            ],
            env={"MISTRAL_API_KEY": "key"},
        )
        assert result.exit_code == 0
        # Expect two markdown files
        p1 = out_dir / "a.md"
        p2 = out_dir / "b.md"
        assert p1.exists() and p2.exists()
        assert p1.read_text().startswith("# OCR Extracted Text\n\ntext for a.pdf")
        assert p2.read_text().startswith("# OCR Extracted Text\n\ntext for b.pdf")


def test_non_pdf_extension_error():
    runner = CliRunner()
    with runner.isolated_filesystem():
        txt = Path("x.txt")
        txt.write_text("hello")
        result = runner.invoke(cli, ["extract", str(txt)], env={"MISTRAL_API_KEY": "k"})
        # Click group catches and exits with code 1
        assert result.exit_code == 1
        assert "Only PDF files are supported" in result.output


def test_validate_path_errors_directory():
    runner = CliRunner()
    with runner.isolated_filesystem():
        d = Path("dir")
        d.mkdir()
        # Create a .pdf directory to trick suffix
        dirpdf = d / "docs.pdf"
        dirpdf.mkdir()
        result = runner.invoke(
            cli, ["extract", str(dirpdf)], env={"MISTRAL_API_KEY": "k"}
        )
        assert result.exit_code == 1
        assert "Path is not a file" in result.output


def test_version_and_help_commands():
    runner = CliRunner()
    result_v = runner.invoke(cli, ["--version"])
    assert result_v.exit_code == 0
    # Help is printed when no subcommand
    result_h = runner.invoke(cli, [])
    assert result_h.exit_code == 0
    assert "extract" in result_h.output


def test_config_and_set_key(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        # config
        result_cfg = runner.invoke(cli, ["config"], env={})
        assert result_cfg.exit_code == 0
        assert "Current Configuration" in result_cfg.output

        # set-key with argument (non-interactive)
        result_set = runner.invoke(cli, ["set-key", "abc123"])  # type: ignore[arg-type]
        assert result_set.exit_code == 0
        content = Path(".env").read_text()
        assert "MISTRAL_API_KEY=abc123" in content

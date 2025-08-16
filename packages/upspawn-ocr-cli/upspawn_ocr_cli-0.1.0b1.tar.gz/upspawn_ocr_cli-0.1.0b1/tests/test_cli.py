from click.testing import CliRunner

from ocr.cli import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "extract" in result.output


def test_extract_requires_api_key(tmp_path, monkeypatch):
    pdf_path = tmp_path / "a.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n...")

    # Ensure env var is not visible to the CLI invocation
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    runner = CliRunner()
    result = runner.invoke(cli, ["extract", str(pdf_path)], env={"MISTRAL_API_KEY": ""})
    assert result.exit_code != 0
    assert "API key" in result.output

# Mistral OCR CLI

[![CI](https://github.com/upspawn/mistral-ocr-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/upspawn/mistral-ocr-cli/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mistral-ocr-cli.svg)](https://pypi.org/project/mistral-ocr-cli/)
[![Python](https://img.shields.io/pypi/pyversions/mistral-ocr-cli.svg)](https://pypi.org/project/mistral-ocr-cli/)
[![License](https://img.shields.io/pypi/l/mistral-ocr-cli.svg)](LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Modern, polished CLI to extract text from PDFs using the Mistral OCR API.

## Features

- Elegant TUI with progress bars and rich output
- Single file or batch processing
- Output in text, JSON, or Markdown
- Parallel batch processing with `--jobs`
- Config helper and `.env` support

## Quickstart

1) Install

```bash
uv tool install mistral-ocr-cli  # via pipx-like tool install
# or
uv pip install mistral-ocr-cli   # into current environment
```

2) Configure API key

```bash
export MISTRAL_API_KEY=your_key_here
# or
echo "MISTRAL_API_KEY=your_key_here" >> .env
```

3) Extract text

```bash
ocr extract file.pdf -o out.txt
ocr extract file1.pdf file2.pdf --batch --output-dir outputs --jobs 4
```

## Usage

```bash
ocr extract [OPTIONS] FILES...

Options:
  -o, --output PATH            Output file (single-file mode)
  -f, --format [text|json|markdown]
  -b, --batch                  Enable batch mode
  -O, --output-dir PATH        Directory for batch outputs
  -j, --jobs INTEGER RANGE     Parallel jobs for batch [default: 1]
  -v, --verbose                Verbose logs
  -q, --quiet                  Only errors
  --version                    Show version
  --help                       Show help
```

## Programmatic use

```python
from ocr.pdf2text import pdf_to_text

text = pdf_to_text("/path/file.pdf")
```

## Development

```bash
uv pip install -e .[dev]
uv run pre-commit install
uv run pytest -q
```

Releasing is handled via standard tags and GitHub Releases.

## License

MIT


## Test coverage

```bash
# Terminal report
make coverage

# HTML report in htmlcov/
make coverhtml
```


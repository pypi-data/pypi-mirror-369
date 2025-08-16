"""
Modern CLI for OCR text extraction from PDFs using Mistral API.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from . import __version__
from .pdf2text import pdf_to_text

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
logger = logging.getLogger("ocr")


class OCRError(Exception):
    """Custom exception for OCR-related errors."""

    pass


def setup_api_key() -> str:
    """Get API key from environment or prompt user."""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        console.print(
            Panel.fit(
                "[red]Missing API Key![/red]\n\n"
                "Set your Mistral API key as an environment variable:\n"
                "[cyan]export MISTRAL_API_KEY=your_api_key_here[/cyan]\n\n"
                "Or create a .env file in your project directory with:\n"
                "[cyan]MISTRAL_API_KEY=your_api_key_here[/cyan]",
                title="Configuration Required",
            )
        )
        raise OCRError("API key not configured")
    return api_key


def validate_file_path(file_path: str) -> Path:
    """Validate and return Path object for input file."""
    path = Path(file_path)

    if not path.exists():
        raise OCRError(f"File not found: {file_path}")

    if not path.is_file():
        raise OCRError(f"Path is not a file: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise OCRError(f"Only PDF files are supported. Got: {path.suffix}")

    return path


def format_output(text: str, output_format: str) -> str:
    """Format the extracted text according to the specified format."""
    if output_format == "json":
        return json.dumps({"text": text}, indent=2)
    elif output_format == "markdown":
        return f"# OCR Extracted Text\n\n{text}"
    else:  # plain text
        return text


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version information")
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    """
    🔍 OCR CLI - Modern text extraction from PDFs using Mistral AI

    Extract text from PDF documents with ease and style.
    """
    if version:
        console.print(
            f"[bold blue]OCR CLI[/bold blue] version [green]{__version__}[/green]"
        )
        return

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@cli.command()
@click.argument("files", nargs=-1, required=True, type=click.Path())
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: print to stdout)",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["text", "json", "markdown"], case_sensitive=False),
    default="text",
    help="Output format",
)
@click.option(
    "--batch",
    "-b",
    is_flag=True,
    help="Process multiple files and save each with .txt extension",
)
@click.option(
    "--output-dir",
    "-O",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    help="Directory to write outputs when using --batch",
)
@click.option(
    "--jobs",
    "-j",
    type=click.IntRange(1, 32),
    default=1,
    show_default=True,
    help="Parallel jobs for batch processing",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--quiet", "-q", is_flag=True, help="Suppress all output except errors")
def extract(
    files: tuple[str, ...],
    output: Optional[str],
    output_format: str,
    batch: bool,
    output_dir: Optional[str],
    jobs: int,
    verbose: bool,
    quiet: bool,
) -> None:
    """
    Extract text from PDF files using OCR.

    FILES: One or more PDF files to process

    Examples:

        # Extract text from a single PDF
        ocr extract document.pdf

        # Save to file
        ocr extract document.pdf -o output.txt

        # Process multiple files
        ocr extract file1.pdf file2.pdf file3.pdf --batch

        # Output as JSON
        ocr extract document.pdf --format json
    """
    if verbose:
        logger.setLevel(logging.DEBUG)
    elif quiet:
        logger.setLevel(logging.ERROR)

    try:
        # Setup API key
        api_key = setup_api_key()

        # Validate input files
        validated_files = []
        for file_path in files:
            try:
                validated_files.append(validate_file_path(file_path))
            except OCRError as e:
                console.print(f"[red]Error:[/red] {e}")
                continue

        if not validated_files:
            console.print("[red]No valid files to process![/red]")
            sys.exit(1)

        if batch and len(validated_files) > 1:
            process_batch(
                validated_files, output_format, api_key, output_dir, jobs, quiet
            )
        else:
            process_single_file(validated_files, output, output_format, api_key, quiet)

    except OCRError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)


def process_single_file(
    files: list[Path],
    output: Optional[str],
    output_format: str,
    api_key: str,
    quiet: bool,
) -> None:
    """Process a single file or multiple files into one output."""
    if len(files) > 1 and not output:
        console.print(
            "[yellow]Warning:[/yellow] Multiple files specified but no output file. Results will be concatenated."
        )

    all_text = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        disable=quiet,
    ) as progress:
        task = progress.add_task("Processing files...", total=len(files))

        for file_path in files:
            if not quiet:
                progress.update(task, description=f"Processing {file_path.name}...")

            try:
                text = pdf_to_text(str(file_path), api_key=api_key)
                all_text.append(f"# {file_path.name}\n\n{text}")

                if not quiet:
                    progress.console.print(
                        f"✅ [green]Processed:[/green] {file_path.name}"
                    )

            except Exception as e:
                progress.console.print(f"❌ [red]Failed:[/red] {file_path.name} - {e}")
                continue
            finally:
                progress.advance(task)

    if not all_text:
        console.print("[red]No files were processed successfully![/red]")
        sys.exit(1)

    # Combine all text
    combined_text = "\n\n---\n\n".join(all_text)
    formatted_output = format_output(combined_text, output_format)

    if output:
        Path(output).write_text(formatted_output, encoding="utf-8")
        if not quiet:
            console.print(f"✅ [green]Output saved to:[/green] {output}")
    else:
        console.print(formatted_output)


def process_batch(
    files: list[Path],
    output_format: str,
    api_key: str,
    output_dir: Optional[str],
    jobs: int,
    quiet: bool,
) -> None:
    """Process multiple files, saving each to a separate output file (optionally in parallel)."""
    results_table = Table(title="Batch Processing Results")
    results_table.add_column("File", style="cyan")
    results_table.add_column("Status", style="green")
    results_table.add_column("Output", style="blue")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        disable=quiet,
    ) as progress:
        task = progress.add_task("Processing batch...", total=len(files))

        from concurrent.futures import ThreadPoolExecutor, as_completed

        def _work(file_path: Path) -> tuple[Path, Path]:
            output_ext = {"text": ".txt", "json": ".json", "markdown": ".md"}.get(
                output_format, ".txt"
            )

            out_dir = Path(output_dir) if output_dir else file_path.parent
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / file_path.with_suffix(output_ext).name

            text = pdf_to_text(str(file_path), api_key=api_key)
            formatted_output = format_output(text, output_format)
            out_path.write_text(formatted_output, encoding="utf-8")
            return file_path, out_path

        with ThreadPoolExecutor(max_workers=jobs) as executor:
            future_map = {executor.submit(_work, p): p for p in files}
            for future in as_completed(future_map):
                file_path = future_map[future]
                try:
                    _, out_path = future.result()
                    results_table.add_row(file_path.name, "✅ Success", str(out_path))
                except Exception as e:
                    results_table.add_row(
                        file_path.name, f"❌ Failed: {str(e)[:80]}", "N/A"
                    )
                finally:
                    progress.advance(task)

    if not quiet:
        console.print("\n")
        console.print(results_table)


@cli.command()
def config() -> None:
    """Show current configuration and setup instructions."""
    config_panel = Panel.fit(
        f"""[bold]Current Configuration[/bold]

[cyan]API Key Status:[/cyan] {"✅ Configured" if os.getenv("MISTRAL_API_KEY") else "❌ Not configured"}
[cyan]Environment File:[/cyan] {".env found" if Path(".env").exists() else "No .env file"}

[bold]Setup Instructions:[/bold]

1. Get your API key from: [link]https://console.mistral.ai/[/link]
2. Set environment variable: [cyan]export MISTRAL_API_KEY=your_key[/cyan]
3. Or create .env file with: [cyan]MISTRAL_API_KEY=your_key[/cyan]

[bold]Example Usage:[/bold]

• Extract text: [cyan]ocr extract document.pdf[/cyan]
• Save to file: [cyan]ocr extract document.pdf -o output.txt[/cyan]
• Batch process: [cyan]ocr extract *.pdf --batch[/cyan]
• JSON output: [cyan]ocr extract document.pdf --format json[/cyan]
""",
        title="OCR CLI Configuration",
        border_style="blue",
    )
    console.print(config_panel)


@cli.command()
@click.argument("key", required=False)
def set_key(key: Optional[str] = None) -> None:
    """Set your Mistral API key in the .env file."""
    import re
    from pathlib import Path

    env_path = Path(".env")

    # Prompt if not provided
    if not key:
        from getpass import getpass

        key = getpass("Enter your Mistral API key: ")
        if not key:
            console.print("[red]No key provided. Aborting.[/red]")
            return

    # Read existing .env if present
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    # Remove any existing MISTRAL_API_KEY lines
    lines = [line for line in lines if not re.match(r"^MISTRAL_API_KEY\s*=.*", line)]
    # Add the new key
    lines.append(f"MISTRAL_API_KEY={key}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    console.print(
        Panel.fit(
            "[green]Mistral API key set successfully in .env[/green]", title="Success"
        )
    )


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        console.print(f"[red]Fatal error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

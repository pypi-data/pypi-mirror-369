from importlib.metadata import version as _pkg_version

__all__ = ["__version__"]


def _detect_version() -> str:
    # Try current distribution name first, then legacy
    for dist_name in ("upspawn-ocr-cli", "mistral-ocr-cli"):
        try:
            return _pkg_version(dist_name)
        except Exception:
            continue
    # Fallback during editable installs without metadata
    return "0.0.0"


__version__ = _detect_version()

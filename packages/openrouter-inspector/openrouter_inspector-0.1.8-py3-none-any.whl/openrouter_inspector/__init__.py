"""OpenRouter Inspector - A command-line tool for exploring OpenRouter AI models and providers."""

__author__ = "OpenRouter Inspector Team"
__email__ = "support@example.com"

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version

try:
    __version__ = pkg_version("openrouter-inspector")
except PackageNotFoundError:  # pragma: no cover - dev/editable fallback
    __version__ = "0.0.0"

# Re-export the click group as package-level entry point
from .cli import cli

__all__ = ["cli", "__version__"]

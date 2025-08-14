"""Corpus data loader function utilities."""

from pathlib import Path


def get_corpus_path() -> Path:
    """Returns the path to the Spanish corpus data file.

    Returns:
        Path: An absolute path to the Spanish corpus data file.

    """
    package_dir = Path(__file__).parent
    corpus_path = Path.joinpath(package_dir, "data", "spanish.txt")

    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus file has not been found at {corpus_path}")

    return corpus_path

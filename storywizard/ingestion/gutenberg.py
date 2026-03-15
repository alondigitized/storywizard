"""Project Gutenberg book fetcher."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import httpx

from storywizard.config import PipelineConfig
from storywizard.models import StoryMetadata

logger = logging.getLogger(__name__)

# Curated list of great candidates for graphic novel adaptation
CANDIDATES = {
    43: StoryMetadata(
        title="The Strange Case of Dr. Jekyll and Mr. Hyde",
        author="Robert Louis Stevenson",
        gutenberg_id=43,
        genre="Gothic horror",
        setting="London",
        time_period="Victorian era",
    ),
    11: StoryMetadata(
        title="Alice's Adventures in Wonderland",
        author="Lewis Carroll",
        gutenberg_id=11,
        genre="Fantasy",
        setting="Wonderland",
        time_period="Victorian era",
    ),
    46: StoryMetadata(
        title="A Christmas Carol",
        author="Charles Dickens",
        gutenberg_id=46,
        genre="Ghost story",
        setting="London",
        time_period="Victorian era",
    ),
    174: StoryMetadata(
        title="The Picture of Dorian Gray",
        author="Oscar Wilde",
        gutenberg_id=174,
        genre="Gothic fiction",
        setting="London",
        time_period="Victorian era",
    ),
    84: StoryMetadata(
        title="Frankenstein",
        author="Mary Shelley",
        gutenberg_id=84,
        genre="Gothic science fiction",
        setting="Europe",
        time_period="18th century",
    ),
    77416: StoryMetadata(
        title="Romance of the Three Kingdoms",
        author="Luo Guanzhong (trans. C.H. Brewitt-Taylor)",
        gutenberg_id=77416,
        genre="Mythic martial arts adventure",
        setting="Ancient China — Han Dynasty collapse",
        time_period="Late 2nd century CE",
    ),
}


def fetch_book(
    book_id: int, config: PipelineConfig | None = None
) -> tuple[StoryMetadata, str]:
    """Fetch a book's text from Project Gutenberg.

    Returns the metadata and full plain text of the book.
    Caches the downloaded text in the stories directory.
    """
    stories_dir = Path(config.stories_dir if config else "stories")
    stories_dir.mkdir(parents=True, exist_ok=True)

    cache_path = stories_dir / f"gutenberg_{book_id}.txt"

    # Use cached version if available
    if cache_path.exists():
        logger.info("Using cached text for book %d", book_id)
        text = cache_path.read_text(encoding="utf-8")
    else:
        url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
        logger.info("Fetching book %d from %s", book_id, url)
        response = httpx.get(url, follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        text = response.text
        cache_path.write_text(text, encoding="utf-8")
        logger.info("Cached book %d (%d chars)", book_id, len(text))

    # Strip Gutenberg header/footer boilerplate
    text = _strip_gutenberg_boilerplate(text)

    # Use curated metadata if available, otherwise create basic metadata
    if book_id in CANDIDATES:
        metadata = CANDIDATES[book_id]
    else:
        metadata = StoryMetadata(
            title=f"Gutenberg Book #{book_id}",
            author="Unknown",
            gutenberg_id=book_id,
        )
    metadata.source_url = f"https://www.gutenberg.org/ebooks/{book_id}"

    return metadata, text


def _strip_gutenberg_boilerplate(text: str) -> str:
    """Remove Project Gutenberg header and footer from the text."""
    # Find start marker
    start_markers = [
        "*** START OF THE PROJECT GUTENBERG EBOOK",
        "*** START OF THIS PROJECT GUTENBERG EBOOK",
        "***START OF THE PROJECT GUTENBERG EBOOK",
    ]
    for marker in start_markers:
        idx = text.upper().find(marker.upper())
        if idx != -1:
            # Skip past the marker line
            newline = text.find("\n", idx)
            if newline != -1:
                text = text[newline + 1 :]
            break

    # Find end marker
    end_markers = [
        "*** END OF THE PROJECT GUTENBERG EBOOK",
        "*** END OF THIS PROJECT GUTENBERG EBOOK",
        "***END OF THE PROJECT GUTENBERG EBOOK",
        "End of the Project Gutenberg EBook",
        "End of Project Gutenberg",
    ]
    for marker in end_markers:
        idx = text.upper().find(marker.upper())
        if idx != -1:
            text = text[:idx]
            break

    return text.strip()

#!/usr/bin/env python3
"""Run the Storywizard publishing pipeline on a candidate story."""

import logging
import sys

from storywizard.config import PipelineConfig
from storywizard.ingestion.gutenberg import fetch_book
from storywizard.pipeline import PublishingPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("storywizard")


def main() -> None:
    book_id = int(sys.argv[1]) if len(sys.argv) > 1 else 43  # Default: Jekyll & Hyde

    config = PipelineConfig()
    if not config.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY environment variable is required")
        sys.exit(1)

    logger.info("Fetching book %d from Project Gutenberg...", book_id)
    metadata, text = fetch_book(book_id, config)
    logger.info("Loaded '%s' by %s (%d chars)", metadata.title, metadata.author, len(text))

    pipeline = PublishingPipeline(config)
    novel = pipeline.run(text, metadata)

    logger.info("=" * 60)
    logger.info("COMPLETE!")
    logger.info("Title: %s", novel.metadata.title)
    logger.info("Scenes: %d", len(novel.panel_scripts))
    logger.info("Panels: %d", len(novel.generated_panels))
    if novel.editorial_review:
        logger.info(
            "Editorial score: %d/10 (%s)",
            novel.editorial_review.overall_score,
            "approved" if novel.editorial_review.approved else "not approved",
        )
    logger.info("Output: %s/", config.output_dir)


if __name__ == "__main__":
    main()

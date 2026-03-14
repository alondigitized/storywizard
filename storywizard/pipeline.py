"""Pipeline orchestrator — runs the full publishing pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

from storywizard.agents.story_analyst import StoryAnalyst
from storywizard.agents.production_designer import ProductionDesigner
from storywizard.agents.script_writer import ScriptWriter
from storywizard.agents.artist import Artist
from storywizard.agents.critical_editor import CriticalEditor
from storywizard.agents.focus_group import FocusGroup
from storywizard.config import PipelineConfig
from storywizard.models import GraphicNovel, StoryMetadata
from storywizard.output.renderer import render_graphic_novel

logger = logging.getLogger(__name__)


class PublishingPipeline:
    """Orchestrates the full AI publishing pipeline.

    Runs each agent in sequence, passing outputs forward. The Critical Editor
    can reject and trigger revisions up to max_revision_rounds times.
    """

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self.story_analyst = StoryAnalyst(self.config)
        self.production_designer = ProductionDesigner(self.config)
        self.script_writer = ScriptWriter(self.config)
        self.artist = Artist(self.config)
        self.critical_editor = CriticalEditor(self.config)
        self.focus_group = FocusGroup(self.config)

    def run(self, source_text: str, metadata: StoryMetadata) -> GraphicNovel:
        """Execute the full publishing pipeline."""
        slug = metadata.title.lower().replace(" ", "-")[:40]
        output_dir = Path(self.config.output_dir) / slug

        # Stage 1: Story Analysis
        logger.info("=" * 60)
        logger.info("STAGE 1: Story Analyst analyzing '%s'", metadata.title)
        logger.info("=" * 60)
        analysis = self.story_analyst.analyze(source_text, metadata)
        logger.info(
            "Found %d characters, %d scenes, %d themes",
            len(analysis.characters),
            len(analysis.scenes),
            len(analysis.themes),
        )

        # Stage 2: Production Design
        logger.info("=" * 60)
        logger.info("STAGE 2: Production Designer creating style guide")
        logger.info("=" * 60)
        style_guide = self.production_designer.design(analysis)
        logger.info("Style guide created: %s", style_guide.art_style)

        # Stage 3: Script Writing
        logger.info("=" * 60)
        logger.info("STAGE 3: Script Writer creating panel scripts")
        logger.info("=" * 60)
        scripts = self.script_writer.write_all_scripts(
            analysis.scenes, analysis.characters, style_guide
        )
        total_panels = sum(len(s.panels) for s in scripts)
        logger.info("Created %d scripts with %d total panels", len(scripts), total_panels)

        # Stage 4: Art Generation
        logger.info("=" * 60)
        logger.info("STAGE 4: Artist generating panels (%s backend)", self.config.image_backend)
        logger.info("=" * 60)
        panels = self.artist.generate_panels(scripts, style_guide, output_dir / "panels")
        logger.info("Generated %d panel images", len(panels))

        # Stage 5: Editorial Review (with revision loop)
        logger.info("=" * 60)
        logger.info("STAGE 5: Critical Editor reviewing draft")
        logger.info("=" * 60)
        editorial_review = None
        for attempt in range(1, self.config.max_revision_rounds + 1):
            editorial_review = self.critical_editor.review(
                metadata, style_guide, scripts, panels
            )
            logger.info(
                "Editorial review (attempt %d): score=%d, approved=%s",
                attempt,
                editorial_review.overall_score,
                editorial_review.approved,
            )
            if editorial_review.approved:
                break
            if attempt < self.config.max_revision_rounds:
                logger.info("Draft rejected — revision feedback provided")
                # In a full implementation, we'd feed the review back to
                # the relevant agents for revision. For now, we log and retry.
                logger.info("Issues: %s", editorial_review.issues)
        else:
            logger.warning(
                "Draft not approved after %d rounds — proceeding with final version",
                self.config.max_revision_rounds,
            )

        # Stage 6: Focus Group
        logger.info("=" * 60)
        logger.info("STAGE 6: Focus Group evaluating from persona perspectives")
        logger.info("=" * 60)
        focus_feedback = self.focus_group.evaluate(
            metadata, style_guide, scripts, editorial_review
        )
        logger.info("Received feedback from %d personas", len(focus_feedback))

        # Assemble final graphic novel
        graphic_novel = GraphicNovel(
            metadata=metadata,
            style_guide=style_guide,
            panel_scripts=scripts,
            generated_panels=panels,
            editorial_review=editorial_review,
            focus_group_feedback=focus_feedback,
        )

        # Render output
        logger.info("=" * 60)
        logger.info("RENDERING: Assembling final graphic novel")
        logger.info("=" * 60)
        render_graphic_novel(graphic_novel, output_dir)
        logger.info("Graphic novel saved to %s", output_dir)

        return graphic_novel

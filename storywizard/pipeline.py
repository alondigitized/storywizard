"""Pipeline orchestrator — runs the full publishing pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

from storywizard.agents.story_analyst import StoryAnalyst
from storywizard.agents.curator import Curator
from storywizard.agents.production_designer import ProductionDesigner
from storywizard.agents.script_writer import ScriptWriter
from storywizard.agents.artist import Artist
from storywizard.agents.critical_editor import CriticalEditor
from storywizard.agents.focus_group import FocusGroup
from storywizard.agents.web_publisher import AccessibilityReviewer, WebPublisher
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
        self.curator = Curator(self.config)
        self.production_designer = ProductionDesigner(self.config)
        self.script_writer = ScriptWriter(self.config)
        self.artist = Artist(self.config)
        self.critical_editor = CriticalEditor(self.config)
        self.focus_group = FocusGroup(self.config)
        self.web_publisher = WebPublisher(self.config)
        self.accessibility_reviewer = AccessibilityReviewer(self.config)

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

        # Stage 2: The Curator — why this book matters
        logger.info("=" * 60)
        logger.info("STAGE 2: The Curator articulating why this book matters")
        logger.info("=" * 60)
        curator_statement = self.curator.curate(analysis)
        logger.info("Curator: \"%s\"", curator_statement.one_line)

        # Stage 3: Production Design
        logger.info("=" * 60)
        logger.info("STAGE 3: Production Designer creating style guide")
        logger.info("=" * 60)
        style_guide = self.production_designer.design(analysis)
        logger.info("Style guide created: %s", style_guide.art_style)

        # Stage 4: Script Writing
        logger.info("=" * 60)
        logger.info("STAGE 4: Script Writer creating panel scripts")
        logger.info("=" * 60)
        scripts = self.script_writer.write_all_scripts(
            analysis.scenes, analysis.characters, style_guide
        )
        total_panels = sum(len(s.panels) for s in scripts)
        logger.info("Created %d scripts with %d total panels", len(scripts), total_panels)

        # Stage 5: Art Generation
        logger.info("=" * 60)
        logger.info("STAGE 5: Artist generating panels (%s backend)", self.config.image_backend)
        logger.info("=" * 60)
        panels = self.artist.generate_panels(scripts, style_guide, output_dir / "panels")
        logger.info("Generated %d panel images", len(panels))

        # Stage 6: Editorial Review (with revision loop)
        logger.info("=" * 60)
        logger.info("STAGE 6: Critical Editor reviewing draft")
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
                logger.info("Draft rejected — revising scripts based on feedback")
                logger.info("Issues: %s", editorial_review.issues)

                # Feed editor feedback to Script Writer for revision
                feedback_context = (
                    f"EDITOR FEEDBACK (score {editorial_review.overall_score}/10):\n"
                    f"Issues: {'; '.join(editorial_review.issues)}\n"
                    f"Suggestions: {'; '.join(editorial_review.suggestions)}\n"
                    f"Visual consistency: {editorial_review.visual_consistency}\n"
                    f"Narrative coherence: {editorial_review.narrative_coherence}\n"
                    f"Dialogue quality: {editorial_review.dialogue_quality}\n"
                    f"Pacing: {editorial_review.pacing}"
                )
                scripts = self.script_writer.revise_scripts(
                    scripts, analysis.characters, style_guide, feedback_context
                )
                total_panels = sum(len(s.panels) for s in scripts)
                logger.info(
                    "Revised %d scripts with %d total panels",
                    len(scripts), total_panels,
                )

                # Re-generate panels from revised scripts
                panels = self.artist.generate_panels(
                    scripts, style_guide, output_dir / "panels"
                )
                logger.info("Re-generated %d panel images", len(panels))
        else:
            logger.warning(
                "Draft not approved after %d rounds — proceeding with final version",
                self.config.max_revision_rounds,
            )

        # Stage 7: Focus Group
        logger.info("=" * 60)
        logger.info("STAGE 7: Focus Group evaluating from persona perspectives")
        logger.info("=" * 60)
        focus_feedback = self.focus_group.evaluate(
            metadata, style_guide, scripts, editorial_review
        )
        logger.info("Received feedback from %d personas", len(focus_feedback))

        # Assemble final graphic novel
        graphic_novel = GraphicNovel(
            metadata=metadata,
            curator_statement=curator_statement,
            style_guide=style_guide,
            panel_scripts=scripts,
            generated_panels=panels,
            editorial_review=editorial_review,
            focus_group_feedback=focus_feedback,
        )

        # Render markdown output
        logger.info("=" * 60)
        logger.info("RENDERING: Assembling final graphic novel")
        logger.info("=" * 60)
        render_graphic_novel(graphic_novel, output_dir)

        # Stage 8: Web Publishing
        logger.info("=" * 60)
        logger.info("STAGE 8: Web Publisher preparing for web delivery")
        logger.info("=" * 60)
        self.web_publisher.prepare_for_web(graphic_novel, output_dir)
        logger.info("Web-optimized data saved")

        # Stage 9: Accessibility Review
        logger.info("=" * 60)
        logger.info("STAGE 9: Accessibility Reviewer checking web version")
        logger.info("=" * 60)
        a11y_review = self.accessibility_reviewer.review_accessibility(graphic_novel)
        logger.info(
            "Accessibility score: %s/10", a11y_review.get("overall_score", "N/A")
        )

        # Save accessibility review
        import json
        a11y_path = output_dir / "accessibility_review.json"
        a11y_path.write_text(json.dumps(a11y_review, indent=2), encoding="utf-8")

        logger.info("Graphic novel published to %s", output_dir)
        return graphic_novel

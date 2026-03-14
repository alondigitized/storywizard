"""Output renderer — assembles the final graphic novel as markdown and JSON."""

from __future__ import annotations

from pathlib import Path

from storywizard.models import GraphicNovel


def render_graphic_novel(novel: GraphicNovel, output_dir: Path) -> Path:
    """Render the graphic novel as markdown documents and JSON for the web app.

    Creates:
    - novel.json — full structured data for the web reader
    - graphic_novel.md — the main reading document
    - style_guide.md — the production design style guide
    - editorial_review.md — the editor's review
    - focus_group.md — focus group feedback
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON for web app
    json_path = output_dir / "novel.json"
    json_path.write_text(novel.model_dump_json(indent=2), encoding="utf-8")

    # Main graphic novel
    main_path = output_dir / "graphic_novel.md"
    main_path.write_text(_render_main(novel), encoding="utf-8")

    # Style guide
    style_path = output_dir / "style_guide.md"
    style_path.write_text(_render_style_guide(novel), encoding="utf-8")

    # Editorial review
    if novel.editorial_review:
        review_path = output_dir / "editorial_review.md"
        review_path.write_text(_render_editorial(novel), encoding="utf-8")

    # Focus group
    if novel.focus_group_feedback:
        focus_path = output_dir / "focus_group.md"
        focus_path.write_text(_render_focus_group(novel), encoding="utf-8")

    return main_path


def _render_main(novel: GraphicNovel) -> str:
    """Render the main graphic novel document."""
    lines = [
        f"# {novel.metadata.title}",
        f"### A Graphic Novel Adaptation",
        f"**Original by {novel.metadata.author}**",
        "",
        f"*Art style: {novel.style_guide.art_style}*",
        "",
        "---",
        "",
    ]

    # Build panel lookup
    panel_lookup: dict[tuple[int, int], str] = {}
    for p in novel.generated_panels:
        panel_lookup[(p.scene_number, p.panel_number)] = p.image_path

    for script in novel.panel_scripts:
        lines.append(f"## Scene {script.scene_number}: {script.scene_title}")
        lines.append("")
        if script.layout_notes:
            lines.append(f"*{script.layout_notes}*")
            lines.append("")

        for panel in script.panels:
            lines.append(f"### Panel {panel.panel_number}")
            lines.append("")

            # Image reference
            key = (script.scene_number, panel.panel_number)
            if key in panel_lookup:
                img_path = panel_lookup[key]
                lines.append(f"![{panel.visual_direction[:80]}]({img_path})")
                lines.append("")

            # Narration
            if panel.narration:
                lines.append(f"> *{panel.narration}*")
                lines.append("")

            # Dialogue
            for line in panel.dialogue:
                lines.append(f"**\"{line}\"**")
                lines.append("")

            # Sound effects
            if panel.sound_effects:
                lines.append(
                    "***" + "  ".join(panel.sound_effects) + "***"
                )
                lines.append("")

        lines.append("---")
        lines.append("")

    lines.append("")
    lines.append(
        f"*Produced by Storywizard AI Publishing Pipeline — "
        f"preserving stories for all readers.*"
    )
    return "\n".join(lines)


def _render_style_guide(novel: GraphicNovel) -> str:
    """Render the style guide document."""
    sg = novel.style_guide
    lines = [
        f"# Visual Style Guide: {novel.metadata.title}",
        "",
        f"## Art Style",
        sg.art_style,
        "",
        f"## Color Palette",
    ]
    for color in sg.color_palette:
        lines.append(f"- {color}")
    lines.extend([
        "",
        f"## Mood",
        sg.mood,
        "",
        f"## Character Designs",
    ])
    for cd in sg.character_designs:
        lines.append(f"### {cd.character_name}")
        lines.append(f"**Appearance:** {cd.appearance}")
        if cd.clothing:
            lines.append(f"**Clothing:** {cd.clothing}")
        if cd.distinguishing_features:
            lines.append(
                f"**Distinguishing features:** {', '.join(cd.distinguishing_features)}"
            )
        lines.append("")

    lines.extend([
        f"## Environment Notes",
        sg.environment_notes,
        "",
        f"## Typography",
        sg.typography_notes,
        "",
        f"## Consistency Rules",
    ])
    for rule in sg.consistency_rules:
        lines.append(f"- {rule}")

    if sg.full_style_document:
        lines.extend(["", "---", "", sg.full_style_document])

    return "\n".join(lines)


def _render_editorial(novel: GraphicNovel) -> str:
    """Render the editorial review document."""
    r = novel.editorial_review
    lines = [
        f"# Editorial Review: {novel.metadata.title}",
        "",
        f"**Score: {r.overall_score}/10** — {'APPROVED' if r.approved else 'NEEDS REVISION'}",
        "",
        f"## Summary",
        r.summary,
        "",
        f"## Visual Consistency",
        r.visual_consistency,
        "",
        f"## Narrative Coherence",
        r.narrative_coherence,
        "",
        f"## Dialogue Quality",
        r.dialogue_quality,
        "",
        f"## Pacing",
        r.pacing,
        "",
    ]
    if r.issues:
        lines.append("## Issues")
        for issue in r.issues:
            lines.append(f"- {issue}")
        lines.append("")
    if r.suggestions:
        lines.append("## Suggestions")
        for s in r.suggestions:
            lines.append(f"- {s}")
    return "\n".join(lines)


def _render_focus_group(novel: GraphicNovel) -> str:
    """Render the focus group feedback document."""
    lines = [
        f"# Focus Group Feedback: {novel.metadata.title}",
        "",
    ]
    for fb in novel.focus_group_feedback:
        lines.extend([
            f"## {fb.persona_name}",
            f"*{fb.persona_description}*" if fb.persona_description else "",
            "",
            f"- **Accessibility:** {fb.accessibility_score}/10",
            f"- **Engagement:** {fb.engagement_score}/10",
            f"- **Would read:** {'Yes' if fb.would_read else 'No'}",
            "",
        ])
        if fb.strengths:
            lines.append("**Strengths:**")
            for s in fb.strengths:
                lines.append(f"- {s}")
            lines.append("")
        if fb.concerns:
            lines.append("**Concerns:**")
            for c in fb.concerns:
                lines.append(f"- {c}")
            lines.append("")
        if fb.suggestions:
            lines.append("**Suggestions:**")
            for s in fb.suggestions:
                lines.append(f"- {s}")
            lines.append("")
        if fb.summary:
            lines.extend([fb.summary, ""])
        lines.append("---")
        lines.append("")
    return "\n".join(lines)

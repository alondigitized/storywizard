#!/usr/bin/env python3
"""Create demo graphic novel data for testing the web interface."""

import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def create_jekyll_hyde_demo():
    """Create a demo Jekyll & Hyde graphic novel with sample data."""
    slug = "the-strange-case-of-dr.-jekyll-and-m"
    novel_dir = OUTPUT_DIR / slug
    novel_dir.mkdir(parents=True, exist_ok=True)
    (novel_dir / "panels").mkdir(exist_ok=True)

    novel_data = {
        "metadata": {
            "title": "The Strange Case of Dr. Jekyll and Mr. Hyde",
            "author": "Robert Louis Stevenson",
            "source_url": "https://www.gutenberg.org/ebooks/43",
            "gutenberg_id": 43,
            "genre": "Gothic Horror",
            "setting": "London",
            "time_period": "Victorian Era",
        },
        "curator_statement": {
            "human_truth": "Every person contains multitudes \u2014 impulses we act on and impulses we suppress. Stevenson gave form to the terrifying idea that the darkness inside us isn\u2019t a flaw to be fixed, but a fundamental part of who we are. Jekyll doesn\u2019t become Hyde; he already IS Hyde. The potion just removes the mask.",
            "historical_moment": "Written in 1886, during the height of Victorian respectability, when gentlemen were expected to be moral pillars in public while London\u2019s underworld thrived in shadow. Stevenson wrote the entire novella in three feverish days, burned the first draft, and rewrote it in three more. It became an instant sensation \u2014 selling 40,000 copies in six months \u2014 because it said out loud what everyone secretly knew: the respectable facade was a lie.",
            "living_relevance": "In an age of curated social media personas, where everyone projects a polished self while hiding their darker impulses, Jekyll and Hyde is more relevant than ever. We all maintain a public face and a private one. The story asks: what happens when the gap between who we pretend to be and who we actually are becomes unbridgeable?",
            "invitation": "This isn\u2019t a long read \u2014 it\u2019s a short, sharp shock. In just five scenes, you\u2019ll follow the mystery of a sinister door, a trampled child, and a will that leaves everything to a man no one has ever seen. By the time you reach the final revelation, you\u2019ll understand why this story invented a phrase that\u2019s been part of our language for nearly 140 years. Everyone has a Hyde. Come meet yours.",
            "one_line": "The story that gave us the language to talk about the darkness hiding inside every respectable person.",
            "target_audience": "Young adults and adult readers",
        },
        "style_guide": {
            "art_style": "Dark Victorian noir with ink wash textures — heavy shadows, gaslit atmosphere, influenced by Mike Mignola and Dave McKean",
            "color_palette": [
                "Deep charcoal (#2C2C2C) — the fog-shrouded streets",
                "Sickly amber (#D4A847) — gaslight and moral corruption",
                "Blood crimson (#8B0000) — violence and Hyde's presence",
                "Cold blue-grey (#6B7B8D) — Jekyll's repression and clinical detachment",
                "Ivory white (#F5F0E1) — innocence and the facade of respectability",
            ],
            "mood": "Oppressive, claustrophobic Victorian dread — the constant sense that something monstrous lurks beneath the veneer of respectability. Shadows are alive, fog obscures truth, and every gentleman's face hides a beast.",
            "character_designs": [
                {
                    "character_name": "Dr. Henry Jekyll",
                    "appearance": "Tall, handsome man of 50 with refined features, greying temples, kind but haunted eyes. Carries himself with impeccable posture that slowly deteriorates.",
                    "clothing": "Immaculate dark frock coat, high collar, silk cravat. His clothing becomes increasingly disheveled as the story progresses.",
                    "distinguishing_features": ["Haunted eyes with dark circles", "Trembling hands he tries to hide", "A warmth in his smile that doesn't reach his eyes"],
                    "color_associations": ["Cool blue-grey", "White that yellows"],
                },
                {
                    "character_name": "Mr. Edward Hyde",
                    "appearance": "Small, pale, dwarfish figure that radiates wrongness. Features are not deformed but give an impression of deformity — something fundamentally off about his proportions.",
                    "clothing": "Jekyll's clothes hanging loose on his smaller frame. Rumpled, stained. Wears a heavy cape to hide in shadows.",
                    "distinguishing_features": ["Unsettling smile", "Movements that are too quick, almost insectile", "A shadow that seems larger than his body"],
                    "color_associations": ["Blood crimson", "Deep charcoal"],
                },
                {
                    "character_name": "Mr. Gabriel Utterson",
                    "appearance": "Lean, long, dusty, dreary lawyer. Rugged face weathered by years of keeping others' secrets. Loyal eyes.",
                    "clothing": "Conservative dark suit, always proper. A man who blends into the background by design.",
                    "distinguishing_features": ["Deep-set watchful eyes", "Firm jaw suggesting quiet determination"],
                    "color_associations": ["Muted browns", "Reliable grey"],
                },
            ],
            "environment_notes": "Victorian London rendered in heavy shadow and fog. Streets are narrow, gaslit corridors. Jekyll's house is grand but with one wing perpetually dark. Hyde's Soho apartment is cramped, stained. The laboratory door is always in shadow — a threshold between worlds.",
            "typography_notes": "Dialogue in clean serif (Caslon-style). Narration in slightly weathered italic. Hyde's speech in a more jagged, unsettling variant. Sound effects hand-lettered with ink splatter.",
            "consistency_rules": [
                "Hyde is ALWAYS drawn smaller than everyone around him",
                "Gaslight casts amber; moonlight casts blue-grey",
                "Jekyll's hands are prominent in every scene — trembling, clenching, transforming",
                "Shadows grow longer and more distorted as the story progresses",
                "The laboratory door appears in the background of at least one panel per scene",
                "Weather worsens with narrative tension — mist to fog to storm",
            ],
            "full_style_document": "",
        },
        "panel_scripts": [
            {
                "scene_number": 1,
                "scene_title": "The Story of the Door",
                "layout_notes": "Wide establishing shot followed by tight conversation panels. The door should dominate the final panel.",
                "panels": [
                    {
                        "panel_number": 1,
                        "visual_direction": "Wide shot: A foggy London street at dusk. Mr. Utterson and Mr. Enfield walk side by side, silhouettes against amber gaslight. Victorian buildings loom on either side, their upper floors lost in mist.",
                        "dialogue": [],
                        "narration": "Mr. Utterson the lawyer was a man of rugged countenance, that was never lighted by a smile. And yet somehow, he was lovable.",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 2,
                        "visual_direction": "Medium shot of Enfield gesturing toward a sinister door set into a windowless wall. The door is blistered, stained — utterly out of place on the respectable street. Deep shadows pool around its threshold.",
                        "dialogue": ["Did you ever remark that door?", "It is connected in my mind with a very odd story."],
                        "narration": "",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 3,
                        "visual_direction": "Flashback panel — tilted angle, more expressionistic. A small, pale figure (Hyde) tramples over a screaming child at a street corner. The scene is rendered in harsh crimson and black. Hyde's face is obscured by shadow but his posture radiates malice.",
                        "dialogue": [],
                        "narration": "It was some damned Juggernaut — the man trampled calmly over the child's body and left her screaming on the ground.",
                        "sound_effects": ["CRACK"],
                    },
                    {
                        "panel_number": 4,
                        "visual_direction": "Close-up of the sinister door, now filling the entire panel. The wood grain seems to form a face. A keyhole glints like an eye. Utterson's reflection is barely visible in the dark wood.",
                        "dialogue": ["And the man who did this — he had a key to that door."],
                        "narration": "",
                        "sound_effects": [],
                    },
                ],
            },
            {
                "scene_number": 2,
                "scene_title": "Search for Mr. Hyde",
                "layout_notes": "Claustrophobic panels that grow tighter as Utterson hunts through the night. The final panel opens wide for the confrontation.",
                "panels": [
                    {
                        "panel_number": 1,
                        "visual_direction": "Utterson alone in his study at night, holding Jekyll's will by candlelight. The document glows amber. His face is deeply troubled, carved by shadows. Behind him, bookshelves recede into darkness.",
                        "dialogue": [],
                        "narration": "That evening, Mr. Utterson came home to his bachelor house in sombre spirits and sat down to dinner without relish.",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 2,
                        "visual_direction": "Montage panel: Three small frames showing Utterson haunting the street near the door at different times — dawn, noon, night. Each time the street is emptier, the shadows deeper. He is a dark sentinel, watching.",
                        "dialogue": [],
                        "narration": "If he be Mr. Hyde, I shall be Mr. Seek.",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 3,
                        "visual_direction": "The confrontation: Hyde emerges from the door, face half-lit by a distant gaslight. He is small but radiates menace. Utterson blocks his path. The size difference is stark — Hyde looks up at the tall lawyer, but somehow Utterson seems the more vulnerable.",
                        "dialogue": ["Mr. Hyde, I think?", "That is my name. What do you want?"],
                        "narration": "",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 4,
                        "visual_direction": "Extreme close-up of Hyde's face — the only time we see it clearly. Not deformed, but deeply wrong. His smile is too wide, his eyes too bright, something reptilian in his gaze. The amber gaslight makes his skin look sickly.",
                        "dialogue": ["Will you let me see your face?"],
                        "narration": "Mr. Hyde was pale and dwarfish; he gave an impression of deformity without any nameable malformation.",
                        "sound_effects": [],
                    },
                ],
            },
            {
                "scene_number": 3,
                "scene_title": "The Carew Murder Case",
                "layout_notes": "This is the violent centerpiece. Panels shatter and overlap as the murder unfolds. Strict panel borders dissolve into chaos.",
                "panels": [
                    {
                        "panel_number": 1,
                        "visual_direction": "A peaceful moonlit scene: Sir Danvers Carew, a beautiful old gentleman with white hair, walks along the Thames embankment. The moon is full, London is serene. This peace is about to be destroyed.",
                        "dialogue": [],
                        "narration": "It was a fine night — the moon lay on her back, and the lanes were brilliantly lit.",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 2,
                        "visual_direction": "Hyde appears from shadow, cane in hand. His shadow falls over Carew. The panel is split diagonally — the peaceful moonlit half versus the encroaching crimson darkness of Hyde's arrival.",
                        "dialogue": [],
                        "narration": "",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 3,
                        "visual_direction": "VIOLENCE — rendered almost abstractly. The cane rises and falls. Splashes of crimson against the blue moonlight. Panel borders crack and splinter. Hyde's face is pure savage joy. This should be horrifying but artfully composed — the violence of a Caravaggio painting.",
                        "dialogue": [],
                        "narration": "With ape-like fury, he was trampling his victim under foot and hailing down a storm of blows.",
                        "sound_effects": ["CRACK", "CRACK", "CRACK"],
                    },
                    {
                        "panel_number": 4,
                        "visual_direction": "Aftermath: The broken cane lies in two pieces. A pool of moonlight — or is it something else? — spreads across the cobblestones. Hyde is gone. Only the fog remains.",
                        "dialogue": [],
                        "narration": "The stick with which the deed had been done was of some rare and very tough wood — it had broken in the middle under the stress of this insensate cruelty.",
                        "sound_effects": [],
                    },
                ],
            },
            {
                "scene_number": 4,
                "scene_title": "The Last Night",
                "layout_notes": "Build from quiet dread to the explosive revelation. The door becomes a character. Final panels should be the largest in the entire novel.",
                "panels": [
                    {
                        "panel_number": 1,
                        "visual_direction": "Jekyll's butler Poole stands at Utterson's door, terror in his eyes. Behind him, the street is a wall of fog. His hands twist his hat. The warm light from Utterson's hallway contrasts with the cold night.",
                        "dialogue": ["Mr. Utterson, sir — something is wrong.", "There has been foul play."],
                        "narration": "",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 2,
                        "visual_direction": "Utterson and Poole approach Jekyll's laboratory door. Servants huddle in the hallway behind them, holding candles that create a procession of wavering light. The door at the end of the corridor is the darkest point in the image — a void.",
                        "dialogue": ["Jekyll! I demand to see you!"],
                        "narration": "",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 3,
                        "visual_direction": "A voice from behind the door — rendered as a jagged speech bubble, the lettering unstable, wavering between Jekyll's refined hand and something more primal.",
                        "dialogue": ["For God's sake, have mercy!"],
                        "narration": "Utterson heard a voice from within: a voice that was not Jekyll's — and yet somehow was.",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 4,
                        "visual_direction": "FULL PAGE: The door crashes open. Inside, Hyde's body lies crumpled on the floor, still twitching. A vial rolls from his hand. But the horror is in the details — Jekyll's clothes on Hyde's small frame. The chemicals still smoking. The full-length mirror reflecting something we cannot see. Utterson and Poole stand frozen in the doorway, backlit.",
                        "dialogue": [],
                        "narration": "Right in the midst there lay the body of a man sorely contorted and still twitching. They drew near on tiptoe, turned it on its back, and beheld the face of Edward Hyde.",
                        "sound_effects": [],
                    },
                ],
            },
            {
                "scene_number": 5,
                "scene_title": "Henry Jekyll's Full Statement",
                "layout_notes": "The transformation sequence. Panels dissolve and morph. Jekyll's handwriting narrates. This is the emotional climax — horror and tragedy intertwined.",
                "panels": [
                    {
                        "panel_number": 1,
                        "visual_direction": "Jekyll alone in his laboratory, hand reaching for a bubbling green potion. The room is cluttered with scientific apparatus. His face shows equal parts terror and fascination. The potion glows, casting his face in an eerie green light.",
                        "dialogue": [],
                        "narration": "I hesitated long before I put this theory to the test of practice. I knew well that I risked death.",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 2,
                        "visual_direction": "THE TRANSFORMATION — a four-part sequence within one panel. Jekyll drinks. His body convulses. His features shift and compress. Hyde emerges. Each stage overlaps the last like a multiple exposure photograph. Pain and ecstasy are indistinguishable on his changing face.",
                        "dialogue": [],
                        "narration": "The most racking pangs succeeded: a grinding in the bones, deadly nausea, and a horror of the spirit that cannot be exceeded at the hour of birth or death.",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 3,
                        "visual_direction": "Hyde stands before a full-length mirror, seeing himself for the first time. His reflection fills the panel — small, young, wicked, grinning. Behind the mirror, the ghostly outline of Jekyll watches, trapped.",
                        "dialogue": [],
                        "narration": "I felt younger, lighter, happier in body. I knew myself, at the first breath of this new life, to be more wicked, tenfold more wicked — and the thought delighted me like wine.",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 4,
                        "visual_direction": "Final panel — split vertically. Left half: Jekyll writing his confession by candlelight, tears on his cheeks, hand trembling. Right half: Hyde's shadow looming behind him, growing, consuming. The two halves are separated by a crack that runs through the middle — the self, divided and irreparable.",
                        "dialogue": [],
                        "narration": "I bring the life of that unhappy Henry Jekyll to an end.",
                        "sound_effects": [],
                    },
                ],
            },
        ],
        "generated_panels": [],
        "editorial_review": {
            "overall_score": 8,
            "approved": True,
            "visual_consistency": "Strong noir aesthetic maintained throughout. The gaslight-to-moonlight color shifting is effective. Hyde's consistent small stature creates excellent visual dissonance.",
            "narrative_coherence": "The five selected scenes create a compelling arc from mystery to revelation. The Carew murder scene effectively marks the turn from suspense to horror.",
            "dialogue_quality": "Dialogue is well-adapted from the source — concise and powerful. The mix of original Stevenson prose in narration with adapted dialogue works well.",
            "pacing": "Excellent build from slow-burn suspense to explosive revelation. The transformation sequence is the emotional peak, properly positioned.",
            "issues": [
                "Scene 3 panel 3 could be more specific about composition to ensure the violence reads as artistic rather than gratuitous",
                "Consider adding a quiet epilogue panel after the full statement — Utterson alone with the letter",
            ],
            "suggestions": [
                "The color palette could incorporate more green for the transformation scenes to contrast with the amber/crimson palette",
                "Consider a recurring visual motif of hands — Jekyll's refined hands becoming Hyde's brutal ones",
            ],
            "summary": "A strong, atmospheric adaptation that captures the psychological horror of Stevenson's novella. The visual style guide creates a cohesive world, and the scene selection balances suspense, violence, and tragedy effectively. Approved with minor suggestions for enhancement.",
        },
        "focus_group_feedback": [
            {
                "persona_name": "Reluctant Teen Reader",
                "persona_description": "15-year-old who finds traditional books boring. Loves anime and video games.",
                "accessibility_score": 8,
                "engagement_score": 9,
                "strengths": [
                    "The murder scene is intense and visually dynamic — very manga-influenced with the breaking panel borders",
                    "Hyde is genuinely creepy without being over-the-top",
                    "The transformation sequence is the kind of thing I'd screenshot and share",
                ],
                "concerns": [
                    "Some of the Victorian language in narration might slow me down",
                    "Would love to see more of Hyde causing chaos before the murder",
                ],
                "suggestions": [
                    "Modernize some narration phrasing while keeping dialogue period-accurate",
                    "Add more visual action — Hyde in motion, not just described",
                ],
                "would_read": True,
                "summary": "This is way better than I expected from a 'classic.' The dark art style sells it. I'd actually read this.",
            },
            {
                "persona_name": "Visual Learner Adult",
                "persona_description": "35-year-old professional who reads graphic novels regularly. Values artistic quality.",
                "accessibility_score": 9,
                "engagement_score": 8,
                "strengths": [
                    "The Mike Mignola / Dave McKean influence is inspired — perfect for this material",
                    "Color palette is sophisticated and narratively meaningful",
                    "Panel compositions show real cinematic thinking",
                ],
                "concerns": [
                    "Only 5 scenes might feel too compressed for someone who knows the source material",
                    "The editorial voice in the narration boxes needs to be carefully balanced — too much tells, too little loses the literary quality",
                ],
                "suggestions": [
                    "Consider a brief text prologue giving context for readers unfamiliar with Victorian London",
                    "The style guide's consistency rules are excellent — ensure they're followed rigorously in final art",
                ],
                "would_read": True,
                "summary": "A respectful, artistically ambitious adaptation. The visual design elevates the source material rather than simplifying it.",
            },
            {
                "persona_name": "ESL Student",
                "persona_description": "22-year-old learning English. Visual context helps comprehension.",
                "accessibility_score": 7,
                "engagement_score": 8,
                "strengths": [
                    "The visual storytelling is strong enough to follow even without reading every word",
                    "Character expressions and body language convey emotion clearly",
                    "The transformation sequence is universally understandable — no language needed",
                ],
                "concerns": [
                    "Some Victorian vocabulary will be challenging (Juggernaut, frock coat, cravat)",
                    "The narration-heavy panels may be overwhelming",
                ],
                "suggestions": [
                    "Consider a glossary for archaic terms",
                    "Ensure dialogue is in simpler English while narration preserves the literary voice",
                    "More visual context clues for period-specific elements",
                ],
                "would_read": True,
                "summary": "The story comes through visually even when the words are difficult. Good adaptation for language learners.",
            },
        ],
        # Web metadata
        "description": "Step into the fog-shrouded streets of Victorian London in this haunting graphic novel adaptation. Dr. Henry Jekyll's desperate experiments unleash the monstrous Mr. Hyde, blurring the line between civilization and savagery.",
        "tags": ["Gothic Horror", "Victorian", "Psychological Thriller", "Classic Literature", "Dark", "Transformation", "Duality"],
        "accent_color": "#D4A847",
        "cover_bg": "#1a1a2e",
        "reading_time_minutes": 25,
        "target_audience": "Young adults and graphic novel enthusiasts who enjoy dark, atmospheric storytelling",
        "seo_description": "Read Dr. Jekyll and Mr. Hyde as a stunning AI-generated graphic novel. Dark Victorian noir art brings Stevenson's classic to vivid life.",
    }

    # Generate mock panel prompt files
    for script in novel_data["panel_scripts"]:
        for panel in script["panels"]:
            sn = script["scene_number"]
            pn = panel["panel_number"]
            prompt_path = novel_dir / "panels" / f"scene{sn:02d}_panel{pn:02d}.prompt.txt"
            prompt_path.write_text(
                f"[MOCK IMAGE — would be generated by AI image API]\n\n"
                f"SCENE: {script['scene_title']}\n"
                f"PANEL {pn}\n\n"
                f"IMAGE PROMPT:\n{panel['visual_direction']}\n",
                encoding="utf-8",
            )
            # Also add to generated_panels
            novel_data["generated_panels"].append({
                "scene_number": sn,
                "panel_number": pn,
                "image_prompt": panel["visual_direction"],
                "image_path": f"panels/scene{sn:02d}_panel{pn:02d}.prompt.txt",
                "alt_text": panel["visual_direction"][:120],
            })

    # Save novel.json
    json_path = novel_dir / "novel.json"
    json_path.write_text(json.dumps(novel_data, indent=2), encoding="utf-8")
    print(f"Demo novel created at {novel_dir}")
    return novel_dir


def create_frankenstein_demo():
    """Create a second demo novel for the bookshelf."""
    slug = "frankenstein"
    novel_dir = OUTPUT_DIR / slug
    novel_dir.mkdir(parents=True, exist_ok=True)
    (novel_dir / "panels").mkdir(exist_ok=True)

    novel_data = {
        "metadata": {
            "title": "Frankenstein",
            "author": "Mary Shelley",
            "source_url": "https://www.gutenberg.org/ebooks/84",
            "gutenberg_id": 84,
            "genre": "Gothic Science Fiction",
            "setting": "Europe",
            "time_period": "18th Century",
        },
        "curator_statement": {
            "human_truth": "What do you owe the life you create? Frankenstein is about the most primal form of abandonment \u2014 a parent who rejects their child because it didn\u2019t turn out as expected. The Creature isn\u2019t born evil; he\u2019s made evil by a world that refuses to see past his appearance. His rage is the rage of anyone who has ever been judged before they could speak.",
            "historical_moment": "Mary Shelley was just eighteen years old when she began writing Frankenstein in 1816, during a stormy summer in Switzerland with Percy Shelley and Lord Byron. They challenged each other to write ghost stories. The two famous poets produced nothing memorable. The teenager produced the first science fiction novel ever written \u2014 a book that invented an entire genre and has never gone out of print in over two hundred years.",
            "living_relevance": "As we build artificial intelligence, gene-edit embryos, and push the boundaries of what we can create, Frankenstein\u2019s central question has never been more urgent: just because we CAN create something, should we? And if we do, what responsibility do we bear for what we\u2019ve made? Victor Frankenstein is the patron saint of every technologist who ships first and asks questions later.",
            "invitation": "Forget the bolts-in-the-neck movie monster \u2014 Shelley\u2019s Creature is eloquent, lonely, and heartbreaking. He teaches himself to read with Paradise Lost. He weeps when a family he secretly loves rejects him. And when he finally confronts his creator on an Alpine glacier, their conversation is one of the most powerful scenes in all of literature. This is the book that started science fiction, written by a teenage girl. Come find out why it still matters.",
            "one_line": "Written by an eighteen-year-old woman in 1818, this is the book that invented science fiction \u2014 and the question it asks about creating life has never been more urgent.",
            "target_audience": "Young adults and adult readers",
        },
        "style_guide": {
            "art_style": "Romantic-era oil painting aesthetic with dramatic chiaroscuro — influenced by Caspar David Friedrich's sublime landscapes and Fuseli's nightmarish figures",
            "color_palette": [
                "Storm grey (#4A4E5A) — the bleak northern skies",
                "Lightning white (#F0F5FF) — the spark of creation and horror",
                "Warm amber (#B8860B) — firelight, humanity, warmth being lost",
                "Ice blue (#A8C8E0) — the Arctic, isolation, pursuit",
                "Decay green (#5A6B3C) — the unnatural, the Creature's world",
            ],
            "mood": "Sublime terror meeting intimate tragedy. Vast landscapes dwarf the characters, emphasizing their insignificance against nature and the horror of playing God.",
            "character_designs": [
                {
                    "character_name": "Victor Frankenstein",
                    "appearance": "Young, initially handsome with bright eyes that become increasingly hollow and feverish. Gaunt, obsessed, deteriorating.",
                    "clothing": "Scholar's attire that degrades from crisp university wear to ragged, travel-worn layers.",
                    "distinguishing_features": ["Feverish, sunken eyes", "Hands stained with chemicals", "A posture that curls inward with guilt"],
                    "color_associations": ["Warm amber fading to storm grey"],
                },
                {
                    "character_name": "The Creature",
                    "appearance": "Eight feet tall, proportioned like a classical sculpture gone wrong. Beautiful component parts assembled into something horrifying. Yellow skin barely covers the muscles beneath. Watery eyes that hold unexpected intelligence and sorrow.",
                    "clothing": "Initially naked, then in scavenged mismatched clothing. Eventually a dark cloak.",
                    "distinguishing_features": ["Enormous stature", "Yellow translucent skin", "Eyes that express more humanity than his creator's"],
                    "color_associations": ["Decay green", "Lightning white"],
                },
            ],
            "environment_notes": "Locations range from cramped university labs to sublime Alpine vistas to the frozen Arctic. Each environment reflects the emotional state — the lab is suffocating, the mountains are liberating but terrifying, the Arctic is the end of all things.",
            "typography_notes": "Victor's narration in elegant serif. The Creature's speech in a raw, powerful hand that becomes more refined as he learns. Walton's frame narrative in a clean, documentary style.",
            "consistency_rules": [
                "The Creature is ALWAYS the tallest figure in any panel",
                "Lightning imagery recurs throughout — in skies, in reflections, in Victor's eyes",
                "Fire and ice as opposing visual motifs",
                "Hands are emphasized in every scene — creating, reaching, recoiling",
            ],
            "full_style_document": "",
        },
        "panel_scripts": [
            {
                "scene_number": 1,
                "scene_title": "It's Alive",
                "layout_notes": "Build from dark cramped lab to the explosive moment of creation. The final panel should be the largest.",
                "panels": [
                    {
                        "panel_number": 1,
                        "visual_direction": "Victor hunched over his workbench in the attic laboratory. Candlelight barely reaches the corners. Anatomical sketches cover the walls. His hands, stained and trembling, reach for the final connection.",
                        "dialogue": [],
                        "narration": "It was on a dreary night of November that I beheld the accomplishment of my toils.",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 2,
                        "visual_direction": "The Creature's eye opens — a single massive panel showing just the eye. Yellow, watery, but undeniably alive. Lightning reflected in the iris.",
                        "dialogue": [],
                        "narration": "I saw the dull yellow eye of the creature open; it breathed hard, and a convulsive motion agitated its limbs.",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 3,
                        "visual_direction": "Victor recoils in horror, knocking over equipment. The Creature sits up on the slab, one enormous hand reaching toward its creator. The scene is half shadow, half lightning flash — beautiful and terrible.",
                        "dialogue": [],
                        "narration": "How can I describe my emotions at this catastrophe? His limbs were in proportion, and I had selected his features as beautiful. Beautiful! Great God!",
                        "sound_effects": [],
                    },
                ],
            },
            {
                "scene_number": 2,
                "scene_title": "The Creature's Tale",
                "layout_notes": "Intimate campfire scene in the mountains. Warm amber lighting against cold blue wilderness.",
                "panels": [
                    {
                        "panel_number": 1,
                        "visual_direction": "A vast Alpine landscape — tiny figures of Victor and the Creature sitting by a fire on a glacial moraine. The scale emphasizes their smallness against creation. Mer de Glace stretches behind them.",
                        "dialogue": ["Listen to me, Frankenstein. You accuse me of murder, yet you would destroy your own creature. Hear my tale."],
                        "narration": "",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 2,
                        "visual_direction": "Close-up of the Creature's face by firelight — his expression is not monstrous but deeply sad. The amber light softens his features. His enormous eyes glisten with tears.",
                        "dialogue": ["I am malicious because I am miserable. Am I not shunned and hated by all mankind?"],
                        "narration": "",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 3,
                        "visual_direction": "Victor listens, face torn between revulsion and guilt. The fire between them creates a barrier — two silhouettes on opposite sides of the flame.",
                        "dialogue": [],
                        "narration": "For the first time, I felt what the duties of a creator towards his creature were.",
                        "sound_effects": [],
                    },
                ],
            },
            {
                "scene_number": 3,
                "scene_title": "The Arctic Pursuit",
                "layout_notes": "Stark white and blue palette. Emptiness as a visual force. The two figures — pursuer and pursued — are specks in infinite white.",
                "panels": [
                    {
                        "panel_number": 1,
                        "visual_direction": "An endless Arctic ice field. Victor, emaciated and wild-eyed, drives a dog sled across the frozen waste. In the far distance, barely visible, a massive dark figure moves across the ice.",
                        "dialogue": [],
                        "narration": "I pursued him across the frozen seas, sustained only by vengeance.",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 2,
                        "visual_direction": "Victor collapses on the ice as Walton's ship appears. He is barely human anymore — a skeleton wrapped in furs, eyes burning with obsession. The ship looms above like salvation or judgment.",
                        "dialogue": ["He is here... you must promise me... you will find him... and destroy him."],
                        "narration": "",
                        "sound_effects": [],
                    },
                    {
                        "panel_number": 3,
                        "visual_direction": "FINAL PANEL: The Creature stands over Victor's deathbed in the ship's cabin. He is weeping — enormous, terrible, and heartbroken. His hand reaches out but doesn't quite touch his creator's face. The most human moment in the story, belonging to the inhuman.",
                        "dialogue": ["Farewell, Frankenstein! Blasted as thou wert, my agony was still superior to thine."],
                        "narration": "He sprung from the cabin window upon the ice raft which lay close to the vessel. He was soon borne away by the waves, and lost in darkness and distance.",
                        "sound_effects": [],
                    },
                ],
            },
        ],
        "generated_panels": [],
        "editorial_review": {
            "overall_score": 9,
            "approved": True,
            "visual_consistency": "The Romantic painting aesthetic is maintained beautifully. The scale contrasts between figures and landscapes create genuine awe.",
            "narrative_coherence": "Three scenes capture the essential arc: creation, confrontation, destruction. Efficient and emotionally powerful.",
            "dialogue_quality": "Faithful to Shelley's prose while adapted for graphic novel pacing. The Creature's dialogue is the emotional core.",
            "pacing": "Excellent — builds from claustrophobic creation to sublime landscapes to desolate conclusion.",
            "issues": [],
            "suggestions": ["Consider adding the wedding night scene for additional horror"],
            "summary": "A visually stunning adaptation that honors Shelley's themes of creation, responsibility, and the nature of humanity. The art direction elevates this beyond mere illustration into genuine visual literature.",
        },
        "focus_group_feedback": [
            {
                "persona_name": "Reluctant Teen Reader",
                "persona_description": "15-year-old who finds traditional books boring.",
                "accessibility_score": 8,
                "engagement_score": 8,
                "strengths": ["The creation scene is epic", "The Creature is sympathetic, not just scary"],
                "concerns": ["Only 3 scenes feels very short"],
                "suggestions": ["Add more action scenes"],
                "would_read": True,
                "summary": "Short but powerful. The Creature's sadness hits hard.",
            },
        ],
        "description": "Witness the birth of the world's most famous monster in this sublime graphic novel adaptation. Victor Frankenstein's ambition creates life — and destroys everything he loves.",
        "tags": ["Gothic Horror", "Science Fiction", "Romantic Era", "Classic Literature", "Tragedy", "Creation"],
        "accent_color": "#B8860B",
        "cover_bg": "#1a2a1a",
        "reading_time_minutes": 15,
    }

    # Generate mock panels
    for script in novel_data["panel_scripts"]:
        for panel in script["panels"]:
            sn = script["scene_number"]
            pn = panel["panel_number"]
            prompt_path = novel_dir / "panels" / f"scene{sn:02d}_panel{pn:02d}.prompt.txt"
            prompt_path.write_text(
                f"[MOCK IMAGE]\n\n{panel['visual_direction']}\n",
                encoding="utf-8",
            )
            novel_data["generated_panels"].append({
                "scene_number": sn,
                "panel_number": pn,
                "image_prompt": panel["visual_direction"],
                "image_path": f"panels/scene{sn:02d}_panel{pn:02d}.prompt.txt",
                "alt_text": panel["visual_direction"][:120],
            })

    json_path = novel_dir / "novel.json"
    json_path.write_text(json.dumps(novel_data, indent=2), encoding="utf-8")
    print(f"Demo novel created at {novel_dir}")
    return novel_dir


if __name__ == "__main__":
    create_jekyll_hyde_demo()
    create_frankenstein_demo()
    print("Demo data created! Run the web server with: python -m web.serve")

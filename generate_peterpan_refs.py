#!/usr/bin/env python3
"""Generate character reference and set design images for Peter Pan.

Modern animated style — bold clean lines, vivid colors, dynamic action.
Disney/Pixar concept art meets graphic novel. Kid-friendly for age 9+.

Usage:
    python3 generate_peterpan_refs.py
"""

import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("peterpan_refs")

OUTPUT_DIR = Path("output/peter-pan/character_refs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_PREFIX = (
    "Modern animated illustration in the style of Disney/Pixar concept art "
    "meets graphic novel. Bold clean lines, vivid saturated colors, dynamic "
    "action poses, expressive character animation. Warm and whimsical with "
    "a sense of wonder and adventure. Kid-friendly, bright, and magical. "
    "Painterly digital art with visible brushwork and rich textures. "
)

CHARACTERS = [
    # ── Peter Pan ──
    {
        "name": "peter_pan",
        "images": [
            {
                "suffix": "front",
                "seed": 7200,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Peter Pan: eternally young boy of about 12, "
                    "wild auburn hair, bright mischievous green eyes full of confidence and "
                    "daring. Pointed ears. Impish grin that says he knows something you don't. "
                    "Wearing a green tunic made of leaves and vines, a jaunty feathered cap, "
                    "brown belt with a small dagger. Golden fairy dust particles swirl around "
                    "him. Warm golden light. Vivid greens, warm golds, sky blue background "
                    "with wispy clouds. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 7201,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Peter Pan: wild auburn-haired boy, "
                    "bright green eyes, pointed ears, impish grin. Wearing green leaf tunic "
                    "and feathered cap. Hovering slightly off the ground — feet not touching — "
                    "with arms crossed confidently. Golden fairy dust trailing from his feet. "
                    "Turned slightly, looking over his shoulder with a daring expression that "
                    "invites you to follow. Neverland jungle and lagoon visible in background. "
                    "Vivid greens, tropical blues, warm golden light. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 7202,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body portrait of Peter Pan flying: wild auburn hair streaming, "
                    "bright green eyes, pointed ears, joyful laugh. Wearing green leaf tunic, "
                    "feathered cap, brown belt with dagger. Arms spread wide, legs bent behind "
                    "him, soaring through a starlit night sky. Golden fairy dust trail behind. "
                    "Full figure head to toe against a deep midnight blue sky full of stars. "
                    "The second star to the right glows brightest. Vivid greens, midnight blue, "
                    "warm gold fairy dust. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 7203,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic action scene of Peter Pan sword-fighting Captain Hook on the "
                    "deck of the Jolly Roger. Peter is airborne, hovering above Hook, small "
                    "dagger flashing, wild auburn hair flying, green eyes blazing with "
                    "fearless excitement, laughing in mid-combat. His green tunic catches "
                    "the warm lantern light of the ship. Golden fairy dust sparks where his "
                    "blade meets Hook's sword. Dynamic diagonal composition full of movement "
                    "and energy. No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Wendy Darling ──
    {
        "name": "wendy",
        "images": [
            {
                "suffix": "front",
                "seed": 7210,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Wendy Darling: kind, practical girl of about 12 "
                    "with long brown hair tied with a blue ribbon, warm brown eyes full of "
                    "imagination and gentle determination. Wearing a pale blue nightgown with "
                    "white lace trim — the night she flew to Neverland. Expression of wonder "
                    "mixed with quiet bravery. Soft warm bedroom light. Blue, white, warm "
                    "gold tones. Stars visible through a window behind her. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 7211,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter portrait of Wendy Darling: brown hair with blue ribbon, "
                    "warm brown eyes, pale blue nightgown. Sitting up in bed telling a story "
                    "to the Lost Boys gathered around her — hands animated in the telling, "
                    "face lit with the joy of storytelling. Underground home setting with "
                    "warm lantern light, cozy earthy textures. Blue, amber warmth, forest "
                    "greens. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 7212,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body portrait of Wendy Darling flying: brown hair streaming behind "
                    "her with blue ribbon, pale blue nightgown billowing, arms outstretched "
                    "in wonder, brown eyes wide with amazement and delight. Flying through "
                    "a starlit London sky with rooftops and chimneys below. Golden fairy dust "
                    "trail. Full figure head to toe. Midnight blue sky, warm London lights "
                    "below, gold and blue palette. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 7213,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Wendy Darling standing protectively in front of the "
                    "Lost Boys, facing Captain Hook's pirates with fierce determination. "
                    "Brown hair with blue ribbon, blue nightgown now worn from adventure, "
                    "holding a wooden sword. Her expression is brave and maternal — she's "
                    "both the storyteller and the protector. Behind her: frightened but "
                    "trusting Lost Boys. Warm amber versus cool pirate-ship shadows. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Captain Hook ──
    {
        "name": "captain_hook",
        "images": [
            {
                "suffix": "front",
                "seed": 7220,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Captain Hook: flamboyant pirate villain with "
                    "long curly black hair, sharp handsome face twisted by bitterness and "
                    "vanity, thin curled moustache, piercing dark eyes. Wearing an elaborate "
                    "crimson velvet coat with gold braid and brass buttons, plumed wide-brimmed "
                    "hat with an enormous feather, ruffled white shirt. His right hand is "
                    "replaced by a gleaming iron hook. Expression of theatrical menace — "
                    "more vain than truly evil. Rich crimsons, deep purples, gold details. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 7221,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter portrait of Captain Hook: long curly black hair, thin "
                    "moustache, crimson velvet coat, plumed hat, iron hook hand. Standing at "
                    "the helm of the Jolly Roger, hook hand resting on the ship's wheel, "
                    "turned slightly with a scheming expression. Behind him: dark sails, "
                    "skull-and-crossbones flag, moonlit ocean. Rich crimson, deep ocean blue, "
                    "gold lantern light. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 7222,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body portrait of Captain Hook: tall, thin, dramatically posed. "
                    "Long curly black hair, thin moustache, crimson velvet coat with gold "
                    "braid, plumed hat, ruffled shirt, black boots with silver buckles, "
                    "iron hook gleaming on right hand, ornate sword at hip. Standing on the "
                    "deck of the Jolly Roger, full figure head to toe. He's theatrical and "
                    "vain — even his posture is a performance. Crimson, gold, ocean blue. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 7223,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Captain Hook recoiling in terror from the ticking "
                    "crocodile: crimson coat flying, plumed hat askew, dark eyes wide with "
                    "pure panic, hook hand raised defensively. The enormous green crocodile "
                    "emerges from the water below the ship, jaws open, a clock visible "
                    "glowing inside its belly — tick tick tick. Hook's vanity crumbles into "
                    "genuine fear. Comedic and scary simultaneously. Green, crimson, dark "
                    "ocean blue. No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Tinker Bell ──
    {
        "name": "tinker_bell",
        "images": [
            {
                "suffix": "front",
                "seed": 7230,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Tinker Bell: tiny fairy about 6 inches tall, "
                    "radiating golden light. Blonde hair in a messy bun, large expressive "
                    "blue eyes, delicate translucent wings like a dragonfly catching light "
                    "in iridescent patterns. Wearing a short green leaf dress. Expression of "
                    "fierce loyalty mixed with jealous possessiveness — she's tiny but her "
                    "emotions are enormous. Surrounded by swirling golden pixie dust that "
                    "sparkles like stars. Warm golds, emerald greens, magical shimmer. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 7231,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter portrait of Tinker Bell: tiny glowing fairy, blonde bun, "
                    "big blue eyes, translucent iridescent wings, green leaf dress. Perched "
                    "on Peter Pan's shoulder, arms crossed, expression pouty and jealous — "
                    "she doesn't like sharing Peter's attention. Golden pixie dust emanates "
                    "from her like a miniature sun. Close-up showing her tiny scale against "
                    "Peter's shoulder. Warm gold glow, emerald green, magical atmosphere. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 7232,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body portrait of Tinker Bell in flight: tiny fairy leaving a trail "
                    "of golden pixie dust, blonde bun, big blue eyes bright with determination, "
                    "translucent wings a blur of iridescent motion, green leaf dress. Flying "
                    "fast through a magical forest, trailing golden sparkles like a comet. "
                    "Full tiny figure head to toe, surrounded by oversized flowers and leaves "
                    "that show her scale. Vivid greens, warm golds, magical forest light. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 7233,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Tinker Bell sacrificing herself: drinking the poisoned "
                    "medicine meant for Peter Pan, her golden light flickering and dimming. "
                    "Tiny fairy lying in Peter's cupped hands, wings drooping, glow fading "
                    "from brilliant gold to pale. Peter's face visible above, anguished. "
                    "The scene is lit only by her dying light. Fading gold against darkness, "
                    "emotional and poignant. Beautiful even in sadness. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Tiger Lily ──
    {
        "name": "tiger_lily",
        "images": [
            {
                "suffix": "front",
                "seed": 7240,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Tiger Lily: proud brave Neverland princess, "
                    "about 12 years old. Long straight black hair with feathers and beads "
                    "woven in, dark fierce eyes, strong determined jaw, warm brown skin. "
                    "Wearing a decorated buckskin dress with intricate beadwork in turquoise "
                    "and coral, feathered headdress. Expression of dignified courage — she "
                    "fears nothing. Warm earth tones, turquoise, coral, forest green background "
                    "with Neverland jungle. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 7241,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter portrait of Tiger Lily: long black hair with feathers, "
                    "dark fierce eyes, warm brown skin, buckskin dress with beadwork. "
                    "Standing at the edge of the Neverland lagoon, one hand shading her eyes "
                    "as she scans the horizon, the other on a decorated bow. Expression of "
                    "watchful confidence. Tropical lagoon with palm trees and crystal water "
                    "behind her. Earth tones, turquoise water, tropical greens. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 7242,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body portrait of Tiger Lily: proud Neverland princess standing "
                    "tall, long black hair with feathers and beads, dark eyes, warm brown "
                    "skin. Wearing decorated buckskin dress, moccasins, feathered headdress, "
                    "bow and quiver on her back. Full figure head to toe, standing on a rocky "
                    "outcrop above the Neverland forest. She commands the landscape. Warm "
                    "earth tones, turquoise sky, forest greens. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 7243,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Tiger Lily captured by pirates but refusing to speak: "
                    "tied to a rock at Marooners' Rock as the tide rises, water reaching her "
                    "ankles. Long black hair wet, dark eyes blazing with defiance, jaw set. "
                    "She will not betray Peter Pan's hiding place. Moonlit lagoon, rising "
                    "dark water, her feathers and beadwork catching moonlight. Courage "
                    "personified. Cool moonlit blues, warm skin tones, dramatic contrast. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
]

ENVIRONMENTS = [
    {
        "name": "set_darling_nursery",
        "seed": 7300,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "The Darling nursery in London: a warm cozy bedroom with three small beds, "
            "a large open window revealing a starlit London night sky with rooftops and "
            "chimneys. The second star to the right glows brightest in the sky. Warm "
            "lamplight illuminates toys, a rocking horse, storybooks scattered about. "
            "A dog kennel in the corner (Nana the nursemaid dog). Patterned wallpaper, "
            "soft curtains billowing in the night breeze. Golden warmth meeting cool "
            "starlit blue at the window. No figures. No text, no words, no lettering."
        ),
    },
    {
        "name": "set_neverland",
        "seed": 7301,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "Neverland from above: a magical tropical island seen from a flying perspective. "
            "Dense jungle in vivid greens, a crystal-blue mermaid lagoon, sandy beaches, "
            "a rocky pirate cove with the Jolly Roger anchored, a Native encampment with "
            "colorful tents, the Lost Boys' forest with hidden underground entrances. "
            "Mountains with waterfalls, a rainbow, exotic birds in flight. Everything is "
            "more vivid and saturated than the real world — colors turned up to magical "
            "levels. Bright tropical palette. No figures. No text, no words, no lettering."
        ),
    },
    {
        "name": "set_jolly_roger",
        "seed": 7302,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "The Jolly Roger pirate ship at night: a dark magnificent galleon with black "
            "sails, skull-and-crossbones flags flying, warm amber lanterns swinging on deck. "
            "Ornate carved stern with Hook's quarters, cannons bristling from gun ports, "
            "rope rigging climbing to the crow's nest. Anchored in the moonlit cove of "
            "Neverland. Dark ocean blue, warm amber lanterns, crimson accents on the hull, "
            "silver moonlight. Atmospheric and slightly sinister but also exciting. "
            "No figures. No text, no words, no lettering."
        ),
    },
    {
        "name": "set_underground_home",
        "seed": 7303,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "The Underground Home of the Lost Boys: a cozy magical hideout beneath the "
            "roots of an enormous tree. Hollowed-out earth walls with exposed tree roots "
            "forming natural shelves and alcoves. Warm lanterns and candles. Hammocks "
            "strung between roots, mushroom stools, a fireplace carved from stone, animal "
            "fur rugs, wooden swords and slingshots hung on root-hooks. Small entrance "
            "tunnels visible. Warm amber light, earthy browns, forest greens, cozy and "
            "inviting. A perfect child's dream hideout. "
            "No figures. No text, no words, no lettering."
        ),
    },
]


def generate(prompt: str, width: int, height: int, seed: int, output: Path) -> bool:
    cmd = [
        "mflux-generate-z-image-turbo",
        "--prompt", prompt,
        "--width", str(width),
        "--height", str(height),
        "--steps", "9",
        "--seed", str(seed),
        "--output", str(output),
    ]
    logger.info("Generating %s (seed=%d, %dx%d)", output.name, seed, width, height)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        if result.returncode != 0:
            logger.error("Failed: %s", result.stderr[:300])
            return False
        if not output.exists() or output.stat().st_size < 1024:
            logger.error("Output missing or too small: %s", output)
            return False
        logger.info("Saved %s (%d bytes)", output.name, output.stat().st_size)
        return True
    except subprocess.TimeoutExpired:
        logger.error("Timeout generating %s", output.name)
        return False
    except FileNotFoundError:
        logger.error("mflux-generate-z-image-turbo not found. pip install mflux")
        sys.exit(1)


def main() -> None:
    total = sum(len(c["images"]) for c in CHARACTERS) + len(ENVIRONMENTS)
    count = 0
    failed = []

    for char in CHARACTERS:
        for img in char["images"]:
            count += 1
            w, h = [int(x) for x in img["size"].split("x")]
            output = OUTPUT_DIR / f"{char['name']}_{img['suffix']}.png"
            logger.info("=== Image %d/%d: %s ===", count, total, output.name)
            if not generate(img["prompt"], w, h, img["seed"], output):
                failed.append(output.name)

    for env in ENVIRONMENTS:
        count += 1
        w, h = [int(x) for x in env["size"].split("x")]
        output = OUTPUT_DIR / f"{env['name']}.png"
        logger.info("=== Image %d/%d: %s ===", count, total, output.name)
        if not generate(env["prompt"], w, h, env["seed"], output):
            failed.append(output.name)

    logger.info("=" * 60)
    logger.info("COMPLETE: %d/%d succeeded", count - len(failed), total)
    if failed:
        logger.error("Failed: %s", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate character reference and set design images for Peter Pan.

Studio Ghibli-inspired watercolor style. Kid-friendly for age 9+.

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

STYLE = (
    "Studio Ghibli-inspired watercolor illustration in the style of Hayao Miyazaki "
    "and background artist Kazuo Oga. Soft luminous watercolor washes, delicate "
    "hand-drawn linework, rich atmospheric detail. Characters with simple expressive "
    "faces, large emotive eyes, fluid movement. Warm saturated colors, handpainted "
    "feel, nostalgic wonder. "
)

CHARACTERS = [
    {
        "name": "peter_pan",
        "images": [
            {"suffix": "front", "seed": 7200, "size": "768x1024",
             "prompt": f"{STYLE}Front portrait of Peter Pan: a wild boy of about 12 with tousled auburn hair, bright green eyes full of mischief and fearlessness, pointed ears, impish grin. Wearing a tunic of sewn-together autumn leaves in greens and russets, a jaunty red-feathered cap, barefoot. Golden fairy dust motes float around him. Warm dappled forest light. Soft watercolor background of Neverland jungle. No text, no lettering."},
            {"suffix": "three_quarter", "seed": 7201, "size": "768x1024",
             "prompt": f"{STYLE}Three-quarter portrait of Peter Pan hovering slightly off the ground, arms crossed with confident grin. Tousled auburn hair, green eyes, leaf tunic, red-feathered cap, barefoot. Golden fairy dust trailing from his feet. Looking over his shoulder invitingly. Neverland lagoon and jungle in soft watercolor background. Warm golden afternoon light. No text, no lettering."},
            {"suffix": "full_body", "seed": 7202, "size": "768x1024",
             "prompt": f"{STYLE}Full body of Peter Pan in flight against a starlit midnight blue sky. Arms spread wide in joy, tousled auburn hair streaming, green leaf tunic, red-feathered cap, barefoot. Golden fairy dust trail behind him like a comet. The second star to the right glows brightest. Clouds painted in soft Ghibli style below. Deep indigo sky with warm gold accents. No text, no lettering."},
            {"suffix": "dramatic", "seed": 7203, "size": "768x1024",
             "prompt": f"{STYLE}Peter Pan sword-fighting Captain Hook on the Jolly Roger deck. Peter is airborne above Hook, small dagger flashing, auburn hair wild, green eyes blazing with fearless excitement, laughing. Leaf tunic catching warm lantern light. Dynamic diagonal composition full of energy and movement. Ghibli-style action with fluid motion lines. Warm amber ship lanterns against deep ocean blue. No text, no lettering."},
        ],
    },
    {
        "name": "wendy",
        "images": [
            {"suffix": "front", "seed": 7210, "size": "768x1024",
             "prompt": f"{STYLE}Front portrait of Wendy Darling: kind practical girl of 12 with long brown hair tied with a blue ribbon, warm brown eyes full of imagination and gentle determination. Wearing a pale blue nightgown with white lace trim. Expression of wonder mixed with quiet bravery. Soft warm bedroom lamplight. Stars visible through a window behind her. Gentle watercolor warmth. No text, no lettering."},
            {"suffix": "three_quarter", "seed": 7211, "size": "768x1024",
             "prompt": f"{STYLE}Wendy Darling sitting up telling a story, hands animated, face lit with storytelling joy. Brown hair with blue ribbon, warm brown eyes, pale blue nightgown. Surrounded by Lost Boys listening raptly in the underground home. Warm amber lantern light, cozy earthy textures, tree roots and mushroom stools. Ghibli interior warmth. No text, no lettering."},
            {"suffix": "full_body", "seed": 7212, "size": "768x1024",
             "prompt": f"{STYLE}Full body of Wendy Darling flying through a starlit London sky. Brown hair streaming with blue ribbon, pale blue nightgown billowing, arms outstretched in amazement. Golden fairy dust trail. Victorian London rooftops and chimneys below in soft watercolor. Midnight blue sky with warm city lights below. The joy of first flight. No text, no lettering."},
            {"suffix": "dramatic", "seed": 7213, "size": "768x1024",
             "prompt": f"{STYLE}Wendy standing protectively before the Lost Boys, facing pirates with fierce determination. Brown hair, blue nightgown worn from adventure, holding a wooden sword. Brave and maternal. Behind her: frightened but trusting Lost Boys. Warm amber versus cool pirate shadows. Ghibli-style emotional courage. No text, no lettering."},
        ],
    },
    {
        "name": "captain_hook",
        "images": [
            {"suffix": "front", "seed": 7220, "size": "768x1024",
             "prompt": f"{STYLE}Front portrait of Captain Hook: flamboyant pirate villain with long curly black hair, sharp handsome face twisted by bitterness, thin curled moustache, piercing dark eyes. Elaborate crimson velvet coat with gold braid, plumed hat with enormous feather, ruffled white shirt. Gleaming iron hook replacing right hand. Theatrical menace, more vain than evil. Rich crimsons and deep purples. No text, no lettering."},
            {"suffix": "three_quarter", "seed": 7221, "size": "768x1024",
             "prompt": f"{STYLE}Captain Hook at the helm of the Jolly Roger. Long curly black hair, crimson velvet coat, plumed hat, iron hook on ship's wheel. Scheming expression. Dark sails and skull-and-crossbones flag behind, moonlit ocean. Rich crimson, deep ocean blue, gold lantern light. Ghibli-style atmospheric night scene. No text, no lettering."},
            {"suffix": "full_body", "seed": 7222, "size": "768x1024",
             "prompt": f"{STYLE}Full body of Captain Hook on the Jolly Roger deck. Tall thin dramatic pose. Long black hair, crimson velvet coat with gold braid, plumed hat, ruffled shirt, black boots with silver buckles, iron hook gleaming, ornate sword at hip. Theatrical and vain. Ghibli-style character design with elegant villain proportions. Crimson, gold, ocean blue palette. No text, no lettering."},
            {"suffix": "dramatic", "seed": 7223, "size": "768x1024",
             "prompt": f"{STYLE}Captain Hook recoiling in terror from the ticking crocodile. Crimson coat flying, plumed hat askew, dark eyes wide with pure panic, hook raised defensively. Enormous green crocodile emerging from water below, jaws open, clock glowing inside its belly. Comedic and scary. Ghibli-style expressive fear and humor. Green, crimson, dark ocean blue. No text, no lettering."},
        ],
    },
    {
        "name": "tinker_bell",
        "images": [
            {"suffix": "front", "seed": 7230, "size": "768x1024",
             "prompt": f"{STYLE}Front portrait of Tinker Bell: tiny fairy about 6 inches tall radiating soft golden light. Blonde hair in messy bun, large expressive blue eyes, delicate translucent dragonfly wings catching iridescent light. Short green leaf dress. Fierce loyalty mixed with jealous possessiveness — tiny but enormous emotions. Surrounded by swirling golden pixie dust like fireflies. Warm golds, emerald greens. Ghibli-style magical creature. No text, no lettering."},
            {"suffix": "three_quarter", "seed": 7231, "size": "768x1024",
             "prompt": f"{STYLE}Tinker Bell perched on Peter Pan's shoulder, arms crossed, expression pouty and jealous. Tiny glowing fairy, blonde bun, big blue eyes, translucent wings, green leaf dress. Golden light emanating from her like a miniature sun. Close-up showing her tiny scale. Warm gold glow, Ghibli-style magical atmosphere. No text, no lettering."},
            {"suffix": "full_body", "seed": 7232, "size": "768x1024",
             "prompt": f"{STYLE}Full body of Tinker Bell in flight through a magical forest. Tiny fairy trailing golden pixie dust like a comet. Blonde bun, big blue eyes, translucent wings blurring, green leaf dress. Oversized flowers and leaves show her tiny scale. Vivid Ghibli forest greens, warm golden light filtering through canopy, magical atmosphere. No text, no lettering."},
            {"suffix": "dramatic", "seed": 7233, "size": "768x1024",
             "prompt": f"{STYLE}Tinker Bell's sacrifice: tiny fairy lying in Peter's cupped hands after drinking poisoned medicine. Wings drooping, golden glow fading from brilliant to pale. Peter's anguished face above. Lit only by her dying light. Fading gold against soft darkness. Ghibli-style emotional poignancy, beautiful even in sadness. No text, no lettering."},
        ],
    },
    {
        "name": "tiger_lily",
        "images": [
            {"suffix": "front", "seed": 7240, "size": "768x1024",
             "prompt": f"{STYLE}Front portrait of Tiger Lily: proud brave Neverland princess about 12 years old. Long straight black hair with feathers and beads, dark fierce eyes, strong determined jaw, warm brown skin. Decorated buckskin dress with turquoise and coral beadwork, feathered headdress. Dignified courage. Warm earth tones, turquoise accents, Neverland jungle background. Ghibli-style strong girl character. No text, no lettering."},
            {"suffix": "three_quarter", "seed": 7241, "size": "768x1024",
             "prompt": f"{STYLE}Tiger Lily at the Neverland lagoon edge, hand shading eyes scanning the horizon, other hand on decorated bow. Black hair with feathers, dark fierce eyes, buckskin dress. Watchful confidence. Tropical lagoon with palm trees and crystal water. Earth tones, turquoise water, Ghibli-style tropical landscape. No text, no lettering."},
            {"suffix": "full_body", "seed": 7242, "size": "768x1024",
             "prompt": f"{STYLE}Full body of Tiger Lily standing tall on a rocky outcrop above Neverland forest. Long black hair with feathers and beads, decorated buckskin dress, moccasins, bow and quiver. She commands the landscape. Ghibli-style panoramic background with lush forest, rolling clouds, warm golden light. No text, no lettering."},
            {"suffix": "dramatic", "seed": 7243, "size": "768x1024",
             "prompt": f"{STYLE}Tiger Lily tied to Marooners' Rock as tide rises, refusing to betray Peter Pan. Black hair wet, dark eyes blazing with defiance. Water reaching her ankles, moonlit lagoon, feathers catching moonlight. Courage personified. Cool moonlit blues, warm skin tones. Ghibli-style dramatic moonlight scene. No text, no lettering."},
        ],
    },
]

ENVIRONMENTS = [
    {"name": "set_darling_nursery", "seed": 7300, "size": "1024x768",
     "prompt": f"{STYLE}The Darling nursery in London at night. Three small beds, large open window revealing starlit sky with rooftops and chimneys. The second star to the right glows brightest. Warm lamplight, toys, rocking horse, scattered storybooks. Dog kennel in corner. Patterned wallpaper, curtains billowing in night breeze. Golden warmth meeting cool starlit blue at the window. Ghibli-style cozy interior with meticulous domestic detail. No figures. No text, no lettering."},
    {"name": "set_neverland", "seed": 7301, "size": "1024x768",
     "prompt": f"{STYLE}Neverland from above: magical tropical island seen from flying perspective. Dense jungle in vivid greens, crystal-blue mermaid lagoon, sandy beaches, pirate cove with Jolly Roger anchored, Lost Boys forest. Mountains with waterfalls, rainbow, exotic birds. Everything more vivid and saturated than the real world. Ghibli-style lush panoramic landscape painted with incredible atmospheric depth. No figures. No text, no lettering."},
    {"name": "set_jolly_roger", "seed": 7302, "size": "1024x768",
     "prompt": f"{STYLE}The Jolly Roger pirate ship at night. Dark magnificent galleon with weathered sails, skull flags, warm amber lanterns swinging on deck. Ornate carved stern, cannons, rope rigging to crow's nest. Anchored in moonlit Neverland cove. Dark ocean blue, warm amber lanterns, crimson hull accents, silver moonlight. Ghibli-style atmospheric ship painting with rich detail. No figures. No text, no lettering."},
    {"name": "set_underground_home", "seed": 7303, "size": "1024x768",
     "prompt": f"{STYLE}The Underground Home of the Lost Boys beneath enormous tree roots. Cozy magical hideout with hollowed earth walls, tree roots forming shelves. Warm lanterns and candles, hammocks, mushroom stools, stone fireplace, fur rugs, wooden swords on root-hooks. Small entrance tunnels. Warm amber light, earthy browns, forest greens. Ghibli-style magical interior — a perfect child's dream hideout with handpainted warmth. No figures. No text, no lettering."},
]


def generate(prompt, width, height, seed, output):
    cmd = ["mflux-generate-z-image-turbo", "--prompt", prompt,
           "--width", str(width), "--height", str(height),
           "--steps", "9", "--seed", str(seed), "--output", str(output)]
    logger.info("Generating %s (seed=%d, %dx%d)", output.name, seed, width, height)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        if result.returncode != 0:
            logger.error("Failed: %s", result.stderr[:300])
            return False
        if not output.exists() or output.stat().st_size < 1024:
            logger.error("Output missing or too small")
            return False
        logger.info("Saved %s (%d bytes)", output.name, output.stat().st_size)
        return True
    except subprocess.TimeoutExpired:
        logger.error("Timeout generating %s", output.name)
        return False
    except FileNotFoundError:
        logger.error("mflux not found. pip install mflux")
        sys.exit(1)


def main():
    total = sum(len(c["images"]) for c in CHARACTERS) + len(ENVIRONMENTS)
    count, failed = 0, []
    for char in CHARACTERS:
        for img in char["images"]:
            count += 1
            w, h = [int(x) for x in img["size"].split("x")]
            out = OUTPUT_DIR / f"{char['name']}_{img['suffix']}.png"
            logger.info("=== Image %d/%d: %s ===", count, total, out.name)
            if not generate(img["prompt"], w, h, img["seed"], out):
                failed.append(out.name)
    for env in ENVIRONMENTS:
        count += 1
        w, h = [int(x) for x in env["size"].split("x")]
        out = OUTPUT_DIR / f"{env['name']}.png"
        logger.info("=== Image %d/%d: %s ===", count, total, out.name)
        if not generate(env["prompt"], w, h, env["seed"], out):
            failed.append(out.name)
    logger.info("=" * 60)
    logger.info("COMPLETE: %d/%d succeeded", count - len(failed), total)
    if failed:
        logger.error("Failed: %s", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()

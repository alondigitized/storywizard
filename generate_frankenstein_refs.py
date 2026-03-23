#!/usr/bin/env python3
"""Generate character reference and set design images for Frankenstein.

Generates 20 character images (5 characters × 4 perspectives) and
5 set/environment images using mflux turbo. Runs sequentially to
avoid GPU contention.

Usage:
    python3 generate_frankenstein_refs.py
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
logger = logging.getLogger("frankenstein_refs")

OUTPUT_DIR = Path("output/frankenstein/character_refs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_PREFIX = (
    "Dark Romantic Expressionism illustration, fusion of Gustave Doré engraving "
    "gravitas with Mike Mignola chiaroscuro ink mastery, loose expressionist "
    "watercolor washes, German Expressionist cinema influence. "
    "Anatomical illustration precision with psychological distortion. "
)

# ── Character Reference Images ──────────────────────────────────────

CHARACTERS = [
    # ── Victor Frankenstein ──
    {
        "name": "victor",
        "images": [
            {
                "suffix": "front",
                "seed": 5200,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Victor Frankenstein: classically Romantic beauty, "
                    "high cheekbones, large dark intensely expressive eyes full of guilt and obsession, "
                    "thick dark hair with a single silver streak at the left temple, "
                    "trembling fevered scholar's hands. Wearing high-collared white shirt, "
                    "long dark midnight blue coat, waistcoat, cravat in 1790s gentleman-scholar style. "
                    "Slightly disheveled, feverish pallor. Color palette: midnight Prussian blue (#1B2A4A), "
                    "amber candlelight highlights on one side. Deep shadow background with faint "
                    "laboratory apparatus silhouettes. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 5201,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Victor Frankenstein: high cheekbones, "
                    "large dark expressive eyes haunted by guilt, thick dark hair with silver streak "
                    "at left temple, gaunt scholarly features. Wearing dark midnight blue coat, "
                    "white high-collared shirt, loosened cravat. Turned slightly, gazing at something "
                    "unseen with an expression of tortured fascination. One trembling hand raised "
                    "near his face. Amber candlelight from the left, deep Prussian blue shadows. "
                    "Gothic university study background with heavy wooden shelves. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 5202,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body standing portrait of Victor Frankenstein: tall, thin figure showing "
                    "early deterioration. High cheekbones, dark haunted eyes, silver streak in dark hair. "
                    "Wearing long dark midnight blue coat over waistcoat, white shirt with loosened cravat, "
                    "dark trousers, boots. Standing in his Ingolstadt garret laboratory — tables crowded "
                    "with glass apparatus, chemical flasks, anatomical drawings. Sickly yellow-green "
                    "(#C5C46A) glow from electrical apparatus. Full figure head to toe. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 5203,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Victor Frankenstein in his laboratory at the moment of creation: "
                    "shirtsleeves rolled up, wild dark hair with silver streak, large dark eyes wide "
                    "with horrified revelation, trembling hands outstretched toward an unseen figure. "
                    "Lightning crackles through the garret window casting jagged yellow-green light. "
                    "Laboratory chaos — overturned flasks, scattered papers, electrical apparatus sparking. "
                    "His shadow on the wall behind him is enormous and wrong-shaped. "
                    "Corpse yellow-green (#C5C46A) and midnight Prussian blue (#1B2A4A) dominate. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── The Creature ──
    {
        "name": "creature",
        "images": [
            {
                "suffix": "front",
                "seed": 5210,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Frankenstein's Creature: eight feet tall with massive "
                    "limbs. Skin the yellow of old parchment or bruised cadaver, stretched taut over "
                    "visible musculature. Face has perfect individual features — lustrous straight black "
                    "hair, white teeth, dark lips — but assembled together creates profound wrongness, "
                    "uncanny valley maximum. Watery pale yellow eyes with enlarged irises. Visible "
                    "construction seams at neck and temples as pale raised scars. Expression of "
                    "denied longing and intelligence. Wearing rough scavenged cloak over bare chest. "
                    "Color palette: corpse yellow-green (#C5C46A), storm violet-black (#1A0F1E). "
                    "Dark background. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 5211,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Frankenstein's Creature: enormous figure, "
                    "skin of yellow parchment stretched over visible musculature, watery pale yellow "
                    "eyes with enlarged irises conveying profound sorrow and intelligence, straight "
                    "black hair, dark lips. Visible seams at wrists and temples. Turned slightly, "
                    "looking over shoulder with an expression of grief and longing. Hunched inward "
                    "in characteristic posture of one denied belonging. Wearing patchwork rough-spun "
                    "garments. Forest shadow green (#2D4A2D) background with moonlight filtering "
                    "through trees. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 5212,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body standing portrait of Frankenstein's Creature: eight feet tall, "
                    "towering, massive limbs and torso. Skin of yellow parchment over visible "
                    "musculature, watery yellow eyes, straight black hair, dark lips, visible "
                    "construction seams. Wearing mismatched scavenged clothing — rough cloak, "
                    "too-small waistcoat, ill-fitting trousers. Standing before a doorway he must "
                    "crouch to pass through, emphasizing his enormous scale. Full figure head to toe. "
                    "Storm violet-black (#1A0F1E) and corpse yellow-green tones. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 5213,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Frankenstein's Creature on the Mer de Glace glacier: "
                    "eight feet tall, massive silhouette against vast Alpine ice. Skin of yellow "
                    "parchment, watery yellow eyes blazing, straight black hair whipping in wind, "
                    "enormous hands — one raised in supplication, one clenched in fury. Wearing "
                    "mismatched furs and rough garments. Behind him: shattered glacier ice like "
                    "broken columns, mist as white voids. Color palette: ice white (#EAE6D6), "
                    "midnight Prussian blue (#1B2A4A), corpse yellow-green skin tone. "
                    "Sublime Romantic landscape scale — figure dwarfed by geological immensity. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Robert Walton ──
    {
        "name": "walton",
        "images": [
            {
                "suffix": "front",
                "seed": 5220,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Robert Walton: 28 years old, weather-hardened, "
                    "conventionally handsome face sculpted by Arctic wind. Sandy-reddish hair, "
                    "practical beard, hazel eyes burning with obsessive idealism. Wind-reddened "
                    "complexion. Wearing heavy naval greatcoat in deep navy blue with officer's "
                    "insignia, thick woolen layers beneath. One hand holds a small brass compass. "
                    "Color palette: deep navy blue, ice white (#EAE6D6), amber candlelight warmth "
                    "on face. Arctic grey-white background. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 5221,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Robert Walton: sandy-reddish hair, practical "
                    "beard, hazel eyes, wind-reddened complexion of an Arctic explorer. Wearing deep "
                    "navy blue naval greatcoat. Seated at a desk in his ship's cabin, writing a letter "
                    "by candlelight, one hand turning a small brass compass. Expression of eager "
                    "ambition mixed with dawning concern. Warm amber candlelight from desk lamp, "
                    "cold blue-grey Arctic light from a porthole. Wooden ship interior details. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 5222,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body standing portrait of Robert Walton: weather-hardened 28yo naval captain. "
                    "Sandy-reddish hair, beard, wind-reddened face. Wearing heavy deep navy blue "
                    "greatcoat with officer's insignia, thick woolen layers, heavy boots, calloused "
                    "hands from rope and rigging. Standing on the deck of his ice-locked ship, "
                    "full figure head to toe. Arctic ice field behind him in midnight blue and white. "
                    "Ship's rigging and masts frame the composition. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 5223,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Robert Walton: standing at the bow of his ice-locked ship, "
                    "peering through a spyglass into the Arctic mist. Sandy-reddish hair and beard "
                    "crusted with frost, navy greatcoat billowing. The vast frozen Arctic stretches "
                    "before him — broken ice floes in geometric near-abstraction, horizon uncertain "
                    "where sky meets ice. A distant dark figure is barely visible on the ice. "
                    "Color palette: ice white, midnight Prussian blue (#1B2A4A), cold grey. "
                    "Sublime emptiness. No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Elizabeth Lavenza ──
    {
        "name": "elizabeth",
        "images": [
            {
                "suffix": "front",
                "seed": 5230,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Elizabeth Lavenza: bright golden hair in loose "
                    "late-18th-century arrangement, cloudless blue-grey eyes luminous and clear, "
                    "open gentle features with genuine intelligence. Wearing high-waisted white "
                    "and cream muslin dress with delicate embroidery at collar, blue ribbons. "
                    "Small portrait locket at throat. Expression of warmth with underlying awareness. "
                    "Color palette: amber candlelight (#D4882A) as primary warmth, soft blue-grey "
                    "eyes, ivory white dress. Warm domestic interior background. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 5231,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Elizabeth Lavenza: golden hair catching "
                    "candlelight, blue-grey eyes carrying more expression than words, gentle "
                    "intelligent features. Wearing white muslin dress with blue ribbon at waist, "
                    "portrait locket at throat. Turned slightly, one hand reaching outward in "
                    "characteristic open gesture of connection. Seated in the Frankenstein family "
                    "parlor — warm amber stone walls, Alpine view through large window. "
                    "Amber candlelight warmth dominates. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 5232,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body standing portrait of Elizabeth Lavenza: graceful young woman, "
                    "bright golden hair long and luminous, blue-grey eyes, open features. "
                    "Wearing high-waisted white and cream muslin dress with delicate embroidery, "
                    "blue ribbon sash, light shawl. Portrait locket at throat. Standing in the "
                    "Frankenstein home garden with Alpine lake and mountains behind her. "
                    "Full figure head to toe. Golden afternoon light, warm amber tones. "
                    "Slightly rounded softer linework than other characters. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 5233,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Elizabeth Lavenza on her wedding night: golden hair loose "
                    "and cascading, blue-grey eyes wide with dawning terror, white wedding dress "
                    "that reads simultaneously as bridal gown and burial shroud. Standing alone "
                    "in a candlelit bedchamber, one hand at her throat where the portrait locket "
                    "hangs. A massive shadow falls across the window behind her — the Creature's "
                    "silhouette, enormous and wrong. Amber candlelight fighting against cold "
                    "blue-grey moonlight. Terror and beauty intertwined. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Henry Clerval ──
    {
        "name": "clerval",
        "images": [
            {
                "suffix": "front",
                "seed": 5240,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Henry Clerval: life itself — handsome in a rounded "
                    "open way, warm brown eyes full of animation, easy ready smile. Victor's height "
                    "but carries himself with far greater ease. Wearing merchant-class dress of "
                    "quality — warm brown waistcoat, deep forest green coat, russet cravat. "
                    "Expression of generous warmth and genuine engagement. Color palette: amber "
                    "candlelight (#D4882A) governing warm tones, russet brown and forest green "
                    "(#2D4A2D). Warm background with soft golden light. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 5241,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Henry Clerval: warm brown eyes full of "
                    "animation, easy smile, open rounded handsome features. Wearing forest green "
                    "coat, russet traveling vest. Leaning forward in characteristic orientation-toward "
                    "posture, engaged in conversation. One hand gesturing expressively. Warm amber "
                    "and golden light, a university or tavern interior. He is the visual opposite "
                    "of Victor — all warmth where Victor is all shadow. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 5242,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body standing portrait of Henry Clerval: tall, carries himself with "
                    "natural ease and vitality. Warm brown eyes, easy smile. Wearing russet "
                    "traveling coat over forest green waistcoat, brown trousers, practical boots. "
                    "Standing on a sunlit path, full figure head to toe, body language forward "
                    "and open. Alpine meadow or university quad in background. "
                    "Warm amber and golden tones throughout. Deliberately the warmest, most "
                    "alive-looking character in the visual world. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 5243,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Henry Clerval arriving at Victor's doorstep in Ingolstadt: "
                    "warm brown eyes bright with concern, easy smile faltering as he sees his friend's "
                    "deterioration. Wearing russet traveling coat, bag slung over shoulder. Standing "
                    "in a dark gothic university corridor with amber lamplight behind him — he brings "
                    "literal warmth and light into Victor's dark world. The contrast between Clerval's "
                    "vibrant warm tones and the sickly yellow-green shadows of Ingolstadt is stark. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
]

# ── Set/Environment Design Images ───────────────────────────────────

ENVIRONMENTS = [
    {
        "name": "set_geneva_home",
        "seed": 5300,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "Interior of the Frankenstein family home in Geneva: grand warm stone architecture, "
            "spacious ordered rooms embodying a stable loving world. High ceilings with ornate "
            "molding, large windows revealing Alpine lake and mountain views. Amber candlelight "
            "from multiple sources bathes everything in golden warmth. Rich wooden furniture, "
            "bookshelves, family portraits on walls. Late 18th-century Swiss domestic elegance. "
            "Careful crosshatched architectural detail. Color palette: amber candlelight (#D4882A), "
            "warm stone, soft golden afternoon light. No figures, empty room. "
            "No text, no words, no lettering."
        ),
    },
    {
        "name": "set_ingolstadt_lab",
        "seed": 5301,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "Victor Frankenstein's garret laboratory in Ingolstadt: chaos incarnate. Tables crowded "
            "with scientific apparatus, chemical flasks, anatomical drawings, body parts in shadow. "
            "Sickly yellow-green (#C5C46A) glow of electrical apparatus mixed with insufficient "
            "orange of candles that fail to illuminate. Gothic vaulted stone ceiling, heavy wooden "
            "door. Anatomy charts and Gothic arches create medical horror through ecclesiastical "
            "architecture. Never fully lit — corners always dark, perspective subtly warped. "
            "Expressionistic distortion. No figures, empty room. "
            "No text, no words, no lettering."
        ),
    },
    {
        "name": "set_mer_de_glace",
        "seed": 5302,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "The Mer de Glace glacier in the Swiss Alps: full Romantic sublime landscape in the "
            "vocabulary of Caspar David Friedrich. Vast geological scale with shattered glacier ice "
            "like broken columns, dramatic ink-and-blue-grey wash. Mist as uncrosshatched white voids. "
            "Vertiginous depth, viewer positioned at height looking into infinite space. "
            "Color palette: ice white (#EAE6D6), midnight Prussian blue (#1B2A4A), charnel ash grey. "
            "A tiny human figure visible for scale, dwarfed by immensity. Storm clouds gathering. "
            "No text, no words, no lettering."
        ),
    },
    {
        "name": "set_delacey_cottage",
        "seed": 5303,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "Interior of the De Lacey cottage: a pocket of warmth within a cold forest. Dutch Golden "
            "Age interior vocabulary — warm light on modest beautiful domestic details, textures of "
            "cloth, wood, and firelight. Simple wooden furniture, a fireplace with glowing embers, "
            "worn but clean textiles. Forest shadow green (#2D4A2D) visible through a small window. "
            "Amber candlelight (#D4882A) fills the room with golden warmth. Seen from outside "
            "through a crack in the wall — warm interior framed within dark exterior, belonging "
            "seen from permanent exclusion. No figures. No text, no words, no lettering."
        ),
    },
    {
        "name": "set_arctic_wastes",
        "seed": 5304,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "The Arctic wastes: pure reductive composition of vast whiteness and broken ice floes "
            "in geometric near-abstraction. Horizon uncertain — sky and ice blend in same tone. "
            "Color stripped to minimum: ice white (#EAE6D6), midnight Prussian blue (#1B2A4A), "
            "cold grey. An ice-locked ship visible in the distance, tiny against immensity. "
            "Dog-sled tracks visible in the snow — visual emblem of obsessive pursuit. "
            "Crushing emptiness, sublime desolation. Minimal linework, vast negative space. "
            "No text, no words, no lettering."
        ),
    },
]


def generate(prompt: str, width: int, height: int, seed: int, output: Path) -> bool:
    """Run mflux turbo and return True on success."""
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

    # Character references
    for char in CHARACTERS:
        for img in char["images"]:
            count += 1
            w, h = [int(x) for x in img["size"].split("x")]
            output = OUTPUT_DIR / f"{char['name']}_{img['suffix']}.png"
            logger.info("=== Image %d/%d: %s ===", count, total, output.name)
            if not generate(img["prompt"], w, h, img["seed"], output):
                failed.append(output.name)

    # Environment references
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

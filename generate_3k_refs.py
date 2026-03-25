#!/usr/bin/env python3
"""Generate character reference and set design images for Romance of the Three Kingdoms.

Generates 24 character images (6 characters × 4 perspectives) and
5 set/environment images using mflux turbo. Runs sequentially.

Usage:
    python3 generate_3k_refs.py
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
logger = logging.getLogger("3k_refs")

OUTPUT_DIR = Path("output/romance-of-the-three-kingdoms/character_refs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_PREFIX = (
    "Ink-wash wuxia realism illustration, fusion of traditional Chinese shuimo "
    "water-ink painting and cinematic Western graphic novel draftsmanship. "
    "Characters rendered with meticulous muscular linework in classical Chinese "
    "figure painting tradition, atmospheric loosely-brushed backgrounds echoing "
    "Song Dynasty landscape scrolls. Monumental and mythic register. "
)

CHARACTERS = [
    # ── Liu Pei ──
    {
        "name": "liu_pei",
        "images": [
            {
                "suffix": "front",
                "seed": 6200,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Liu Pei (Liu Yuan-te): tall lean figure with "
                    "inherent quiet aristocratic bearing despite humble circumstances. Divine "
                    "markers rendered with dignified naturalism — ears with lobes hanging to "
                    "shoulder level, wide-set otherworldly eyes. Cool jade-ivory complexion, "
                    "rich red lips, composed almost expressionless face concealing emotional "
                    "depth. Wearing worn practical traveling robes of muted blue-green, fabric "
                    "once-fine but frayed at hems, sandal-merchant who is also somehow imperial. "
                    "Color palette: jade green (#3A7D44), parchment ivory (#F2EBD9), imperial "
                    "gold (#C9963D) as faint trim. Ink-wash atmospheric background. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 6201,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Liu Pei: tall lean man with long earlobes, "
                    "wide-set eyes, jade-ivory complexion, red lips. Expression of quiet "
                    "watchfulness — the eye of the storm. Wearing worn blue-green traveling robes "
                    "with subtle imperial gold threading visible at collar. Turned slightly, "
                    "gazing into middle distance with calm unreadable expression. Peach blossoms "
                    "falling gently in background. Jade green and parchment ivory tones. "
                    "Song Dynasty landscape scroll atmosphere. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 6202,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body standing portrait of Liu Pei: tall lean figure, long earlobes, "
                    "wide-set eyes, jade-ivory complexion. Arms unusually long reaching past "
                    "knees. Wearing worn muted blue-green traveling robes, frayed hems, mended "
                    "patches visible — poverty visible in worn sandal soles. Despite humble "
                    "clothing, bearing is inherently noble. Standing on a dusty road, full "
                    "figure head to toe. Bamboo grove and misty mountains in background. "
                    "Jade green and parchment ivory palette. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 6203,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Liu Pei at the Oath of the Peach Garden: kneeling before "
                    "a ceremonial altar beneath a canopy of peach blossoms in full bloom, hands "
                    "raised in solemn oath. Jade-ivory complexion, long earlobes, wide-set eyes "
                    "now fierce with determination. Wearing his worn blue-green robes but bearing "
                    "transformed — no longer a humble merchant but a man claiming his destiny. "
                    "Imperial gold incense smoke rises around him. Petals drift through golden "
                    "spring light. Jade green, imperial gold (#C9963D), cinnabar red (#C1392B) "
                    "of the oath altar. No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Kuan Yu ──
    {
        "name": "kuan_yu",
        "images": [
            {
                "suffix": "front",
                "seed": 6210,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Kuan Yu (Yun-chang): the most imposing warrior, "
                    "towering figure whose presence commands the frame. Dark brown skin absorbing "
                    "light with solidity and permanence. Magnificent long flowing beard, the single "
                    "most recognizable feature. Phoenix eyes slightly upturned and luminous, "
                    "silkworm eyebrows thick and deeply expressive. Paradox of absolute ferocity "
                    "and absolute dignity — reads as already-god. Wearing battle armor of lacquered "
                    "deep crimson and black. Color palette: deep crimson (#8B1A1A), midnight ink "
                    "(#1A1A2E), bone white (#E8DFD0) edge highlights. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 6211,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Kuan Yu: towering warrior with dark brown "
                    "skin, magnificent long beard flowing, phoenix eyes luminous, silkworm eyebrows "
                    "expressive. Wearing deep crimson and black lacquered armor. The Black Dragon "
                    "glaive rests against his shoulder — massive curved blade midnight-black with "
                    "blood-moon edge, its own weight and personality visible. Turned slightly, "
                    "expression of gravitational stillness and righteous dignity. Warm firelight "
                    "on his dark skin. Deep crimson, midnight ink, bone white palette. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 6212,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body standing portrait of Kuan Yu: towering warrior, consistently the "
                    "tallest figure, dark brown skin, magnificent long beard, phoenix eyes. "
                    "Wearing full crimson and black lacquered battle armor with ceremonial quality "
                    "despite functionality. The Black Dragon glaive held upright — massive heavy "
                    "curved blade casting its own deep shadow. Standing before a military camp, "
                    "crimson banners in background. Full figure head to toe showing imposing "
                    "height and gravitational presence. Deep crimson and midnight ink palette. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 6213,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic battle scene of Kuan Yu: charging on horseback, Black Dragon glaive "
                    "sweeping in a massive arc, dark brown skin glowing with battle-light, "
                    "magnificent beard streaming behind him, phoenix eyes blazing with righteous "
                    "fury. Deep crimson armor catching firelight. The glaive's midnight-black blade "
                    "cuts a diagonal across the composition. Dust and chaos of battle behind him — "
                    "banners, smoke, fallen warriors. He is the eye of war, utterly composed amid "
                    "destruction. Cinnabar red, midnight ink, bone white palette. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Chang Fei ──
    {
        "name": "chang_fei",
        "images": [
            {
                "suffix": "front",
                "seed": 6220,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Chang Fei (I-te): compact dense volcanic figure "
                    "built like a war drum — low center of gravity, enormous presence. Bullet-round "
                    "head almost perfectly spherical, large protruding eyes expressing fury and "
                    "loyalty equally, pointed chin, bristling moustache pointing outward like a "
                    "warning. Simultaneously comic and terrifying. Wearing practical rough-hewn "
                    "military garb in earth umber (#6B3D1E) and deep brown, functional armor "
                    "showing wear and impact. Color palette: earth umber, volcanic orange-red "
                    "highlights, deep brown. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 6221,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Chang Fei: compact explosive warrior, "
                    "bullet-round head, large protruding eyes blazing, bristling moustache, "
                    "pointed chin. Wearing earth-brown armor. Turned with explosive energy, "
                    "one fist clenched, mouth open in his famous roar that can scatter armies. "
                    "His 18-foot spear held diagonally, creating a dynamic line across the "
                    "composition. Perpetually about to explode. Earth umber, deep brown, "
                    "volcanic orange-red highlights. Dust rising around his feet. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 6222,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body standing portrait of Chang Fei: compact stocky warrior, shorter "
                    "than his brothers but wider and denser. Bullet-round head, protruding eyes, "
                    "bristling moustache. Wearing rough earth-brown military armor showing wear. "
                    "His extraordinary 18-foot spear held upright, its extreme length defining "
                    "the composition's vertical axis. Standing in a marketplace — once a butcher "
                    "of pigs, now a butcher of the enemies of righteousness. Full figure head "
                    "to toe. Earth umber and deep brown palette. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 6223,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Chang Fei on the bridge: standing alone on a narrow "
                    "bridge, 18-foot spear planted, bullet-round head thrown back, mouth open "
                    "in his legendary roar that can scatter armies. Large protruding eyes blazing "
                    "with volcanic fury, bristling moustache trembling with the force of his voice. "
                    "Behind him: dust clouds rising from retreating enemy forces. The bridge shakes. "
                    "His compact body radiates explosive compressed energy. Earth umber, volcanic "
                    "orange-red, electric yellow lightning-flash highlights. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Tsao Tsao ──
    {
        "name": "tsao_tsao",
        "images": [
            {
                "suffix": "front",
                "seed": 6230,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Tsao Tsao (Meng-te): the most dangerous man in "
                    "any room. Medium height, small watchful eyes that see everything while "
                    "revealing nothing, long distinguished calculated beard. Visually difficult "
                    "to read — compelling and charismatic with absolute competence. Slight smile "
                    "never reaching eyes, the most dangerous expression. Wearing military "
                    "commander's armor in deep black with signature crimson detailing. "
                    "Color palette: deep black, crimson (#C1392B), cold silver. A crimson "
                    "banner visible at edge of frame. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 6231,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Tsao Tsao: medium height, small watchful "
                    "eyes missing nothing, long calculated beard, slight dangerous smile. Wearing "
                    "deep black armor with crimson details. Seated at a command table studying "
                    "battle maps, one hand resting on his sword, absolutely still where others "
                    "would fidget. Expression of cold strategic brilliance. Crimson banners hang "
                    "in background. Candlelight casts cold silver on his armor. Deep black, "
                    "crimson, cold silver palette. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 6232,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body standing portrait of Tsao Tsao: medium height but commanding — "
                    "others unconsciously orient toward him. Small watchful eyes, long calculated "
                    "beard, absolute stillness and control. Wearing deep black military armor with "
                    "crimson detailing, sword at hip. Standing before his army's crimson banners, "
                    "full figure head to toe. Never the tallest but always the center of gravity. "
                    "Deep black, crimson banners, cold silver edge highlights. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 6233,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Tsao Tsao arriving with his army: mounted on a black "
                    "war-horse, deep black armor gleaming, crimson cape billowing. Small eyes "
                    "surveying the battlefield with cold calculation, slight smile of a man "
                    "who has already won. Behind him: a sea of crimson banners stretching to "
                    "the horizon, an army in perfect formation. The wolf under crimson banners. "
                    "Deep black, crimson (#C1392B), cold silver, smoke ash (#7A7A8A) atmosphere. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Sun Chien ──
    {
        "name": "sun_chien",
        "images": [
            {
                "suffix": "front",
                "seed": 6240,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Sun Chien, Tiger of Wu: lithe powerful figure "
                    "radiant with joy and kinetic energy. Broad open face of someone who never "
                    "learned to dissemble, youthful compared to weathered northern heroes. "
                    "Wearing lighter more mobile armor than northern fighters — Wu-region "
                    "aesthetic designed for river warfare and rapid assault. Bright warm "
                    "bronze-gold metal catching light. Color palette: bronze gold, river blue, "
                    "warm silver. Southern warmth and optimistic energy. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 6241,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Sun Chien: lithe warrior with broad open "
                    "honest face, kinetic energy visible even in stillness. Wearing bronze-gold "
                    "light armor. Turned with acrobatic readiness, hand on sword hilt, expression "
                    "of fierce joy — a warrior who loves righteous battle. River and southern "
                    "landscape in background. Bronze gold catching warm light, river blue "
                    "reflections. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 6242,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body standing portrait of Sun Chien, Tiger of Wu: lithe powerful "
                    "warrior, broad open face, youthful kinetic energy. Wearing light mobile "
                    "bronze-gold armor with minimal bulk allowing acrobatic movement. Standing "
                    "at the base of a city wall, looking upward — about to scale it. Full "
                    "figure head to toe. Bronze gold, river blue, warm silver palette. "
                    "Southern Wu aesthetic. No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 6243,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Sun Chien scaling a fortress wall: acrobatic warrior "
                    "mid-climb, one hand gripping stone, the other swinging a spear seized from "
                    "a defender. Bronze-gold armor flashing, broad face split in a fierce grin "
                    "of pure martial joy. Below: chaos of battle, siege ladders, soldiers. "
                    "Above: terrified defenders looking down at this luminous ascending tiger. "
                    "Bronze gold, cinnabar red of battle, warm silver highlights. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
    # ── Chang Chio ──
    {
        "name": "chang_chio",
        "images": [
            {
                "suffix": "front",
                "seed": 6250,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Front-facing portrait of Chang Chio, leader of the Yellow Turban rebellion: "
                    "elongated almost ascetic figure, a healer who became revolution. Robes of "
                    "saffron yellow-ochre (#D4943A) and deep teal (#1E6B7A) that seem to move in "
                    "winds others cannot feel. Eyes with quality of looking at something vast and "
                    "distant that mortals cannot perceive. Yellow headband of the movement. "
                    "Genuine spiritual authority visible. Supernatural wind effect on robes "
                    "and long beard. Storm teal energy crackling at fingertips. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "three_quarter",
                "seed": 6251,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Three-quarter angle portrait of Chang Chio: elongated ascetic mystic, "
                    "yellow-ochre and teal robes billowing supernaturally. Hands raised in "
                    "invocation, storm teal energy swirling around his fingers. Eyes fixed "
                    "on something beyond mortal perception. Yellow headband. Long beard moving "
                    "in impossible wind. Book of Heaven scrolls implied in composition. "
                    "Background: supernatural storm gathering, teal lightning in dark sky. "
                    "Yellow ochre, storm teal (#1E6B7A), deep gold. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "full_body",
                "seed": 6252,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Full body standing portrait of Chang Chio: tall elongated ascetic figure, "
                    "pulled upward toward Heaven. Yellow-ochre and teal ceremonial robes, yellow "
                    "headband, long beard. Full figure head to toe. Standing before a sea of "
                    "followers wearing yellow headbands — a visual sea of saffron. Arms "
                    "outstretched commanding weather itself. Storm teal supernatural aura. "
                    "Yellow ochre (#D4943A), storm teal, earth umber crowd tones. "
                    "No text, no words, no lettering."
                ),
            },
            {
                "suffix": "dramatic",
                "seed": 6253,
                "size": "768x1024",
                "prompt": (
                    f"{STYLE_PREFIX}"
                    "Dramatic scene of Chang Chio calling phantom armies from the storm: "
                    "elongated figure standing on a hilltop, arms raised, yellow-ochre and teal "
                    "robes whipping in supernatural wind. Storm teal lightning crackles through "
                    "a black sky. Phantom soldiers made of storm-teal mist materialize from the "
                    "clouds — ghostly army descending. His eyes glow with cosmic force. Below: "
                    "terrified mortal soldiers looking up. Full supernatural protocol — normal "
                    "shadow breaks, humans diminished. Storm teal, midnight ink, yellow ochre. "
                    "No text, no words, no lettering."
                ),
            },
        ],
    },
]

ENVIRONMENTS = [
    {
        "name": "set_peach_garden",
        "seed": 6300,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "The Peach Garden in spring: a sacred grove of peach trees in full glorious bloom, "
            "pink and white blossoms cascading in golden afternoon light. A simple stone altar "
            "at center with incense burners, ceremonial wine vessels, offerings of black ox and "
            "white horse. Jade green grass, petals drifting through warm air. Song Dynasty "
            "landscape atmosphere with misty mountains in background. Color palette: jade green "
            "(#3A7D44), imperial gold (#C9963D), cinnabar red (#C1392B) altar cloth, parchment "
            "ivory blossoms. No figures. No text, no words, no lettering."
        ),
    },
    {
        "name": "set_han_imperial_court",
        "seed": 6301,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "Interior of the Han Imperial Court in decay: vast throne hall with towering columns, "
            "elaborate dragon carvings, imperial gold and crimson lacquer — but shadows pool in "
            "every corner, dust motes drift through failing shafts of light, silk hangings fray. "
            "The Dragon Throne sits in deep shadow. Midnight ink (#1A1A2E) dominates with dying "
            "imperial gold highlights. Architecture precise but overlaid with visible entropy. "
            "Eunuchs' shadows on walls. No figures. No text, no words, no lettering."
        ),
    },
    {
        "name": "set_battlefield",
        "seed": 6302,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "A Three Kingdoms battlefield: explosive diagonal compositions with motion-blur ink "
            "streaks. Dust and smoke obscure the middle distance. War banners of multiple armies "
            "in crimson, yellow, and black wave above the chaos. Fallen weapons, broken chariots, "
            "scattered arrows in the foreground. Individual heroes would be crisply rendered "
            "against the chaotic abstract background. Earth umber (#6B3D1E), cinnabar red, "
            "midnight ink, smoke ash (#7A7A8A). No figures. No text, no words, no lettering."
        ),
    },
    {
        "name": "set_yellow_turban_camp",
        "seed": 6303,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "A Yellow Turban rebel encampment at night: sea of saffron-yellow tents and banners "
            "under a supernatural storm teal sky. Campfires cast warm amber light against the "
            "cosmic teal darkness. Yellow headband banners flutter everywhere. In the distance, "
            "storm-teal lightning flickers with supernatural portent. Earth and ochre tones "
            "dominate the ground. Yellow ochre (#D4943A), storm teal (#1E6B7A), earth umber, "
            "amber firelight. No figures. No text, no words, no lettering."
        ),
    },
    {
        "name": "set_burning_palace",
        "seed": 6304,
        "size": "1024x768",
        "prompt": (
            f"{STYLE_PREFIX}"
            "The Imperial Palace of Loyang in flames: apocalyptic scene of cinnabar red fire "
            "consuming ancient architecture against a midnight sky. Dragon-carved pillars collapse, "
            "silk curtains burn, imperial gold melts. The fire reflects off the night sky turning "
            "it blood-red. Sparks and embers rise like inverse snowfall. This is civilization "
            "itself burning. Cinnabar red (#C1392B), midnight ink (#1A1A2E), imperial gold melting, "
            "bone white ash. No figures. No text, no words, no lettering."
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

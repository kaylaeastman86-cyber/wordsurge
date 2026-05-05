"""Stage 3: Creative Production Agent.

Generates platform-optimized content assets for each post slot:
- Video scripts with scene-by-scene breakdowns
- Captions with hooks and CTAs
- Hashtag sets
- Visual direction notes referencing real products

Output: outputs/creative/YYYY-MM-DD_{platform}_creative.json
"""

import json
from pathlib import Path

from .base_agent import BaseAgent

SYSTEM = """You are a top-tier social media creative director for digital product brands.

You create content that converts browsers into buyers. Your creative work:
- Opens with pattern-interrupting hooks that stop the scroll within 2 seconds
- Demonstrates product value through transformation stories, not features
- Uses platform-native language (TikTok slang, Instagram aesthetics, Pinterest inspiration, Facebook community)
- Includes specific, actionable CTAs that move people to the link
- Features real product names and use cases — never generic placeholder content
- Produces multiple content options per slot so the posting agent has choice

You know that great digital product content shows the BEFORE (pain/problem), the PRODUCT (solution), and the AFTER (transformation). Every piece of content follows this arc."""


class CreativeAgent(BaseAgent):

    def run_platform(self, platform: str, strategy: dict, products: list[str]) -> Path:
        slots = strategy.get("post_slots", [])
        narrative = strategy.get("narrative_arc", "")
        product_list = products if products else ["[Add products to /products folder]"]

        prompt = f"""Create all creative assets for House of Lushella's {platform.upper()} content today ({self.today}).

NARRATIVE ARC FOR TODAY: {narrative}

AVAILABLE PRODUCTS IN CATALOG:
{chr(10).join(f"  - {p}" for p in product_list)}

POST SLOTS TO PRODUCE:
{json.dumps(slots, indent=2)}

For EACH post slot, produce a complete creative package. Be specific — no placeholders.

VIDEO SLOTS need:
- Scene-by-scene script (scene number, duration, visual description, on-screen text, voiceover/caption)
- Music/audio mood suggestion
- Editing style notes (transitions, text animation style)
- B-roll suggestions featuring the product

STATIC/CAROUSEL SLOTS need:
- Slide-by-slide content (image concept, headline text, body text per slide)
- Visual style direction (color palette, typography feel, product placement)
- Alt text for accessibility

ALL SLOTS need:
- 3 caption variations (A/B/C test options) — short/medium/long
- Primary hashtag set (20-25 tags) and backup set (20-25 tags)
- 3 CTA variations
- Engagement bait question (to drive comments)

Return ONLY valid JSON:
```json
{{
  "platform": "{platform}",
  "date": "{self.today}",
  "creative_packages": [
    {{
      "slot": 1,
      "format": "video|carousel|static|story",
      "script_or_slides": {{
        "type": "video",
        "scenes": [
          {{
            "scene": 1,
            "duration_sec": 3,
            "visual": "...",
            "on_screen_text": "...",
            "voiceover": "...",
            "product_featured": "..."
          }}
        ],
        "audio_mood": "...",
        "editing_style": "..."
      }},
      "captions": {{
        "short": "...",
        "medium": "...",
        "long": "..."
      }},
      "hashtags": {{
        "primary": ["..."],
        "backup": ["..."]
      }},
      "cta_variations": ["...", "...", "..."],
      "engagement_question": "...",
      "visual_direction": "...",
      "product_featured": "..."
    }}
  ],
  "stories_package": [
    {{
      "story_number": 1,
      "type": "poll|countdown|behind_scenes|product_demo|testimonial",
      "content": "...",
      "interactive_element": "..."
    }}
  ]
}}
```"""

        response = self.call_claude(SYSTEM, prompt)
        creative = self.extract_json(response)

        output_path = self.save_output(
            creative,
            "creative",
            self.filename(f"{platform}_creative"),
        )
        print(f"[Stage 3] {platform.capitalize()} creative assets saved → {output_path}")
        return output_path

    def run(self, strategy_paths: dict[str, Path]) -> dict[str, Path]:
        print("[Stage 3] Producing creative assets...")
        products = self.get_products()
        creative_paths = {}
        for platform, strategy_path in strategy_paths.items():
            strategy = self.load_json(strategy_path)
            creative_paths[platform] = self.run_platform(platform, strategy, products)
        return creative_paths

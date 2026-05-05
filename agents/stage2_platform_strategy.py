"""Stage 2: Platform-Specific Strategy Agents (4 parallel agents).

Each platform agent reads the research brief and produces:
- Daily posting frequency & optimal times
- Content direction for each post slot
- Platform-specific tone and format guidance

Outputs: outputs/strategy/{platform}/YYYY-MM-DD_strategy.json
"""

import json
from pathlib import Path

from .base_agent import BaseAgent

SYSTEM_TEMPLATE = """You are the dedicated {platform} strategy agent for House of Lushella.

You are an expert in {platform}'s algorithm, audience psychology, and content mechanics.
You know exactly:
- How many times to post per day without triggering shadowban or reach penalties
- The precise windows when House of Lushella's audience ({audience}) is most active
- What content structures, lengths, and formats {platform}'s algorithm currently rewards
- How to sequence posts throughout the day for maximum cumulative reach
- What hooks work for digital product discovery on {platform} specifically

You produce daily content strategies that posting agents can execute with zero ambiguity."""

PLATFORM_CONTEXT = {
    "tiktok": {
        "audience_active": "7-9 AM, 12-3 PM, 7-11 PM",
        "max_posts_day": "3-5",
        "primary_format": "short-form video (15-60 sec)",
        "discovery_mechanism": "For You Page algorithm via watch time + shares",
        "cta_style": "link in bio → Payhip/Etsy",
    },
    "instagram": {
        "audience_active": "6-9 AM, 11 AM-1 PM, 7-9 PM",
        "max_posts_day": "1-2 feed posts + 5-7 Stories + 1 Reel",
        "primary_format": "Reels (7-30 sec), carousels (5-10 slides), Stories",
        "discovery_mechanism": "Reels Explore, hashtag search, saves signal",
        "cta_style": "link in bio, story swipe-up, DM automation",
    },
    "pinterest": {
        "audience_active": "8-11 PM weekdays, all day weekends",
        "max_posts_day": "5-15 Pins (batching acceptable)",
        "primary_format": "vertical static pins (2:3 ratio), Idea Pins, video pins",
        "discovery_mechanism": "keyword search, board suggestions, visual similarity",
        "cta_style": "direct link to product page on each Pin",
    },
    "facebook": {
        "audience_active": "1-4 PM, 6-9 PM",
        "max_posts_day": "1-2 posts + Stories",
        "primary_format": "video (1-3 min), link posts, carousels, Stories",
        "discovery_mechanism": "Group engagement, shares, Reels cross-post",
        "cta_style": "post comments, Messenger, direct link post",
    },
}


class PlatformStrategyAgent(BaseAgent):

    def run_platform(self, platform: str, research_brief: dict) -> Path:
        ctx = PLATFORM_CONTEXT[platform]
        system = SYSTEM_TEMPLATE.format(
            platform=platform.capitalize(),
            audience=self.settings["brand"]["target_audience"],
        )

        platform_research = research_brief.get("platforms", {}).get(platform, {})
        strategic_theme = research_brief.get("strategic_theme", "")
        urgent_opps = research_brief.get("urgent_opportunities", [])

        prompt = f"""Build today's ({self.today}) content strategy for House of Lushella on {platform.upper()}.

PLATFORM SPECS
- Optimal post windows: {ctx['audience_active']}
- Max daily posts: {ctx['max_posts_day']}
- Primary format: {ctx['primary_format']}
- Discovery mechanism: {ctx['discovery_mechanism']}
- CTA style: {ctx['cta_style']}

TODAY'S RESEARCH INTELLIGENCE
Strategic theme: {strategic_theme}
Urgent opportunities: {json.dumps(urgent_opps)}
Platform-specific data: {json.dumps(platform_research, indent=2)}

STRATEGY REQUIREMENTS
1. Determine exact posting frequency for today (number and rationale)
2. Define precise posting times (e.g., 7:15 AM, 12:30 PM) with reasoning
3. For EACH post slot, specify:
   - Content format (video/carousel/static/story)
   - Hook / opening line
   - Core message angle
   - Product focus (if products are available)
   - Hashtag set (mix rising + peak from research)
   - CTA wording
   - Caption length and tone
4. Define today's overall narrative arc (how posts build on each other)
5. Identify the single most important post of the day

Return ONLY valid JSON:
```json
{{
  "platform": "{platform}",
  "date": "{self.today}",
  "posting_frequency": {{
    "count": 0,
    "rationale": "..."
  }},
  "narrative_arc": "...",
  "hero_post_slot": 1,
  "post_slots": [
    {{
      "slot": 1,
      "time": "HH:MM AM/PM",
      "format": "...",
      "hook": "...",
      "message_angle": "...",
      "product_focus": "...",
      "hashtags": ["...", "..."],
      "cta": "...",
      "caption_length": "short|medium|long",
      "tone": "..."
    }}
  ],
  "stories_plan": {{
    "count": 0,
    "themes": ["..."]
  }},
  "engagement_windows": ["HH:MM AM/PM - HH:MM AM/PM"]
}}
```"""

        response = self.call_claude(system, prompt)
        strategy = self.extract_json(response)

        output_path = self.save_output(
            strategy,
            f"strategy/{platform}",
            self.filename("strategy"),
        )
        print(f"[Stage 2] {platform.capitalize()} strategy saved → {output_path}")
        return output_path

    def run(self, research_path: Path) -> dict[str, Path]:
        print("[Stage 2] Building platform strategies...")
        research = self.load_json(research_path)
        strategy_paths = {}
        for platform in self.settings["platforms"]:
            strategy_paths[platform] = self.run_platform(platform, research)
        return strategy_paths

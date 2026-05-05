"""Stage 1: Competitive Intelligence & Market Research.

Produces a daily research brief covering all four platforms.
Output: outputs/research/YYYY-MM-DD_brief.json
"""

import json
from pathlib import Path

from .base_agent import BaseAgent

SYSTEM = """You are a senior social media intelligence analyst specializing in digital product brands.

Your role is to conduct deep competitive analysis and surface actionable insights every day. You study:
- What competitors are posting and how it performs
- Trending content formats, hooks, and topics on each platform
- Algorithm behavior changes and reach signals
- Hashtag momentum (rising vs saturated)
- Audience sentiment patterns
- What content types are driving digital product sales right now

You output structured, data-rich research briefs that platform strategists can act on immediately."""


class ResearchAgent(BaseAgent):

    def run(self, previous_report: dict | None = None) -> Path:
        print("[Stage 1] Running competitive research...")

        products = self.get_products()
        product_info = (
            f"Available products in catalog: {', '.join(products)}"
            if products
            else "No product files found in /products — use general digital product category insights."
        )

        yesterday_insights = ""
        if previous_report:
            yesterday_insights = f"""
YESTERDAY'S PERFORMANCE CONTEXT (use to refine today's research focus):
{json.dumps(previous_report.get('key_insights', {}), indent=2)}
"""

        prompt = f"""Conduct today's ({self.today}) competitive intelligence research for House of Lushella.

{product_info}

{yesterday_insights}

Analyze each of the four platforms (TikTok, Instagram, Pinterest, Facebook) and produce a comprehensive research brief.

For EACH platform, research and report:
1. **Trending content formats** this week (video styles, carousel patterns, static post trends)
2. **Top performing hooks** for digital product content (first 3 seconds / first line)
3. **Hashtag intelligence**: 5 rising hashtags (gaining traction), 5 peak hashtags (high volume), 3 saturated hashtags to avoid
4. **Competitor moves**: What are top digital product sellers doing differently this week?
5. **Algorithm signals**: Any recent changes affecting reach or discovery?
6. **Audience sentiment**: What pain points / desires are your target audience expressing?
7. **Content gap opportunity**: One underserved angle competitors are missing
8. **Conversion patterns**: What CTA styles are driving clicks to Payhip/Etsy?

Then provide:
- **Today's strategic theme** (single unifying content angle across all platforms)
- **Top 3 urgent opportunities** to act on today
- **Content angles to avoid** today (oversaturated or low-performing)

Return ONLY valid JSON matching this exact structure:
```json
{{
  "date": "{self.today}",
  "strategic_theme": "...",
  "urgent_opportunities": ["...", "...", "..."],
  "angles_to_avoid": ["...", "..."],
  "platforms": {{
    "tiktok": {{
      "trending_formats": ["..."],
      "top_hooks": ["..."],
      "hashtags": {{
        "rising": ["...", "...", "...", "...", "..."],
        "peak": ["...", "...", "...", "...", "..."],
        "avoid": ["...", "...", "..."]
      }},
      "competitor_moves": "...",
      "algorithm_signal": "...",
      "audience_sentiment": "...",
      "content_gap": "...",
      "conversion_pattern": "..."
    }},
    "instagram": {{
      "trending_formats": ["..."],
      "top_hooks": ["..."],
      "hashtags": {{
        "rising": ["...", "...", "...", "...", "..."],
        "peak": ["...", "...", "...", "...", "..."],
        "avoid": ["...", "...", "..."]
      }},
      "competitor_moves": "...",
      "algorithm_signal": "...",
      "audience_sentiment": "...",
      "content_gap": "...",
      "conversion_pattern": "..."
    }},
    "pinterest": {{
      "trending_formats": ["..."],
      "top_hooks": ["..."],
      "hashtags": {{
        "rising": ["...", "...", "...", "...", "..."],
        "peak": ["...", "...", "...", "...", "..."],
        "avoid": ["...", "...", "..."]
      }},
      "competitor_moves": "...",
      "algorithm_signal": "...",
      "audience_sentiment": "...",
      "content_gap": "...",
      "conversion_pattern": "..."
    }},
    "facebook": {{
      "trending_formats": ["..."],
      "top_hooks": ["..."],
      "hashtags": {{
        "rising": ["...", "...", "...", "...", "..."],
        "peak": ["...", "...", "...", "...", "..."],
        "avoid": ["...", "...", "..."]
      }},
      "competitor_moves": "...",
      "algorithm_signal": "...",
      "audience_sentiment": "...",
      "content_gap": "...",
      "conversion_pattern": "..."
    }}
  }}
}}
```"""

        response = self.call_claude(SYSTEM, prompt)
        brief = self.extract_json(response)

        output_path = self.save_output(brief, "research", self.filename("brief"))
        print(f"[Stage 1] Research brief saved → {output_path}")
        return output_path

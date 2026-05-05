"""Stage 7: Customer Journey Mapping Agent.

Maps the complete path from content discovery to purchase:
- Awareness → interest → consideration → purchase funnel
- Platform-specific journey paths
- Funnel dropoff analysis and friction points
- Touchpoint sequencing recommendations
- Retargeting trigger points

Output: outputs/journey/YYYY-MM-DD_journey.json
"""

import json
from pathlib import Path

from .base_agent import BaseAgent

SYSTEM = """You are the customer journey strategist for House of Lushella.

You think like a buyer, not a seller. You map the exact psychological and behavioral path
someone takes from first seeing House of Lushella content to completing a purchase on Payhip or Etsy.

You understand:
- Each platform creates a different first impression and intent level
- Digital product buyers need to trust the creator before buying
- The average buyer sees content 3-7 times before purchasing
- Friction points (price shock, unclear value, trust gaps) kill conversions at specific stages
- Different audience segments move through the funnel at different speeds

Your journey maps give the team a clear picture of where buyers get stuck and exactly what
content or touchpoint to serve next to move them forward."""


class JourneyAgent(BaseAgent):

    def run(self, analytics_path: Path, engagement_path: Path) -> Path:
        print("[Stage 7] Mapping customer journey...")

        analytics = self.load_json(analytics_path)
        engagement = self.load_json(engagement_path)

        products = self.get_products()
        product_list = products if products else ["[digital products]"]

        prompt = f"""Map today's ({self.today}) customer journey for House of Lushella.

ANALYTICS CONTEXT:
- Overall performance score: {analytics.get('overall_performance_score', 'N/A')}
- Top content angles: {analytics.get('content_insights', {}).get('top_angles', [])}
- Product performance: {json.dumps(analytics.get('product_performance', []), indent=2)}

ENGAGEMENT SIGNALS:
- Green flags (high-intent): {engagement.get('sentiment_flags', {}).get('green', [])}
- Yellow flags (nurturing needed): {engagement.get('sentiment_flags', {}).get('yellow', [])}
- Red flags (friction): {engagement.get('sentiment_flags', {}).get('red', [])}

PRODUCTS IN CATALOG:
{chr(10).join(f"  - {p}" for p in product_list)}

Map the complete customer journey covering:

1. **AWARENESS STAGE** — How people discover House of Lushella today:
   - Which platforms are the primary discovery channels
   - What content types create first impressions
   - Cold audience entry points

2. **INTEREST STAGE** — What moves someone from scroll to pause:
   - Content patterns that trigger saves/follows
   - The "aha moment" for each product type
   - Platform-specific interest signals (saves on Instagram, profile visits on TikTok, etc.)

3. **CONSIDERATION STAGE** — What happens between interest and purchase:
   - Typical research behaviors (profile visit, story views, DMs)
   - Trust-building touchpoints needed
   - Objection moments and what triggers them
   - Average time in consideration stage by platform

4. **DECISION STAGE** — What pushes someone to click buy:
   - Final conversion triggers
   - CTA effectiveness by platform
   - Price anchoring moments
   - Social proof requirements

5. **FUNNEL DROPOFF POINTS** — Where buyers are lost today:
   - Stage with highest abandonment
   - Specific friction points per platform
   - Content gaps causing dropoff

6. **JOURNEY SEQUENCES** — Recommended multi-touch sequences:
   - Cold audience nurture sequence (5 touchpoints)
   - Warm audience conversion sequence (3 touchpoints)
   - Re-engagement sequence for lapsed followers

7. **SEGMENT PROFILES** — 3 buyer personas:
   - Who they are, their pain point, their journey speed, best conversion trigger

Return ONLY valid JSON:
```json
{{
  "date": "{self.today}",
  "funnel_health_score": 0,
  "awareness": {{
    "primary_channels": ["..."],
    "top_discovery_content": "...",
    "cold_audience_size_estimate": "...",
    "awareness_gap": "..."
  }},
  "interest": {{
    "scroll_stop_triggers": ["..."],
    "save_follow_patterns": ["..."],
    "aha_moments_by_product": [
      {{"product": "...", "aha_moment": "..."}}
    ],
    "interest_rate_estimate": 0.0
  }},
  "consideration": {{
    "research_behaviors": ["..."],
    "trust_touchpoints": ["..."],
    "avg_consideration_days_by_platform": {{
      "tiktok": 0, "instagram": 0, "pinterest": 0, "facebook": 0
    }},
    "top_objections": ["..."]
  }},
  "decision": {{
    "conversion_triggers": ["..."],
    "best_cta_by_platform": {{
      "tiktok": "...", "instagram": "...", "pinterest": "...", "facebook": "..."
    }},
    "price_anchoring_strategy": "...",
    "social_proof_required": "..."
  }},
  "dropoff_analysis": {{
    "highest_abandonment_stage": "awareness|interest|consideration|decision",
    "abandonment_rate_estimate": 0.0,
    "friction_points": [
      {{"stage": "...", "platform": "...", "friction": "...", "fix": "..."}}
    ]
  }},
  "nurture_sequences": {{
    "cold_audience": [
      {{"touchpoint": 1, "platform": "...", "content_type": "...", "goal": "...", "timing": "..."}}
    ],
    "warm_audience": [
      {{"touchpoint": 1, "platform": "...", "content_type": "...", "goal": "...", "timing": "..."}}
    ],
    "re_engagement": [
      {{"touchpoint": 1, "platform": "...", "content_type": "...", "goal": "...", "timing": "..."}}
    ]
  }},
  "buyer_personas": [
    {{
      "name": "...",
      "description": "...",
      "pain_point": "...",
      "journey_speed": "fast|medium|slow",
      "best_platform": "...",
      "conversion_trigger": "...",
      "content_that_resonates": "..."
    }}
  ],
  "journey_optimization_priorities": ["...", "...", "..."]
}}
```"""

        response = self.call_claude(SYSTEM, prompt)
        journey = self.extract_json(response)

        output_path = self.save_output(
            journey, "journey", self.filename("journey")
        )
        print(f"[Stage 7] Customer journey map saved → {output_path}")
        return output_path

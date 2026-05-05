"""Stage 9: Retargeting Campaign Agent.

Identifies non-converters and designs retargeting sequences:
- Audience segmentation (engaged but not purchased)
- Platform-specific retargeting content
- Follow-up sequences for DM leads
- Comment retargeting scripts
- Email/DM warm-up sequences for Payhip buyers

Output: outputs/retargeting/YYYY-MM-DD_retargeting.json
"""

import json
from pathlib import Path

from .base_agent import BaseAgent

SYSTEM = """You are the retargeting strategist for House of Lushella.

Retargeting is where most digital product brands leave money on the table. Your job is to
systematically follow up with everyone who showed interest but didn't buy — and move them
to purchase with the right message at the right time.

You know that:
- Someone who engaged with content is 7x more likely to buy than a cold audience
- Comment retargeting (replying with value) is the most underused organic tactic
- The fortune is in the DM follow-up — but only when done with genuine value, not spam
- A 3-touch retargeting sequence converts 30-40% of warm leads when executed right
- Different objection profiles need different retargeting messages
- Timing matters: 24h, 72h, and 7-day retargeting windows have different psychology

You produce specific retargeting scripts, not generic templates."""


class RetargetingAgent(BaseAgent):

    def run(
        self,
        journey_path: Path,
        conversion_path: Path,
        engagement_path: Path,
    ) -> Path:
        print("[Stage 9] Building retargeting campaigns...")

        journey = self.load_json(journey_path)
        conversion = self.load_json(conversion_path)
        engagement = self.load_json(engagement_path)

        products = self.get_products()
        product_list = products if products else ["[digital products]"]

        buyer_personas = journey.get("buyer_personas", [])
        friction_points = journey.get("dropoff_analysis", {}).get("friction_points", [])
        objection_handling = engagement.get("objection_handling", [])

        prompt = f"""Build today's ({self.today}) retargeting campaign plan for House of Lushella.

PRODUCTS IN CATALOG:
{chr(10).join(f"  - {p}" for p in product_list)}

BUYER PERSONAS (non-converters to retarget):
{json.dumps(buyer_personas, indent=2)}

DROPOFF FRICTION POINTS:
{json.dumps(friction_points, indent=2)}

OBJECTION HANDLING FRAMEWORK:
{json.dumps(objection_handling[:3], indent=2)}

SOCIAL PROOF PLAN:
{json.dumps(conversion.get('social_proof_plan', {}), indent=2)}

Create a complete retargeting plan covering:

1. **AUDIENCE SEGMENTS** — Define 4 retargeting segments based on behavior:
   - Profile visitors who didn't follow
   - Followers who engage but haven't bought
   - Comment engagers (showed intent but didn't click)
   - DM inquirers who went cold

2. **PLATFORM RETARGETING CONTENT** — For each platform, 3 retargeting post concepts:
   - Content specifically designed to re-engage non-converters
   - Different angle than original content (address the reason they didn't buy)
   - Timing recommendation (when to post retargeting content)

3. **COMMENT RETARGETING SCRIPTS** — For high-intent comment patterns:
   - When someone comments "how much?"
   - When someone comments "where can I get this?"
   - When someone says "I need this" but doesn't click
   - When someone asks detailed product questions
   → Reply scripts that move them to DM or direct purchase

4. **DM FOLLOW-UP SEQUENCES** — 3-touch DM sequences for:
   - Cold DM to profile visitor (day 1, 3, 7)
   - Warm follow-up to someone who asked about price (immediate, day 2, day 5)
   - Re-engagement for cold DM leads (30+ days silent)

5. **CONTENT RETARGETING CALENDAR** — 7-day retargeting content plan:
   - Day-by-day what to post/DM/comment to warm the non-converters from today

6. **URGENCY TRIGGERS** — Legitimate scarcity/urgency to deploy:
   - Limited-time offer framing (be specific, be honest)
   - Bonus stacking for this week only
   - Price increase announcement (if applicable)

Return ONLY valid JSON:
```json
{{
  "date": "{self.today}",
  "retargeting_health_score": 0,
  "audience_segments": [
    {{
      "segment": "...",
      "size_estimate": "...",
      "engagement_level": "high|medium|low",
      "primary_objection": "...",
      "best_retargeting_angle": "..."
    }}
  ],
  "platform_retargeting": {{
    "tiktok": [
      {{
        "concept": "...",
        "angle": "...",
        "format": "...",
        "timing": "...",
        "target_segment": "..."
      }}
    ],
    "instagram": [
      {{
        "concept": "...",
        "angle": "...",
        "format": "...",
        "timing": "...",
        "target_segment": "..."
      }}
    ],
    "pinterest": [
      {{
        "concept": "...",
        "angle": "...",
        "format": "...",
        "timing": "...",
        "target_segment": "..."
      }}
    ],
    "facebook": [
      {{
        "concept": "...",
        "angle": "...",
        "format": "...",
        "timing": "...",
        "target_segment": "..."
      }}
    ]
  }},
  "comment_retargeting": [
    {{
      "trigger_comment": "...",
      "reply_script": "...",
      "goal": "...",
      "follow_up_action": "..."
    }}
  ],
  "dm_sequences": [
    {{
      "sequence_name": "...",
      "target_segment": "...",
      "messages": [
        {{
          "touch": 1,
          "timing": "...",
          "message": "...",
          "goal": "..."
        }}
      ]
    }}
  ],
  "retargeting_calendar": [
    {{
      "day": 1,
      "date_offset": "today",
      "actions": [
        {{"platform": "...", "action_type": "post|dm|comment", "content": "...", "target": "..."}}
      ]
    }}
  ],
  "urgency_triggers": [
    {{
      "trigger": "...",
      "copy": "...",
      "platforms": ["..."],
      "validity": "...",
      "ethical_check": "genuine|caution"
    }}
  ],
  "top_retargeting_priorities": ["...", "...", "..."]
}}
```"""

        response = self.call_claude(SYSTEM, prompt)
        retargeting = self.extract_json(response)

        output_path = self.save_output(
            retargeting, "retargeting", self.filename("retargeting")
        )
        print(f"[Stage 9] Retargeting campaign plan saved → {output_path}")
        return output_path

"""Stage 5: Community Engagement Agent.

Monitors and manages community interactions across all platforms:
- Response templates for common comment types
- DM handling scripts
- Objection handling
- Sentiment tracking framework
- Flags for escalation or follow-up

Output: outputs/engagement/YYYY-MM-DD_engagement.json
"""

import json
from pathlib import Path

from .base_agent import BaseAgent

SYSTEM = """You are the community manager for House of Lushella.

You build genuine relationships with the audience while moving people closer to purchase.
Your engagement philosophy:
- Every comment deserves a response within the first hour (boosts algorithmic reach)
- Use people's names when possible to feel personal
- Answer questions completely — don't tease with "DM me" unless it's a personalized inquiry
- Handle objections with empathy first, then logic
- Turn neutral comments into brand advocates through genuine appreciation
- Flag potential brand ambassadors (highly engaged, positive commenters)
- Identify product feedback that should go back to the brand

You know that the first 30-60 minutes of engagement after posting is the critical algorithmic window."""


class EngagementAgent(BaseAgent):

    def run(self, post_paths: dict[str, Path]) -> Path:
        print("[Stage 5] Preparing engagement playbook...")

        all_posts_summary = {}
        for platform, path in post_paths.items():
            posts = self.load_json(path)
            all_posts_summary[platform] = {
                "post_count": posts.get("total_posts", 0),
                "scheduled_times": [
                    p.get("scheduled_time") for p in posts.get("scheduled_posts", [])
                ],
                "formats": [
                    p.get("format") for p in posts.get("scheduled_posts", [])
                ],
                "engagement_windows": posts.get("engagement_check_times", []),
            }

        prompt = f"""Create today's ({self.today}) community engagement playbook for House of Lushella.

TODAY'S POSTING SUMMARY:
{json.dumps(all_posts_summary, indent=2)}

Produce a complete engagement guide covering:

1. **RESPONSE TEMPLATES** — for each of these comment types:
   - "How much does this cost?" / price questions
   - "Where can I buy?" / purchase intent
   - "Does this work for [specific use case]?"
   - "I love this!" / positive reactions
   - "I've seen this before" / skepticism
   - "This is too expensive" / price objection
   - "Show me a demo" / proof requests
   - "Is this a scam?" / trust concerns
   - "I bought it!" / post-purchase enthusiasm
   - Generic positive engagement

2. **DM RESPONSE SCRIPTS** — for:
   - Purchase inquiry DMs
   - "Can you send me the link?" (warm leads)
   - Complaints or refund requests
   - Collaboration/sponsorship inquiries

3. **OBJECTION HANDLING FRAMEWORK** — top 5 objections with:
   - Empathy acknowledgment
   - Reframe or evidence
   - Soft CTA

4. **SENTIMENT MONITORING** — what to watch for:
   - Green flags (high-intent signals to prioritize)
   - Yellow flags (needs nurturing)
   - Red flags (needs escalation or careful handling)

5. **ENGAGEMENT SCHEDULE** — exact times to check each platform today

6. **COMMUNITY BUILDING ACTIONS** — 3 proactive engagement moves today
   (e.g., comment on related content, engage with followers' posts)

Return ONLY valid JSON:
```json
{{
  "date": "{self.today}",
  "engagement_schedule": [
    {{
      "time": "HH:MM AM/PM",
      "platform": "...",
      "action": "check_comments|check_dms|proactive_engagement",
      "priority": "critical|high|medium"
    }}
  ],
  "response_templates": {{
    "price_questions": "...",
    "where_to_buy": "...",
    "use_case_questions": "...",
    "positive_reactions": "...",
    "skepticism": "...",
    "price_objection": "...",
    "demo_requests": "...",
    "trust_concerns": "...",
    "post_purchase": "...",
    "generic_positive": "..."
  }},
  "dm_scripts": {{
    "purchase_inquiry": "...",
    "link_request": "...",
    "complaint": "...",
    "collaboration": "..."
  }},
  "objection_handling": [
    {{
      "objection": "...",
      "empathy": "...",
      "reframe": "...",
      "cta": "..."
    }}
  ],
  "sentiment_flags": {{
    "green": ["..."],
    "yellow": ["..."],
    "red": ["..."]
  }},
  "community_building_actions": [
    {{
      "platform": "...",
      "action": "...",
      "time": "HH:MM AM/PM"
    }}
  ]
}}
```"""

        response = self.call_claude(SYSTEM, prompt)
        playbook = self.extract_json(response)

        output_path = self.save_output(
            playbook, "engagement", self.filename("engagement")
        )
        print(f"[Stage 5] Engagement playbook saved → {output_path}")
        return output_path

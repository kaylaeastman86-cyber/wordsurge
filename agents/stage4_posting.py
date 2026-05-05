"""Stage 4: Posting & Scheduling Agent.

Receives creative assets and produces final post packages with:
- Scheduled post times (verified against strategy)
- Final selected captions and hashtags
- Platform-specific formatting (character limits, link placement)
- Post log for analytics tracking

Output: outputs/posts/{platform}/YYYY-MM-DD_posts.json
"""

import json
from pathlib import Path

from .base_agent import BaseAgent

SYSTEM = """You are the publishing manager for House of Lushella's social media operations.

Your job is to take creative assets and finalize them for publishing. You:
- Select the best caption variant for each post based on platform norms and today's strategy
- Format posts to platform character limits (TikTok 2200, Instagram 2200, Pinterest 500, Facebook 63,206)
- Verify hashtag counts are within platform limits (TikTok 3-5 strategic, Instagram 20-30, Pinterest 5-10, Facebook 3-5)
- Confirm posting schedule aligns with audience active windows
- Flag any content that needs a product image/video file attached
- Create a clean post log that analytics can read

You produce ready-to-publish post packages — everything a social media manager needs to hit POST."""

PLATFORM_LIMITS = {
    "tiktok": {"caption_chars": 2200, "hashtag_count": "3-5 strategic"},
    "instagram": {"caption_chars": 2200, "hashtag_count": "20-30"},
    "pinterest": {"caption_chars": 500, "hashtag_count": "5-10"},
    "facebook": {"caption_chars": 63206, "hashtag_count": "3-5"},
}


class PostingAgent(BaseAgent):

    def run_platform(
        self, platform: str, strategy: dict, creative: dict
    ) -> Path:
        limits = PLATFORM_LIMITS[platform]
        post_slots = strategy.get("post_slots", [])
        creative_packages = creative.get("creative_packages", [])
        engagement_windows = strategy.get("engagement_windows", [])

        prompt = f"""Finalize the posting schedule for House of Lushella on {platform.upper()} today ({self.today}).

PLATFORM LIMITS
- Caption: {limits['caption_chars']} characters max
- Hashtags: {limits['hashtag_count']} tags

STRATEGY POST SLOTS:
{json.dumps(post_slots, indent=2)}

CREATIVE PACKAGES:
{json.dumps(creative_packages, indent=2)}

ENGAGEMENT WINDOWS (check back to respond to comments): {engagement_windows}

For each post slot, finalize:
1. Select the best caption variation (A, B, or C) and confirm it fits character limits
2. Select primary OR backup hashtag set (whichever performs better with today's content angle)
3. Confirm or adjust posting time based on engagement windows
4. List any media assets required (product image filename, video filename)
5. Add a posting checklist (what to verify before hitting publish)

Also produce a stories posting schedule if applicable.

Return ONLY valid JSON:
```json
{{
  "platform": "{platform}",
  "date": "{self.today}",
  "total_posts": 0,
  "scheduled_posts": [
    {{
      "post_id": "{platform}_{self.today}_1",
      "slot": 1,
      "scheduled_time": "HH:MM AM/PM",
      "format": "video|carousel|static|story",
      "final_caption": "...",
      "caption_char_count": 0,
      "final_hashtags": ["..."],
      "hashtag_count": 0,
      "cta": "...",
      "media_required": ["filename_or_description"],
      "product_link": "payhip|etsy|both|none",
      "pre_publish_checklist": ["...", "..."],
      "status": "scheduled"
    }}
  ],
  "stories_schedule": [
    {{
      "story_id": "{platform}_{self.today}_story_1",
      "scheduled_time": "HH:MM AM/PM",
      "content": "...",
      "media_required": "...",
      "status": "scheduled"
    }}
  ],
  "engagement_check_times": {json.dumps(engagement_windows)},
  "daily_notes": "..."
}}
```"""

        response = self.call_claude(SYSTEM, prompt)
        post_log = self.extract_json(response)

        output_path = self.save_output(
            post_log,
            f"posts/{platform}",
            self.filename("posts"),
        )
        print(f"[Stage 4] {platform.capitalize()} post schedule saved → {output_path}")
        return output_path

    def run(
        self, strategy_paths: dict[str, Path], creative_paths: dict[str, Path]
    ) -> dict[str, Path]:
        print("[Stage 4] Finalizing post schedules...")
        post_paths = {}
        for platform in self.settings["platforms"]:
            strategy = self.load_json(strategy_paths[platform])
            creative = self.load_json(creative_paths[platform])
            post_paths[platform] = self.run_platform(platform, strategy, creative)
        return post_paths

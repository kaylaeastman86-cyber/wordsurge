"""Stage 6: Analytics & Performance Tracking Agent.

Reads post schedules and simulates/infers performance metrics to:
- Track estimated reach and engagement per post
- Identify top-performing content types and time slots
- Benchmark against platform averages
- Surface which products/angles drove the most interest
- Flag underperforming posts for adjustment

Output: outputs/analytics/YYYY-MM-DD_analytics.json
"""

import json
from pathlib import Path

from .base_agent import BaseAgent

SYSTEM = """You are the analytics director for House of Lushella's social media operations.

You analyze content performance data and extract actionable intelligence. Your analysis:
- Identifies which content formats, hooks, and angles are winning
- Spots time-slot performance patterns across platforms
- Connects content attributes to engagement signals
- Benchmarks against platform-specific industry averages for digital product brands
- Delivers clear performance verdicts: scale, maintain, or cut

You think in terms of what the data means for tomorrow's decisions, not just what happened today.
When actual metrics aren't available yet, you provide realistic projections based on content quality,
posting times, hashtag strength, and platform algorithm behavior."""


class AnalyticsAgent(BaseAgent):

    def run(self, post_paths: dict[str, Path], engagement_path: Path) -> Path:
        print("[Stage 6] Running analytics & performance tracking...")

        posts_by_platform = {}
        for platform, path in post_paths.items():
            posts_by_platform[platform] = self.load_json(path)

        engagement_data = self.load_json(engagement_path)

        prompt = f"""Analyze today's ({self.today}) content performance for House of Lushella.

TODAY'S POST SCHEDULE:
{json.dumps(posts_by_platform, indent=2)}

ENGAGEMENT PLAYBOOK CONTEXT:
- Scheduled engagement windows: {json.dumps(engagement_data.get('engagement_schedule', [])[:4], indent=2)}
- Sentiment monitoring flags: {json.dumps(engagement_data.get('sentiment_flags', {}), indent=2)}

Produce a comprehensive analytics report covering:

1. **PERFORMANCE PROJECTIONS** — For each post on each platform, project:
   - Estimated reach (based on time slot, format, hashtag strength)
   - Estimated engagement rate (likes + comments + saves / reach)
   - Estimated link clicks / profile visits
   - Content quality score (1-10) with reasoning

2. **PLATFORM SCORECARD** — For each platform:
   - Best-performing post slot (time + format)
   - Weakest post slot
   - Overall reach estimate
   - Hashtag performance tier (strong/average/weak)
   - Recommendation: scale up, maintain, or cut

3. **CONTENT INSIGHTS** — Across all platforms:
   - Top 3 content angles that likely drove engagement
   - Content formats ranking (video vs carousel vs static)
   - Hook effectiveness ratings
   - CTA click-through predictions

4. **PRODUCT PERFORMANCE** — Which products featured today:
   - Estimated interest level per product
   - Best-performing product-platform pairing
   - Products that need more content support

5. **ALGORITHM HEALTH CHECK** — Per platform:
   - Posting frequency vs. recommended: on track / over / under
   - Engagement velocity (first-hour performance estimate)
   - Risk of shadowban or reach suppression

6. **TOMORROW'S QUICK WINS** — 3 immediate adjustments based on today's data

Return ONLY valid JSON:
```json
{{
  "date": "{self.today}",
  "overall_performance_score": 0,
  "platforms": {{
    "tiktok": {{
      "posts_analyzed": 0,
      "estimated_total_reach": 0,
      "avg_engagement_rate": 0.0,
      "best_slot": {{"time": "...", "format": "...", "score": 0}},
      "worst_slot": {{"time": "...", "format": "...", "score": 0}},
      "hashtag_performance": "strong|average|weak",
      "algorithm_health": "healthy|caution|risk",
      "recommendation": "scale_up|maintain|cut",
      "post_scores": [
        {{"post_id": "...", "estimated_reach": 0, "engagement_rate": 0.0, "quality_score": 0, "notes": "..."}}
      ]
    }},
    "instagram": {{
      "posts_analyzed": 0,
      "estimated_total_reach": 0,
      "avg_engagement_rate": 0.0,
      "best_slot": {{"time": "...", "format": "...", "score": 0}},
      "worst_slot": {{"time": "...", "format": "...", "score": 0}},
      "hashtag_performance": "strong|average|weak",
      "algorithm_health": "healthy|caution|risk",
      "recommendation": "scale_up|maintain|cut",
      "post_scores": [
        {{"post_id": "...", "estimated_reach": 0, "engagement_rate": 0.0, "quality_score": 0, "notes": "..."}}
      ]
    }},
    "pinterest": {{
      "posts_analyzed": 0,
      "estimated_total_reach": 0,
      "avg_engagement_rate": 0.0,
      "best_slot": {{"time": "...", "format": "...", "score": 0}},
      "worst_slot": {{"time": "...", "format": "...", "score": 0}},
      "hashtag_performance": "strong|average|weak",
      "algorithm_health": "healthy|caution|risk",
      "recommendation": "scale_up|maintain|cut",
      "post_scores": [
        {{"post_id": "...", "estimated_reach": 0, "engagement_rate": 0.0, "quality_score": 0, "notes": "..."}}
      ]
    }},
    "facebook": {{
      "posts_analyzed": 0,
      "estimated_total_reach": 0,
      "avg_engagement_rate": 0.0,
      "best_slot": {{"time": "...", "format": "...", "score": 0}},
      "worst_slot": {{"time": "...", "format": "...", "score": 0}},
      "hashtag_performance": "strong|average|weak",
      "algorithm_health": "healthy|caution|risk",
      "recommendation": "scale_up|maintain|cut",
      "post_scores": [
        {{"post_id": "...", "estimated_reach": 0, "engagement_rate": 0.0, "quality_score": 0, "notes": "..."}}
      ]
    }}
  }},
  "content_insights": {{
    "top_angles": ["...", "...", "..."],
    "format_ranking": ["...", "..."],
    "hook_effectiveness": {{"strong": ["..."], "weak": ["..."]}},
    "cta_predicted_ctr": 0.0
  }},
  "product_performance": [
    {{
      "product": "...",
      "interest_level": "high|medium|low",
      "best_platform": "...",
      "content_needed": "..."
    }}
  ],
  "tomorrow_quick_wins": ["...", "...", "..."],
  "key_insights": {{
    "biggest_win": "...",
    "biggest_risk": "...",
    "trend_to_watch": "..."
  }}
}}
```"""

        response = self.call_claude(SYSTEM, prompt)
        analytics = self.extract_json(response)

        output_path = self.save_output(
            analytics, "analytics", self.filename("analytics")
        )
        print(f"[Stage 6] Analytics report saved → {output_path}")
        return output_path

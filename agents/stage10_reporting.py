"""Stage 10: Daily Reporting & Insights Feedback Agent.

Synthesizes the entire day's workflow into:
- Executive summary with key metrics and wins
- What worked / what didn't / why
- Actionable adjustments for tomorrow
- Trend signals to watch
- Feedback loop data for Stage 1 research

Output: outputs/reports/YYYY-MM-DD_report.json
This report's 'key_insights' field is fed back into Stage 1 research the next day.
"""

import json
from pathlib import Path

from .base_agent import BaseAgent

SYSTEM = """You are the chief marketing intelligence officer for House of Lushella.

Every evening you synthesize the entire day's marketing intelligence — from research through
retargeting — into a clear, actionable report that makes tomorrow better than today.

Your reports are:
- Brutally honest about what didn't work
- Specific about what to do differently (not "post more" but "shift TikTok slot to 7:15 AM")
- Forward-looking: every insight points to a concrete action
- Data-grounded: every recommendation has a reason
- Brief enough to actually be read: executives scan, they don't read essays

You close the feedback loop by extracting the top insights that tomorrow's research agent
needs to know to refine its analysis. This is how the system gets smarter every day."""


class ReportingAgent(BaseAgent):

    def run(
        self,
        analytics_path: Path,
        journey_path: Path,
        conversion_path: Path,
        retargeting_path: Path,
        engagement_path: Path,
    ) -> Path:
        print("[Stage 10] Generating daily report & insights...")

        analytics = self.load_json(analytics_path)
        journey = self.load_json(journey_path)
        conversion = self.load_json(conversion_path)
        retargeting = self.load_json(retargeting_path)
        engagement = self.load_json(engagement_path)

        prompt = f"""Generate today's ({self.today}) comprehensive marketing intelligence report for House of Lushella.

ANALYTICS SUMMARY:
- Overall performance score: {analytics.get('overall_performance_score', 'N/A')}
- Key insights: {json.dumps(analytics.get('key_insights', {}), indent=2)}
- Tomorrow quick wins: {analytics.get('tomorrow_quick_wins', [])}
- Platform recommendations: {{
    tiktok: {analytics.get('platforms', {}).get('tiktok', {}).get('recommendation', 'N/A')},
    instagram: {analytics.get('platforms', {}).get('instagram', {}).get('recommendation', 'N/A')},
    pinterest: {analytics.get('platforms', {}).get('pinterest', {}).get('recommendation', 'N/A')},
    facebook: {analytics.get('platforms', {}).get('facebook', {}).get('recommendation', 'N/A')}
  }}

JOURNEY HEALTH:
- Funnel health score: {journey.get('funnel_health_score', 'N/A')}
- Highest abandonment stage: {journey.get('dropoff_analysis', {}).get('highest_abandonment_stage', 'N/A')}
- Journey optimization priorities: {journey.get('journey_optimization_priorities', [])}

CONVERSION HEALTH:
- Conversion health score: {conversion.get('conversion_health_score', 'N/A')}
- Top conversion wins: {conversion.get('top_conversion_wins', [])}

RETARGETING HEALTH:
- Retargeting health score: {retargeting.get('retargeting_health_score', 'N/A')}
- Top priorities: {retargeting.get('top_retargeting_priorities', [])}

ENGAGEMENT QUALITY:
- Scheduled engagement actions: {len(engagement.get('engagement_schedule', []))} check-ins planned
- Community building actions: {len(engagement.get('community_building_actions', []))} proactive moves

Synthesize this into a comprehensive daily report:

1. **EXECUTIVE SUMMARY** — 3-sentence overview of the day: what happened, key win, key miss

2. **PERFORMANCE DASHBOARD** — Scorecard with all health scores and overall day grade (A/B/C/D/F)

3. **WHAT WORKED TODAY** — Top 5 wins with specific reasons why they worked

4. **WHAT DIDN'T WORK** — Top 3 underperformers with honest diagnosis

5. **TOMORROW'S ACTION PLAN** — 10 specific, prioritized actions (not vague advice):
   - Each action must have: platform, action, expected impact, owner (content/engagement/strategy)

6. **WEEKLY TREND SIGNALS** — 3 patterns emerging over recent days that need attention

7. **PRODUCT INSIGHTS** — Which products got traction, which need positioning work

8. **AUDIENCE INTELLIGENCE** — New things learned about the target audience today

9. **COMPETITIVE INTELLIGENCE** — Any new observations about what's working in the market

10. **FEEDBACK LOOP DATA** — Key insights for tomorrow's Stage 1 research agent:
    - What research questions to prioritize tomorrow
    - Which platforms to scrutinize more closely
    - What hashtag/format experiments to run
    - Audience segment shifts to investigate

Return ONLY valid JSON:
```json
{{
  "date": "{self.today}",
  "day_grade": "A|B|C|D|F",
  "executive_summary": "...",
  "performance_dashboard": {{
    "analytics_score": 0,
    "funnel_health_score": 0,
    "conversion_health_score": 0,
    "retargeting_health_score": 0,
    "overall_score": 0,
    "vs_yesterday": "better|same|worse"
  }},
  "what_worked": [
    {{"rank": 1, "win": "...", "platform": "...", "reason": "...", "repeat_tomorrow": true}}
  ],
  "what_didnt_work": [
    {{"item": "...", "platform": "...", "diagnosis": "...", "fix": "..."}}
  ],
  "tomorrow_action_plan": [
    {{
      "priority": 1,
      "platform": "...",
      "action": "...",
      "expected_impact": "...",
      "owner": "content|engagement|strategy|all"
    }}
  ],
  "weekly_trend_signals": [
    {{"signal": "...", "evidence": "...", "recommendation": "..."}}
  ],
  "product_insights": [
    {{"product": "...", "status": "gaining|stable|declining", "insight": "...", "action": "..."}}
  ],
  "audience_intelligence": ["...", "...", "..."],
  "competitive_intelligence": ["...", "..."],
  "key_insights": {{
    "research_priorities_tomorrow": ["...", "...", "..."],
    "platforms_to_scrutinize": ["..."],
    "experiments_to_run": ["..."],
    "audience_segments_to_investigate": ["..."],
    "content_angles_showing_promise": ["..."],
    "content_angles_to_retire": ["..."]
  }}
}}
```"""

        response = self.call_claude(SYSTEM, prompt)
        report = self.extract_json(response)

        output_path = self.save_output(
            report, "reports", self.filename("report")
        )
        print(f"[Stage 10] Daily report saved → {output_path}")
        return output_path

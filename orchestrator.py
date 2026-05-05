"""House of Lushella Marketing Workflow Orchestrator.

Runs the full 10-stage daily marketing pipeline, sequentially:

  Stage 1: Research & competitive intelligence
  Stage 2: Platform strategy (TikTok, Instagram, Pinterest, Facebook)
  Stage 3: Creative production (content assets per platform)
  Stage 4: Posting & scheduling (finalize post packages)
  Stage 5: Community engagement (response playbook)
  Stage 6: Analytics & performance tracking
  Stage 7: Customer journey mapping
  Stage 8: Conversion optimization
  Stage 9: Retargeting campaigns
  Stage 10: Daily reporting & insights (feeds back to Stage 1)

Scheduled to run daily at 06:00 via the `schedule` library.
Run directly for an immediate single execution: python orchestrator.py --now
"""

import argparse
import json
import logging
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import schedule

from agents.stage1_research import ResearchAgent
from agents.stage2_platform_strategy import PlatformStrategyAgent
from agents.stage3_creative import CreativeAgent
from agents.stage4_posting import PostingAgent
from agents.stage5_engagement import EngagementAgent
from agents.stage6_analytics import AnalyticsAgent
from agents.stage7_journey import JourneyAgent
from agents.stage8_conversion import ConversionAgent
from agents.stage9_retargeting import RetargetingAgent
from agents.stage10_reporting import ReportingAgent

LOG_FORMAT = "%(asctime)s  %(levelname)-8s  %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger(__name__)

SETTINGS_PATH = Path(__file__).parent / "config" / "settings.json"


def load_settings() -> dict:
    with open(SETTINGS_PATH) as f:
        return json.load(f)


def latest_report(settings: dict) -> dict | None:
    outputs_dir = Path(settings["paths"]["outputs"])
    reports_dir = outputs_dir / "reports"
    if not reports_dir.exists():
        return None
    files = sorted(reports_dir.glob("*_report.json"))
    if not files:
        return None
    with open(files[-1]) as f:
        return json.load(f)


def run_workflow() -> None:
    start = datetime.now()
    log.info("=" * 60)
    log.info("House of Lushella — Daily Marketing Workflow starting")
    log.info(f"Date: {start.strftime('%Y-%m-%d')}  Time: {start.strftime('%H:%M:%S')}")
    log.info("=" * 60)

    settings = load_settings()
    previous_report = latest_report(settings)

    if previous_report:
        log.info("Found yesterday's report — feeding insights into research")
    else:
        log.info("No previous report found — running cold start")

    try:
        # ── Stage 1: Research ────────────────────────────────────────────────
        research_agent = ResearchAgent(settings)
        research_path = research_agent.run(previous_report=previous_report)

        # ── Stage 2: Platform Strategy ───────────────────────────────────────
        strategy_agent = PlatformStrategyAgent(settings)
        strategy_paths = strategy_agent.run(research_path)

        # ── Stage 3: Creative Production ────────────────────────────────────
        creative_agent = CreativeAgent(settings)
        creative_paths = creative_agent.run(strategy_paths)

        # ── Stage 4: Posting & Scheduling ───────────────────────────────────
        posting_agent = PostingAgent(settings)
        post_paths = posting_agent.run(strategy_paths, creative_paths)

        # ── Stage 5: Community Engagement ───────────────────────────────────
        engagement_agent = EngagementAgent(settings)
        engagement_path = engagement_agent.run(post_paths)

        # ── Stage 6: Analytics ──────────────────────────────────────────────
        analytics_agent = AnalyticsAgent(settings)
        analytics_path = analytics_agent.run(post_paths, engagement_path)

        # ── Stage 7: Customer Journey ────────────────────────────────────────
        journey_agent = JourneyAgent(settings)
        journey_path = journey_agent.run(analytics_path, engagement_path)

        # ── Stage 8: Conversion Optimization ────────────────────────────────
        conversion_agent = ConversionAgent(settings)
        conversion_path = conversion_agent.run(journey_path, analytics_path)

        # ── Stage 9: Retargeting ─────────────────────────────────────────────
        retargeting_agent = RetargetingAgent(settings)
        retargeting_path = retargeting_agent.run(
            journey_path, conversion_path, engagement_path
        )

        # ── Stage 10: Reporting ──────────────────────────────────────────────
        reporting_agent = ReportingAgent(settings)
        report_path = reporting_agent.run(
            analytics_path,
            journey_path,
            conversion_path,
            retargeting_path,
            engagement_path,
        )

        elapsed = (datetime.now() - start).total_seconds()
        log.info("=" * 60)
        log.info(f"Workflow complete in {elapsed:.1f}s")
        log.info(f"Final report: {report_path}")
        log.info("=" * 60)

    except Exception:
        log.error("Workflow failed with unhandled exception:")
        log.error(traceback.format_exc())
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="House of Lushella marketing workflow orchestrator"
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="Run the workflow immediately and exit (skip scheduler)",
    )
    args = parser.parse_args()

    if args.now:
        run_workflow()
        return

    settings = load_settings()
    run_time = settings.get("schedule", {}).get("run_time", "06:00")

    log.info(f"Scheduler active — workflow will run daily at {run_time}")
    schedule.every().day.at(run_time).do(run_workflow)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()

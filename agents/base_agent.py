"""Base agent class — shared client, caching, I/O helpers for all workflow stages."""

import json
import os
import re
from datetime import datetime
from pathlib import Path

import anthropic


class BaseAgent:
    def __init__(self, settings: dict):
        self.settings = settings
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = settings["anthropic"]["model"]
        self.max_tokens = settings["anthropic"]["max_tokens"]
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.outputs_dir = Path(settings["paths"]["outputs"])
        self.products_dir = Path(settings["paths"]["products"])
        self._brand_context = self._build_brand_context()

    def _build_brand_context(self) -> str:
        brand = self.settings["brand"]
        payhip = brand["product_store_urls"].get("payhip", "[configure payhip URL in settings.json]")
        etsy = brand["product_store_urls"].get("etsy", "[configure etsy URL in settings.json]")
        return f"""You are a world-class marketing AI agent for {brand['name']}.

BRAND PROFILE
Name: {brand['name']}
Niche: {brand['niche']}
Tone: {brand['tone']}
Target Audience: {brand['target_audience']}
Sales Channels: Payhip ({payhip}) | Etsy ({etsy})
Core Hashtags: {', '.join(brand['hashtag_base'])}

MARKETING PHILOSOPHY
- Every piece of content must showcase REAL products with authentic use cases
- Lead with customer transformation, not product features
- Platform-native content beats repurposed content every time
- Consistency compounds — small daily gains outperform viral one-offs
- Data drives decisions — track, measure, iterate

Today's date: {self.today}"""

    def call_claude(self, stage_system: str, user_message: str) -> str:
        """Call Claude with prompt caching on the stable brand context + stage system."""
        system = [
            {
                "type": "text",
                "text": self._brand_context,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": stage_system,
                "cache_control": {"type": "ephemeral"},
            },
        ]

        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            thinking={"type": "adaptive"},
            system=system,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            message = stream.get_final_message()

        return "\n".join(
            block.text for block in message.content if block.type == "text"
        )

    def save_output(self, data: dict, subfolder: str, filename: str) -> Path:
        out_dir = self.outputs_dir / subfolder
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / filename
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path

    def load_json(self, path: Path) -> dict:
        with open(path) as f:
            return json.load(f)

    def latest_in(self, subfolder: str) -> Path | None:
        d = self.outputs_dir / subfolder
        if not d.exists():
            return None
        files = sorted(d.glob("*.json"), reverse=True)
        return files[0] if files else None

    def get_products(self) -> list[str]:
        if not self.products_dir.exists():
            return []
        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        video_exts = {".mp4", ".mov", ".avi"}
        return [
            f.name
            for f in self.products_dir.iterdir()
            if f.suffix.lower() in image_exts | video_exts
        ]

    def extract_json(self, text: str) -> dict:
        """Pull JSON from a markdown code block or raw text."""
        m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw_output": text, "parsed": False}

    def filename(self, label: str, ext: str = "json") -> str:
        return f"{self.today}_{label}.{ext}"

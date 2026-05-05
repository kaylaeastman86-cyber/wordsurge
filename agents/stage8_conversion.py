"""Stage 8: Conversion Optimization Agent.

Tests and refines the full conversion path:
- CTA copy testing and recommendations
- Bio link page optimization
- Caption hook A/B analysis
- Price framing strategies
- Landing page content direction
- Checkout friction reduction

Output: outputs/conversion/YYYY-MM-DD_conversion.json
"""

import json
from pathlib import Path

from .base_agent import BaseAgent

SYSTEM = """You are the conversion rate optimization (CRO) specialist for House of Lushella.

You obsess over the gap between content views and product sales. Your job is to find every
place in the funnel where potential buyers hesitate or drop off, then prescribe the exact
change that will move them forward.

You understand:
- Digital product buyers are sophisticated — they can smell generic copy instantly
- Price objections are almost always a value perception problem, not a price problem
- The bio link page is the most under-optimized asset in most creator businesses
- Every extra click between content and checkout costs 20-30% of conversions
- Social proof (testimonials, transformation stories) does more than any discount
- Urgency and scarcity work when they're real — fake urgency destroys trust

You deliver specific, implementable conversion improvements, not vague advice."""


class ConversionAgent(BaseAgent):

    def run(self, journey_path: Path, analytics_path: Path) -> Path:
        print("[Stage 8] Optimizing conversion paths...")

        journey = self.load_json(journey_path)
        analytics = self.load_json(analytics_path)

        products = self.get_products()
        product_list = products if products else ["[digital products]"]

        friction_points = journey.get("dropoff_analysis", {}).get("friction_points", [])
        buyer_personas = journey.get("buyer_personas", [])
        conversion_triggers = journey.get("decision", {}).get("conversion_triggers", [])
        cta_by_platform = journey.get("decision", {}).get("best_cta_by_platform", {})

        prompt = f"""Create today's ({self.today}) conversion optimization plan for House of Lushella.

PRODUCTS IN CATALOG:
{chr(10).join(f"  - {p}" for p in product_list)}

JOURNEY FRICTION POINTS:
{json.dumps(friction_points, indent=2)}

BUYER PERSONAS:
{json.dumps(buyer_personas, indent=2)}

KNOWN CONVERSION TRIGGERS:
{json.dumps(conversion_triggers, indent=2)}

ANALYTICS — CTA Predicted CTR: {analytics.get('content_insights', {}).get('cta_predicted_ctr', 'N/A')}

Produce a full conversion optimization plan:

1. **CTA COPY TESTS** — For each platform, provide 3 tested CTA variations:
   - Control (current standard)
   - Variant A (urgency/scarcity angle)
   - Variant B (benefit/transformation angle)
   - Winner prediction with reasoning

2. **BIO LINK PAGE AUDIT** — Review and optimize the Payhip/Etsy link-in-bio strategy:
   - Current likely structure vs. optimal structure
   - Above-the-fold headline recommendation
   - Product ordering strategy
   - Trust signals to add (testimonials, reviews, guarantees)
   - Mobile optimization priorities

3. **CAPTION HOOK ANALYSIS** — Rate today's hooks and provide improved versions:
   - For each platform's top post: original hook → optimized version → expected lift

4. **PRICE FRAMING STRATEGIES** — How to present product prices to maximize perceived value:
   - Value stack framing (what's included per dollar)
   - Comparison anchoring (vs. alternative cost)
   - Transformation ROI framing (outcome value)
   - Best strategy for each product

5. **SOCIAL PROOF PLAN** — What proof elements to gather and deploy:
   - Testimonial request templates
   - Screenshot/transformation story prompts
   - Where to place proof on each platform

6. **CHECKOUT FRICTION REDUCTION** — Platform-by-platform:
   - Steps between content and purchase
   - Friction points to eliminate
   - Direct-to-checkout optimizations

7. **TODAY'S CONVERSION TESTS** — 3 specific A/B tests to run today:
   - What to test, how to measure, success criteria

Return ONLY valid JSON:
```json
{{
  "date": "{self.today}",
  "conversion_health_score": 0,
  "cta_tests": {{
    "tiktok": {{
      "control": "...",
      "variant_a": "...",
      "variant_b": "...",
      "predicted_winner": "control|variant_a|variant_b",
      "reasoning": "..."
    }},
    "instagram": {{
      "control": "...",
      "variant_a": "...",
      "variant_b": "...",
      "predicted_winner": "control|variant_a|variant_b",
      "reasoning": "..."
    }},
    "pinterest": {{
      "control": "...",
      "variant_a": "...",
      "variant_b": "...",
      "predicted_winner": "control|variant_a|variant_b",
      "reasoning": "..."
    }},
    "facebook": {{
      "control": "...",
      "variant_a": "...",
      "variant_b": "...",
      "predicted_winner": "control|variant_a|variant_b",
      "reasoning": "..."
    }}
  }},
  "bio_link_audit": {{
    "current_structure_assessment": "...",
    "recommended_headline": "...",
    "product_order": ["..."],
    "trust_signals_to_add": ["..."],
    "mobile_priority_fixes": ["..."],
    "estimated_conversion_lift": "..."
  }},
  "hook_optimization": [
    {{
      "platform": "...",
      "post_slot": 1,
      "original_hook": "...",
      "optimized_hook": "...",
      "expected_lift": "..."
    }}
  ],
  "price_framing": [
    {{
      "product": "...",
      "value_stack_frame": "...",
      "comparison_anchor": "...",
      "transformation_roi": "...",
      "recommended_frame": "value_stack|comparison|transformation",
      "copy_example": "..."
    }}
  ],
  "social_proof_plan": {{
    "testimonial_request_template": "...",
    "transformation_prompt": "...",
    "placement_by_platform": {{
      "tiktok": "...", "instagram": "...", "pinterest": "...", "facebook": "..."
    }}
  }},
  "checkout_friction": [
    {{
      "platform": "...",
      "current_steps": 0,
      "friction_points": ["..."],
      "optimization": "..."
    }}
  ],
  "ab_tests_today": [
    {{
      "test_name": "...",
      "platform": "...",
      "what_to_test": "...",
      "how_to_measure": "...",
      "success_criteria": "...",
      "duration": "..."
    }}
  ],
  "top_conversion_wins": ["...", "...", "..."]
}}
```"""

        response = self.call_claude(SYSTEM, prompt)
        conversion = self.extract_json(response)

        output_path = self.save_output(
            conversion, "conversion", self.filename("conversion")
        )
        print(f"[Stage 8] Conversion optimization plan saved → {output_path}")
        return output_path

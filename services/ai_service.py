import html
import logging
import re

from openai import OpenAI

from config import Config
from prompts import (
    ASTRO_PROMPT,
    SIMPLIFY_PROMPT,
    TRANSIT_PROMPT,
    prompt_when,
    safe_prompt_value,
)

logger = logging.getLogger(__name__)


class AIConfigError(RuntimeError):
    """Raised when an AI feature is used but no API key is configured."""


class AIService:
    """Handles AI API interactions (OpenAI-compatible, e.g. Agnes AI)."""

    def __init__(self):
        self._client = None

    @staticmethod
    def is_configured():
        """True when an API key is available for AI features."""
        return Config.is_ai_configured()

    @property
    def client(self):
        """Lazily build the OpenAI-compatible client.

        The client is only created when a key is present, so the app can boot
        (and serve the core Swiss Ephemeris flow) without any AI credentials.
        """
        if not self.is_configured():
            raise AIConfigError(
                "کلید API تنظیم نشده است. یک کلید رایگان از https://platform.agnes-ai.com/ "
                "بگیرید و در متغیر محیطی API_KEY قرار دهید."
            )
        if self._client is None:
            self._client = OpenAI(base_url=Config.API_URL, api_key=Config.API_KEY)
        return self._client

    def generate_analysis(self, prompt, model=None):
        """Generate an AI analysis for the given prompt."""
        if model is None:
            model = Config.ASTRO_MODEL

        try:
            logger.info(f"Calling AI (model={model}, base_url={Config.API_URL}), prompt={len(prompt)} chars")
            completion = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                timeout=600,
            )
            result = completion.choices[0].message.content
            logger.info(f"AI response received. Length: {len(result or '')} characters")
            return (result or "").strip()
        except AIConfigError:
            raise
        except Exception as e:
            logger.error(f"AI API error: {e}")
            raise RuntimeError(f"خطا در ارتباط با هوش مصنوعی: {str(e)}")

    def analyze_birth_chart(self, astro_data, vision="", name="", date="", time="", place=""):
        """Build the house-by-house birth-chart prompt and generate the analysis."""
        from core.interpretation_guide import render_interpretation_guide_for_prompt

        prompt = ASTRO_PROMPT.format(
            name=safe_prompt_value(name or "مخاطب"),
            when=safe_prompt_value(prompt_when(date, time, place)),
            astro_data=safe_prompt_value(astro_data),
            vision=safe_prompt_value(vision) if vision else "تحلیل جامع زایچه، خانه به خانه",
            interpretation_guide=render_interpretation_guide_for_prompt(),
        )
        return self.generate_analysis(prompt, model=Config.ASTRO_MODEL)

    def analyze_transit(self, transit_data, vision="", name="", date="", time="", place=""):
        """Build the house-by-house transit prompt and generate the analysis."""
        from core.interpretation_guide import render_interpretation_guide_for_prompt

        prompt = TRANSIT_PROMPT.format(
            name=safe_prompt_value(name or "مخاطب"),
            when=safe_prompt_value(prompt_when(date, time, place)),
            transit_data=safe_prompt_value(transit_data),
            vision=safe_prompt_value(vision) if vision else "تحلیل ترانزیت لحظه، خانه به خانه",
            interpretation_guide=render_interpretation_guide_for_prompt(),
        )
        return self.generate_analysis(prompt, model=Config.ASTRO_MODEL)

    def simplify_text(self, text):
        """Simplify an astrological analysis while keeping house-by-house structure."""
        prompt = SIMPLIFY_PROMPT.format(text=safe_prompt_value(text))
        return self.generate_analysis(prompt, model=Config.SIMPLIFY_MODEL)


_HOUSE_HEADER_RE = re.compile(
    r'^(خانه[ٔه]?\s*[۰-۹0-9]{1,2}\b|بخش[‌\s])'
)


def format_analysis_html(text):
    """Convert plain-text AI analysis into safe, styled HTML.

    - Escapes all HTML (model output is treated as untrusted text).
    - Lines made of box-drawing separators become <hr>.
    - Section headers (lines starting with «بخش» or «خانه N») become <h3>.
    - Blank lines split paragraphs; single newlines become <br>.
    """
    if not text:
        return ""

    raw_lines = text.replace("\r\n", "\n").split("\n")
    blocks = []
    buffer = []

    def flush():
        if buffer:
            para = "<br>".join(html.escape(line) for line in buffer)
            blocks.append(f"<p>{para}</p>")
            buffer.clear()

    sep_re = re.compile(r'^[\s━─—=_*·•\-]{3,}$')
    for line in raw_lines:
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if sep_re.match(stripped):
            flush()
            blocks.append("<hr>")
            continue
        if _HOUSE_HEADER_RE.match(stripped):
            flush()
            blocks.append(f"<h3>{html.escape(stripped)}</h3>")
            continue
        buffer.append(stripped)

    flush()
    return "\n".join(blocks)

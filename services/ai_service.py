import html
import logging
import re

from openai import OpenAI

from config import Config
from database import get_ai_settings
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

    @staticmethod
    def settings():
        saved = get_ai_settings()
        api_key = (saved.get('api_key') or Config.API_KEY).strip()
        model = saved.get('model')
        return {
            'api_key': '' if api_key.lower() == 'your_api_key_here' else api_key,
            'base_url': saved.get('base_url', Config.API_URL),
            'model': model or Config.ASTRO_MODEL,
            'simplify_model': model or Config.SIMPLIFY_MODEL,
        }

    @staticmethod
    def is_configured():
        return bool(AIService.settings()['api_key'])

    def generate_analysis(self, prompt, *, system_prompt=None, temperature=0.7, simplify=False):
        """Use one snapshot of the active provider settings for the whole request."""
        settings = self.settings()
        if not settings['api_key']:
            raise AIConfigError("کلید API را در منوی تنظیمات وارد کنید.")
        model = settings['simplify_model' if simplify else 'model']
        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})

        try:
            with OpenAI(base_url=settings['base_url'], api_key=settings['api_key']) as client:
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    timeout=600,
                )
            return (completion.choices[0].message.content or "").strip()
        except Exception as exc:
            logger.warning("AI API error (%s, status=%s)", type(exc).__name__, getattr(exc, 'status_code', None))
            raise RuntimeError("ارتباط با سرویس هوش مصنوعی ناموفق بود. آدرس، نام مدل و کلید API را در تنظیمات بررسی کنید.") from None

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
        return self.generate_analysis(prompt)

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
        return self.generate_analysis(prompt)

    def simplify_text(self, text):
        """Simplify an astrological analysis while keeping house-by-house structure."""
        prompt = SIMPLIFY_PROMPT.format(text=safe_prompt_value(text))
        return self.generate_analysis(prompt, simplify=True)


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

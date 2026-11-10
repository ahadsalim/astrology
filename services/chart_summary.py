"""Generate printable reports with the original natal and solar analysis prompt."""

from utils.text_formatter import format_chart_for_ai


# Headings for saved reports produced before restoring the original prompt.
SUMMARY_SECTIONS = (
    ('overview', 'مبانی و وضعیت کلی زایچه'),
    ('planets', 'کواکب و قرائن قوت و ضعف'),
    ('nodes', 'عقده‌های قمری و درجات ودایی'),
    ('aspects', 'اتصالات به نظر و به محل'),
    ('solar', 'بازگشت خورشید'),
    ('conclusion', 'برآیند قرائن و موارد نیازمند احتیاط'),
)


def generate_chart_summary(ai_service, chart: dict) -> dict:
    birth = chart['birth']
    analysis = ai_service.analyze_birth_chart(
        format_chart_for_ai(chart['natal'], birth, chart['solar']),
        vision=birth.get('vision') or '',
        name=birth['name'],
        date=birth['jalali_date'],
        time=birth['local_time'],
        place=birth['city_name'],
    )
    if not analysis.strip():
        raise ValueError('Empty chart analysis')
    return {'analysis': analysis}

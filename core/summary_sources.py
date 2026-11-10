"""Page-indexed reference excerpts for the three supplied handouts."""

import html
import re

from core.course_interpretation import get_full_course_placement
from core.interpretation_guide import HOUSE_TRIPLICITY_TOPICS
from core.soltani_interpretation import SOLTANI_HOUSES, SOLTANI_HOUSE_STATES, SOLTANI_PLANETS, SOLTANI_TOPICS

INTRO = 'جزوهٔ دورهٔ مقدماتی'
ADVANCED = 'جزوهٔ دورهٔ تکمیلی'
SOLTANI = 'جزوهٔ استاد سلطانی'

INTRO_REFERENCES = {
    'M1': ('۳۳–۴۷، ۵۹–۶۷', 'خوانش اصلی در دوره اعتدالی است. برج تقسیم دایرةالبروج است و خانه به افق، زمان و مکان وابسته است. پلاسیدیوس روش منتخب برای این خوانش است. نظام نجمی در موارد مشخص به‌صورت مکمل استفاده می‌شود.'),
    'M2': ('۴۷–۵۸، ۸۰–۸۱', 'ابتدای هر خانه حاکم آن را تعیین می‌کند. در خانهٔ خالی به برج و حاکم آن توجه کنید. خانه‌های ۱، ۴، ۷ و ۱۰ اوتادند و ۶ و ۱۲ بیت ادبار. خانهٔ ۳ با آموزش و ارتباط و سفر نزدیک و ۹ با معرفت، باور و سفر دور پیوند دارد. خانهٔ ۵ خلاقیت و لذت شخصی و ۱۱ دوستی و کار جمعی است.'),
    'M3': ('۶۷–۷۱', 'سروری در برج خود و وبال در برج مقابل آن است. شرف و هبوطِ درجه‌ای از شرف و هبوطِ برجی جدا هستند و درجهٔ هبوط مقابل درجهٔ شرف قرار دارد. درجهٔ شرف از سروری قوی‌تر و درجهٔ هبوط از وبال ضعیف‌تر است. اختلاف مکاتب در تعیین درجات را در نظر بگیرید.'),
    'M4': ('۷۲–۸۱', 'منسوبات: ماه احساس و مراقبت؛ عطارد عقل، کلام و ارتباط؛ زهره عاطفه و هنر؛ شمس اراده و مدیریت؛ مریخ اقدام و شجاعت؛ مشتری اقبال و اعتقاد؛ زحل صبر، نظم و محدودیت. کیفیت بروز را با قوت و ضعف بخوانید. در درس، شدت‌افزایی رأس و ذنب و دیدگاه متفاوت سنت ایرانی دربارهٔ ذنب جداگانه آمده‌اند.'),
    'M5': ('۹۰–۱۰۳', 'مقارنه، تسدیس، تربیع، تثلیث و مقابله پنج نظر اصلی‌اند. فاعل سریع‌تر، قابل کندتر است. نزدیکی، فاز و حال دو طرف اهمیت دارند. اتفاق قوت تقارن نسبت به حمل–میزان و اتفاق طریقت نسبت به سرطان–جدی است. جزوه اتصال به محل را با تقارن دقیق تعریف می‌کند.'),
    'M6': ('۱۰۴–۱۱۵', 'تصمیم نزدیکی بسیار زیاد به شمس، احتراق ضعف شدید و تحت‌الشعاع ضعف ملایم‌تر است. تشریق علوی و تغریب سفلی بسته به کوکب متفاوت‌اند. رجعت، اقامت و استقامت را از کرامت جدا بخوانید. ضعف حاکم خانه قرینه‌ای است که با حضور و نظر دیگر کواکب سنجیده می‌شود.'),
    'M7': ('۱۱۶–۱۳۰', 'ارباب اول و دوم مثلثه با روز و شب جابه‌جا می‌شوند و شریک جایگاه جدا دارد. حد تقسیم نامساوی برج و وجه بخش ده‌درجه‌ای است. وضع صاحب هر حظ اهمیت دارد. جزوه در ترتیب حد و مثلثه اختلاف نقل می‌کند و اتکا به وجه را در کنار قرائن دیگر می‌داند.'),
    'M8': ('۱۳۱–۱۳۹، ۱۴۱، ۱۶۱–۱۶۸', 'وارگوتاما برابری برج راشی و نه‌بهر است؛ پوشکار جایگاه مساعد نه‌بهر، آشتامشا نسبت هشتم و گاندانتا ناحیهٔ مرزی آب و آتش است. این موارد در نجمی بررسی می‌شوند و مکمل خوانش اعتدالی‌اند. مستولی با چند حظ همان درجه سنجیده می‌شود. برای سهام به برج، خانه، حاکم و اتصالات نگاه می‌شود.'),
}


def build_summary_references(natal: dict) -> dict:
    references = {
        key: {'source': INTRO, 'pages': pages, 'text': text}
        for key, (pages, text) in INTRO_REFERENCES.items()
    }
    references['M9'] = {
        'source': INTRO, 'pages': '۱۲۰–۱۲۲',
        'text': HOUSE_TRIPLICITY_TOPICS,
    }
    references['S1'] = {
        'source': SOLTANI, 'pages': '۵۱–۵۸',
        'text': {
            'خانه‌ها': SOLTANI_HOUSES,
            'ترتیب قوت از قوی به ضعیف': [1, 10, 7, 4, 11, 5, 9, 3, 2, 8, 12, 6],
            'خانه‌های خاص کوکب': {
                name: dict(zip(SOLTANI_HOUSE_STATES, houses))
                for name, (_, _, houses) in SOLTANI_PLANETS.items()
            },
        },
    }
    references['S2'] = {
        'source': SOLTANI, 'pages': '۶۳–۶۷، ۱۳۳–۱۳۴',
        'text': {
            'منسوبات و طبع': {name: [role, temperament] for name, (role, temperament, _) in SOLTANI_PLANETS.items()},
            'عقده‌ها': 'در روایت سلطانی رأس صفت کوکب را افزایش می‌دهد و ذنب از آن می‌کاهد.',
        },
    }
    for key, (section, indexes) in {
        'S3': (2, (0, 1, 2, 3, 4, 7)),
        'S4': (4, (0, 1)),
        'S5': (4, (3,)),
    }.items():
        topics = SOLTANI_TOPICS[section][1]
        references[key] = {
            'source': SOLTANI, 'pages': '، '.join(topics[index][1] for index in indexes),
            'text': [topics[index][2] for index in indexes],
        }
    for planet, point in natal.get('planets', {}).items():
        if not point or not isinstance(point.get('house'), int):
            continue
        house = point['house']
        excerpt = get_full_course_placement(planet, house)
        if excerpt:
            # The placement HTML is generated from the tagged PDF. Keep line boundaries.
            text = re.sub(r'</(?:h4|p|li)>', '\n', excerpt['html'])
            text = html.unescape(re.sub(r'<[^>]+>', '', text))
            first, last = excerpt['pages']
            references[f'T-{planet}-{house}'] = {
                'source': ADVANCED, 'pages': str(first) if first == last else f'{first}–{last}',
                'text': excerpt['title'] + '\n' + text,
            }
    return references

"""Consolidated interpretation reference for chart analysis."""

from __future__ import annotations

from core.sign_qualities import SIGN_CHARACTER_FA

# --- Houses: classical themes + modern notes (merged legacy references) ---
HOUSE_INTERPRETATIONS = [
    {
        'house': 1,
        'title': 'طالع / شخصیت',
        'themes': 'روان، زندگی، عمر، تربیت، زمین‌زادن، دوران کودکی',
        'negative': '—',
    },
    {
        'house': 2,
        'title': 'اموال و معیشت',
        'themes': 'غذا، معیشت، مال، کسب، صنعت، یاران',
        'negative': 'منحوس: آفت در چشم؛ ارتباط با مسائل فرزندان (خانه ۵)',
    },
    {
        'house': 3,
        'title': 'ارتباطات نزدیک',
        'themes': 'برادران، خواهران، خویشان، دوستان، سفر نزدیک، خواب، دانش دینی',
        'negative': '—',
    },
    {
        'house': 4,
        'title': 'خانواده و ریشه',
        'themes': 'پدر، نیاکان، عاقبت کار، عقار، خانه، آب، اصل‌ونسب، میراث پس از مرگ',
        'negative': '—',
    },
    {
        'house': 5,
        'title': 'خلاقیت و فرزند',
        'themes': 'فرزندان، دوستان، شادی، ذخیره، مال پدران، یادگاری پس از مرگ',
        'negative': '—',
    },
    {
        'house': 6,
        'title': 'سلامت و خدمت',
        'themes': 'خدمتکاران، اسب، اندام‌های باطن، بیماری، عیب‌ها',
        'negative': 'منحوس: نقص یا آسیب در پا',
    },
    {
        'house': 7,
        'title': 'همسر و شراکت',
        'themes': 'ازدواج، زنان، سریتان، خصومت، شراکت، خرید و فروش',
        'negative': 'جنگ، خصومت، پرخاش',
    },
    {
        'house': 8,
        'title': 'مرگ و تحول',
        'themes': 'مرگ، میراث، مال زنان، نفقه، درویشی، حاجت',
        'negative': 'زهر، تباهی تن، حیله، نیازمندی',
    },
    {
        'house': 9,
        'title': 'سفر و باور',
        'themes': 'سفر دور، غربت، دین، عبادت، وفا، نجوم، فلسفه، ایمان، خواب‌دیدن',
        'negative': '—',
    },
    {
        'house': 10,
        'title': 'جایگاه اجتماعی',
        'themes': 'ریاست، نام، مادر، پدر (سخت‌دلی)، تجارت، پیشه، فرزندان نیک، شهرت',
        'negative': '—',
    },
    {
        'house': 11,
        'title': 'امید و جمع',
        'themes': 'امید، سعادت، دوستان، کارهای خیر، عشق، زینت، تجارت، عمارت',
        'negative': 'دشمنان (در کنار دوستان)',
    },
    {
        'house': 12,
        'title': 'غربت و پنهان',
        'themes': 'دشمن پنهان، زندان، غربت، مهاجرت، بیماری، خدمت، سپاه',
        'negative': 'بدبختی، اندوه، ترس، محنت، آنچه مادر پیش از زادن دیده',
    },
]

# --- Planets: huquq (positive / negative) + keyword ---
PLANET_INTERPRETATIONS = [
    {
        'name': 'قمر',
        'symbol': '☽',
        'role': 'احساسات، روان، ناخودآگاه',
        'positive': 'شهود، الهام، مراقبت، تخیل، انعطاف، محبوبیت، صلح‌طلبی، آرامش، حافظه (با زحل/عطارد)',
        'negative': 'بی‌ثباتی، دمدمی‌مزاجی، زودرنجی، وابستگی عاطفی، ترس مبهم، رخوت، آشفتگی ذهنی، آسیب‌پذیری اجتماعی',
        'note': 'ماه کامل: هیجان بیشتر؛ لجبازی با مریخ آسیب‌دیده',
    },
    {
        'name': 'عطارد',
        'symbol': '☿',
        'role': 'عقل، تفکر، ارتباط',
        'positive': 'تیزهوشی، علم‌آموزی، تحلیل، سخنوری، کنجکاوی، خوش‌اخلاقی، خوش‌گمانی',
        'negative': 'پرحرفی، عصبیت، وسواس (با ماه)، خبرچینی، دروغ، نیرنگ، اختلال گفتار/نوشتار',
        'note': 'خنثی: با سعد سعد، با نحس نحس؛ قوی = انتقال مطلب بالا',
    },
    {
        'name': 'زهره',
        'symbol': '♀',
        'role': 'عشق، عاطفه، زیبایی، هنر',
        'positive': 'مهربانی، رمانتیسم، شوخ‌طبعی، هنر، جذابیت، خوش‌مشربی، زیبایی، محبوبیت',
        'negative': 'زودرنج عاطفی، شکنندگی، شکست عشقی، نارضایتی جنسی، ابتذال',
        'note': 'سعد اصغر؛ آسیب‌دیده: حافظه رنج',
    },
    {
        'name': 'شمس',
        'symbol': '☉',
        'role': 'هویت، مدیریت، اراده',
        'positive': 'رهبری، اراده، انرژی، بلندهمتی، عزت‌نفس، استقلال، انضباط',
        'negative': 'خودرأیی، استبداد، غرور، خودبینی، جاه‌طلبی بیمارگونه، تشنگی قدرت',
        'note': 'در خانه ۲ آسیب‌دیده: حرص مال؛ مثبت در ۲: ذهنیات مالی قوی',
    },
    {
        'name': 'مریخ',
        'symbol': '♂',
        'role': 'انرژی، اقدام، شجاعت',
        'positive': 'انگیزه، شجاعت، ریسک‌پذیری، اعتماد‌به‌نفس، اراده، پشتکار، قدرت بدنی، رقابت',
        'negative': 'عجولی، پرخاشگری، خشونت، نزاع، بی‌احتیاطی، لجبازی، گستاخی، انتقام',
        'note': 'نحس اصغر؛ با عطارد آسیب‌دیده: مردم‌آزاری',
    },
    {
        'name': 'مشتری',
        'symbol': '♃',
        'role': 'اقبال، اخلاق، اعتقاد',
        'positive': 'خوش‌اخلاقی، شادی، بلندهمتی، بخشندگی، صداقت، وفاداری، عدالت، ادب',
        'negative': 'ولخرجی، خوش‌بینی افراطی، ساده‌لوحی، پرحرفی، غلو، کم‌تعهدی',
        'note': 'سعد اکبر؛ کوکب اعتقادات و اخلاق',
    },
    {
        'name': 'زحل',
        'symbol': '♄',
        'role': 'قانون، ساختار، عمق',
        'positive': 'صبر، زهد، رازداری، سخت‌کوشی، تمرکز، حافظه، عمق فکر، انضباط، ایمان',
        'negative': 'جهل، حسادت، بخل، سردی، تنبلی، پرخوابی، انزوا، افسردگی، فوبیا، نگرانی',
        'note': 'نحس اکبر؛ با عطارد ضعیف می‌تواند حکیمی بسازد',
    },
    {
        'name': 'اورانوس',
        'symbol': '♅',
        'role': 'نوآوری، فناوری، استقلال',
        'positive': 'خلاقیت، تکنولوژی، نوآوری، آزاداندیشی',
        'negative': 'ناپایداری، شورش، قطع ناگهانی',
        'note': 'حاکم مدرن دلو',
    },
    {
        'name': 'نپتون',
        'symbol': '♆',
        'role': 'روح، معنویت درونی، آرامش',
        'positive': 'معنویت غیراعتقادی، آرامش عمیق، الهام باطنی',
        'negative': 'گیجی، فریب، فرار از واقعیت، وابستگی',
        'note': 'حاکم مدرن حوت',
    },
    {
        'name': 'پلوتو',
        'symbol': '♇',
        'role': 'تحول، قدرت، مرگ و نوزایی',
        'positive': 'دگرگونی عمیق، بازسازی، قدرت تحول‌آفرینی',
        'negative': 'وسواس قدرت، ویرانی، کنترل افراطی',
        'note': 'حاکم مدرن عقرب',
    },
]

# --- Signs: merged SIGN_CHARACTER + sign-in-house references ---
SIGN_INTERPRETATIONS = [
    {
        'sign': 'حمل',
        'symbol': '♈',
        'ruler': 'مریخ',
        'element': 'آتش',
        'trait': SIGN_CHARACTER_FA['حمل'],
        'positive': 'جسارت، عمل‌گرایی، پرتحرکی، جاه‌طلبی',
        'negative': 'تندخویی، عجولی، خودمحوری',
    },
    {
        'sign': 'ثور',
        'symbol': '♉',
        'ruler': 'زهره',
        'element': 'خاک',
        'trait': SIGN_CHARACTER_FA['ثور'],
        'positive': 'ثبات، هنر، علاقه مالی، حس عملی',
        'negative': 'سرسختی، وابستگی به مال',
    },
    {
        'sign': 'جوزا',
        'symbol': '♊',
        'ruler': 'عطارد',
        'element': 'باد',
        'trait': SIGN_CHARACTER_FA['جوزا'],
        'positive': 'فکر، ارتباط، یادگیری، رسانه',
        'negative': 'پراکندگی، نوسان، سطحی‌نگری',
    },
    {
        'sign': 'سرطان',
        'symbol': '♋',
        'ruler': 'قمر',
        'element': 'آب',
        'trait': SIGN_CHARACTER_FA['سرطان'],
        'positive': 'مهربانی، حس مادری، وفاداری عاطفی',
        'negative': 'دمدمی‌مزاجی، وابستگی، حساسیت افراطی',
    },
    {
        'sign': 'اسد',
        'symbol': '♌',
        'ruler': 'شمس',
        'element': 'آتش',
        'trait': SIGN_CHARACTER_FA['اسد'],
        'positive': 'رهبری، مدیریت، جوانمردی، درخشندگی',
        'negative': 'خودنمایی، غرور، نیاز به توجه',
    },
    {
        'sign': 'سنبله',
        'symbol': '♍',
        'ruler': 'عطارد',
        'element': 'خاک',
        'trait': SIGN_CHARACTER_FA['سنبله'],
        'positive': 'عملیات، اجرا، دقت، خدمت',
        'negative': 'انتقاد افراطی، وسواس جزئیات',
    },
    {
        'sign': 'میزان',
        'symbol': '♎',
        'ruler': 'زهره',
        'element': 'باد',
        'trait': SIGN_CHARACTER_FA['میزان'],
        'positive': 'تعادل، ظرافت، عشق‌ورزی، دیپلماسی',
        'negative': 'بی‌ثباتی در تصمیم، وابستگی به تأیید دیگران',
    },
    {
        'sign': 'عقرب',
        'symbol': '♏',
        'ruler': 'مریخ / پلوتو',
        'element': 'آب',
        'trait': SIGN_CHARACTER_FA['عقرب'],
        'positive': 'عمق احساس، وفاداری گزینشی، تحول',
        'negative': 'کینه، حساسیت نیش‌دار، پنهان‌کاری',
    },
    {
        'sign': 'قوس',
        'symbol': '♐',
        'ruler': 'مشتری',
        'element': 'آتش',
        'trait': SIGN_CHARACTER_FA['قوس'],
        'positive': 'علم‌دوستی، اخلاق، گشودگی، سفر',
        'negative': 'افراط و تفریط، پرحرفی فلسفی',
    },
    {
        'sign': 'جدی',
        'symbol': '♑',
        'ruler': 'زحل',
        'element': 'خاک',
        'trait': SIGN_CHARACTER_FA['جدی'],
        'positive': 'مسئولیت، سخت‌کوشی، استقامت',
        'negative': 'سردی، سخت‌گیری، بدبینی',
    },
    {
        'sign': 'دلو',
        'symbol': '♒',
        'ruler': 'زحل / اورانوس',
        'element': 'باد',
        'trait': SIGN_CHARACTER_FA['دلو'],
        'positive': 'استقلال، نوآوری، فناوری، آزاداندیشی',
        'negative': 'دوری عاطفی، سرکشی، غیرعملی بودن',
    },
    {
        'sign': 'حوت',
        'symbol': '♓',
        'ruler': 'مشتری / نپتون',
        'element': 'آب',
        'trait': SIGN_CHARACTER_FA['حوت'],
        'positive': 'معنویت، همدلی، تخیل، بخشش',
        'negative': 'فرار از واقعیت، سردرگمی مرزی',
    },
]

# --- Lunar nodes ---
NODE_INTERPRETATIONS = {
    'rule': (
        'رأس و ذنب ذاتاً سعد یا نحس نیستند؛ خاصیت اصلی آن‌ها «شدت‌افزایی» است. '
        'ویژگی‌های کوکب یا خانهٔ محل قرارگیری را پررنگ یا تحت تأثیر قرار می‌دهند. '
        'در سنت ایرانی: رأس نحس نیست؛ ذنب نحس است.'
    ),
    'north_conjunctions': [
        ('شمس', 'مدیریت و ارادهٔ پررنگ؛ خطر غرور افراطی'),
        ('قمر', 'احساسات و مهربانی شدید؛ حساسیت روانی بالا'),
        ('عطارد', 'فکر و ایده‌پردازی فعال؛ قلم یا گفتار پرانرژی'),
        ('زهره', 'اولویت عاطفی؛ پتانسیل هنری'),
        ('مشتری', 'اقبال و اهمیت اعتقاد و علم‌آموزی'),
        ('زحل', 'ضابطه‌مندی و سخت‌گیری شدید'),
        ('مریخ', 'انرژی و اقدام شدید؛ پرخاشگری احتمالی'),
    ],
    'south_theme': 'تضعیف، سستی، از دست رفتن، فضاهای تاریک؛ با کواکب نحس، صفات مثبت آن کوکب را تضعیف می‌کند.',
    'house_placements': [
        ('ذنب در خانه ۱', 'تضعیف جسمانی، کم‌ارزشی، تضاد با رأس–شمس (ظاهر عزتمند / درون ضعیف)'),
        ('رأس در خانه ۲', 'اضطراب مالی شدید؛ اهمیت کسب‌وکار حتی برای غیرمادی‌ها'),
        ('ذنب در خانه ۷', 'سستی ازدواج؛ دشواری همسر یا خطر جدایی (قابل آگاهی و پیشگیری)'),
    ],
}

# --- Major aspects (traditional references) ---
ASPECT_MAJOR = [
    {
        'name': 'اقتران (قران)',
        'angle': '۰°',
        'nature': 'متغیر (با سعد سعد، با نحس نحس)',
        'power': '۱۰۰٪',
        'note': 'احتراق با شمس؛ مجاسده با گره؛ اجتماع شمس–قمر؛ اختفا = هم‌طول و هم‌عرض',
    },
    {
        'name': 'مقابله',
        'angle': '۱۸۰°',
        'nature': 'نحس',
        'power': '۵۰٪',
        'note': 'دو کوکب در دو سر قطر دایرهٔ بروج',
    },
    {
        'name': 'تثلیث',
        'angle': '۱۲۰°',
        'nature': 'سعد (نیم‌دوستی؛ طبع زهره‌ای)',
        'power': '۳۳٪',
        'note': 'ایمن = هم‌سو با توالی برج؛ ایسر = خلاف توالی',
    },
    {
        'name': 'تربیع',
        'angle': '۹۰°',
        'nature': 'نحس (دشمنی؛ طبع مریخی)',
        'power': '۲۵٪',
        'note': 'تربیع مریخ اغلب از تثلیث مریخ قوی‌تر',
    },
    {
        'name': 'تسدیس',
        'angle': '۶۰°',
        'nature': 'سعد',
        'power': '۱۶٪',
        'note': 'ایمن/ایسر مانند تثلیث و تربیع',
    },
]

ASPECT_RULES = [
    'سریع‌رو به کندرو اتصال می‌دهد: فاعل = سریع‌تر، قابل = کندتر (ماه → عطارد → زهره → شمس → مریخ → مشتری → زحل).',
    'حد اتصال: معمولاً «نصف مجموع نصف جرم» دو کوکب؛ سه فاز نزدیک‌شدن (بدايت، وساطت، حاقّ) و سه فاز دورشدن (انصراف).',
    'ایمن (Friendly): تسدیس/تربیع/تثلیث هم‌سو با توالی برج؛ ایسر (Left-handed): خلاف توالی.',
    'درصد قدرت نظر تقریبی است و با طبیعت کوکب‌ها تعدیل می‌شود (مثلاً تثلیث مشتری قوی‌تر از مقابلهٔ مشتری).',
    'در زایچهٔ تولد: اتصالات با کرامت و حاکمیت خانه‌ها جمع‌بندی شوند؛ در سؤال و اختیار دقت فاز اتصال حیاتی‌تر است.',
]

ASPECT_RECEPTION = [
    ('مقبول — دفع قوت', 'قابل قوی و غیرمحترق؛ نظر را می‌پذیرد و به فاعل قوت می‌دهد'),
    ('مقبول — دفع طبیعت', 'قابل در سروری، شرف یا درجهٔ شرف'),
    ('نامقبول — رد', 'قابل محترق، راجعه، محوس یا آسیب‌ذاتی؛ نظر می‌رسد ولی پذیرفته نمی‌شود'),
    ('نامقبول — انکار', 'قابل در وبال، هبوط، حدّ دشمن یا برج مخالف طبع؛ نظر منکر است'),
]

ASPECT_SECONDARY = [
    ('نقل نور', 'سریع‌رو قبل از انفصال از بطیء، با سومی اتصال دهد → نور بطیء را منتقل می‌کند'),
    ('جمع نور', 'سریع‌رو نور دو بطیء را جمع و هم‌جهت می‌کند'),
    ('منع نور', 'کوکب ثالث بین فاعل و قابل → اتصال مستقیم باطل'),
    ('قطع نور', 'بطیء قوی بین سریع و متوسط → قطع اتصال (نه فقط تضعیف)'),
    ('انتکاث / مرادفه', 'رجعت قبل از اتصال = انتکاث؛ رجعت که اتصال بسازد = مرادفه'),
]

# --- Sun relationship / combustion ---
SUN_RELATION_STATES = [
    ('تصمیم (صمیم)', 'تا ۱۶′ از مرکز شمس', 'اوج قدرت؛ یگانگی با خورشید (خلاف احتراق)'),
    ('احتراق', 'تا ۶° از شمس', 'ضعف شدید؛ «سوختن» کوکب'),
    ('تحت‌الشعاع', '۶° تا ۱۲° (مرزهای ویژه برای ماه/عطارد/زهره/مریخ/زحل)', 'ضعف با شدت کمتر'),
    ('تشریق / تغریب', '۱۲° تا ۳۰°', 'متغیر؛ علوی مشرقی یا سفلی مغربی = قوت'),
    ('ضعیف‌التشریق/التغریب', '۳۰° تا ۹۰°', 'قوت یا ضعف خفیف‌تر'),
]

SUN_SECT_RULES = [
    'علوی (زحل، مشتری، مریخ): تشریق = طلوع قبل از شمس (۱۵–۹۰°) → قوت.',
    'سفلی (زهره، عطارد، قمر): تغریب = غروب بعد از شمس → قوت.',
    'نحوست نیره: زحل یا مریخ کمتر از ۱۵° قبل از طلوع شمس → آسیب به خورشید.',
    'طریقه نیره: ۱۹° حمل تا ۳° ثور (قوت‌افزا)؛ طریقه محترقه: ۱۹° میزان تا ۳° عقرب (ضعف).',
    'تجمع احتراق چند کوکب: چالش‌های متعدد در حوزه‌های مربوطه.',
]

# --- Strength assessment ladder ---
STRENGTH_PARAMETERS = [
    ('۱. برج', 'سروری / شرف / هبوط / وبال (کرامت اساسی)'),
    ('۲. مثلثه', 'سازگاری کوکب با صاحب مثلثهٔ عنصر (روز/شب)'),
    ('۳. حد', 'کوکب در حد خودش قوت؛ در حد ناسازگار ضعف (مصری در تولد)'),
    ('۴. وجه', 'صاحب وجه و وضعیت او بر کوکب اثر می‌گذارد'),
    ('۵. نسبت با شمس', 'احتراق، تحت‌الشعاع، تشریق/تغریب، تصمیم'),
    ('۶. جلب / انحراف', 'جلب = موافق بخش روز/شب؛ حیّز = برج هم‌جنس؛ انحراف = برج مخالف جنسیت'),
    ('۷. رجعت', 'در احکام معمولاً ضعف؛ تأخیر، بازگشت، تکرار'),
    ('۸. اتصالات', 'مقبول/نامقبول؛ نظرات فرعی؛ اتصال دقیق (⭐) قوی‌تر'),
]

INTERPRETATION_PRINCIPLES = [
    'آسیب کوکب = آسیب خانه: حاکم خانهٔ ضعیف/محترق، آن خانه را آسیب‌پذیر می‌کند.',
    'مثال: خانه ۷ در ثور → حاکم زهره؛ زهره محترق → چالش در ازدواج (احتمال، نه حکم قطعی).',
    'حاکم طالع ضعیف → ضعف خانه ۱ (جسم، بنیه، ظاهر).',
    'نظرات سعد (مثلاً مشتری) می‌توانند ضعف را تعدیل کنند، نه بی‌اثر کنند.',
    'روش کار: حال کواکب → خانه‌ها → حاکمیت‌ها → جمع قرائن.',
]

# --- Triplicity lords per house ---
HOUSE_TRIPLICITY_TOPICS = [
    ('۱ طالع', 'حیات و سرشت اول عمر', 'حیات، کالبد، وسط عمر', 'عاقبت امر و پس از مرگ'),
    ('۲', 'مال و معاش', 'اعوان و انصار', 'همت، مروت، سخاوت'),
    ('۳', 'خویشاوندان بزرگ', 'خویشان متوسط', 'خویشاوندان کوچک‌تر'),
    ('۴', 'پدران', 'ضیاع و عقار', 'عاقبت کارها'),
    ('۵', 'حیات ولد', 'لذت و طرب', 'رسل، اخبار، هدایا'),
    ('۶', 'بیماری', 'ممالیک و خدمتکاران', 'حواشی و منافع'),
    ('۷', 'ازدواج و نکاح', 'دشمنان و رقیب', 'شراکت و مخاصمه'),
    ('۸', 'مرگ', 'خوف و خطر', 'مواریث'),
    ('۹', 'سفر و خیر/شر آن', 'عبادات', 'علم، رویا، تعبیر'),
    ('۱۰', 'ولایت و جاه', 'ثبات کار سلطانی', 'عمل، مادر، صناعت'),
    ('۱۱', 'امید بر آمدن کار', 'دوستان', 'سخاوت به دوستان'),
    ('۱۲', 'دشمنان', 'بدبختی و رنج', 'ستوران'),
]

TRIPLICITY_INTERPRETATION_NOTE = (
    'برای هر خانه: عنصرِ برجِ ابتدای خانه را بیابید؛ سه ارباب مثلثه (روز/شب/شریک) '
    'موضوعات سه ستون جدول را نشان می‌دهند. در چارت روزی: رب اول = حاکم روز؛ '
    'در چارت شبی: رب اول = حاکم شب. وضعیت هر رب در چارت، کیفیت آن بخش از خانه را می‌سنجد.'
)


def _guide_table(headers: list[str], rows: list[list[str]], *, table_class: str = '') -> str:
    cls = f'interp-guide-table {table_class}'.strip()
    head = ''.join(f'<th>{h}</th>' for h in headers)
    body = ''
    for row in rows:
        body += '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>'
    return f'<table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def render_interpretation_guide_html() -> str:
    """Full HTML body for the interpretation guide modal."""
    parts: list[str] = []

    parts.append('<p class="interp-guide-intro">')
    parts.append(
        'راهنمای فشردهٔ تفسیر خانه‌ها و کواکب و بروج<br>'
        'شامل عقده‌ها، اتصالات، احتراق/تشریق، و سنجش قوت.<br>'
        'هیچ نشانه‌ای به‌تنهایی کافی نیست؛ کرامت، خانه، حاکمیت و اتصالات را با هم ببینید.'
    )
    parts.append('</p>')

    parts.append('<h3 class="interp-guide-section">📐 قواعد کلی تفسیر</h3>')
    for rule in INTERPRETATION_PRINCIPLES:
        parts.append(f'<p class="interp-guide-note">• {rule}</p>')
    strength_rows = [[p[0], p[1]] for p in STRENGTH_PARAMETERS]
    parts.append(_guide_table(['لایه', 'کاربرد'], strength_rows, table_class='interp-strength'))

    parts.append('<h3 class="interp-guide-section">🏠 خانه‌ها</h3>')
    house_rows = [
        [str(h['house']), h['title'], h['themes'], h['negative']]
        for h in HOUSE_INTERPRETATIONS
    ]
    parts.append(_guide_table(['خانه', 'نام', 'موضوعات', 'منفی / هشدار'], house_rows, table_class='interp-houses'))

    parts.append('<h3 class="interp-guide-section">🪐 کواکب — حُظوظ (مثبت / منفی)</h3>')
    planet_rows = [
        [f"{p['symbol']} {p['name']}", p['role'], p['positive'], p['negative'], p.get('note', '—')]
        for p in PLANET_INTERPRETATIONS
    ]
    parts.append(_guide_table(['کوکب', 'نقش', 'مثبت', 'منفی', 'یادداشت'], planet_rows, table_class='interp-planets'))

    parts.append('<h3 class="interp-guide-section">♈ بروج</h3>')
    sign_rows = [
        [
            f"{s['symbol']} {s['sign']}",
            s['ruler'],
            s['element'],
            s['trait'],
            s['positive'],
            s['negative'],
        ]
        for s in SIGN_INTERPRETATIONS
    ]
    parts.append(
        _guide_table(
            ['برج', 'حاکم', 'عنصر', 'ویژگی', 'مثبت', 'منفی'],
            sign_rows,
            table_class='interp-signs',
        )
    )
    parts.append(
        '<p class="interp-guide-note">برج روی طالع یا کوکب در خانه، همان ویژگی‌ها را در شخصیت یا '
        'حوزهٔ زندگی پررنگ می‌کند.</p>'
    )

    parts.append('<h3 class="interp-guide-section">☊☋ عقده‌های قمری</h3>')
    parts.append(f'<p class="interp-guide-note">{NODE_INTERPRETATIONS["rule"]}</p>')
    parts.append('<h4 class="interp-guide-sub">مقارنه رأس با کواکب</h4>')
    node_rows = [[p[0], p[1]] for p in NODE_INTERPRETATIONS['north_conjunctions']]
    parts.append(_guide_table(['کوکب', 'اثر'], node_rows, table_class='interp-nodes'))
    parts.append(f'<p class="interp-guide-note"><strong>ذنب:</strong> {NODE_INTERPRETATIONS["south_theme"]}</p>')
    parts.append('<h4 class="interp-guide-sub">گره در خانه</h4>')
    node_house_rows = [[p[0], p[1]] for p in NODE_INTERPRETATIONS['house_placements']]
    parts.append(_guide_table(['قرارگیری', 'اثر'], node_house_rows, table_class='interp-node-houses'))

    parts.append('<h3 class="interp-guide-section">⚹ اتصالات اصلی (پنج زاویه)</h3>')
    aspect_rows = [
        [a['name'], a['angle'], a['nature'], a['power'], a['note']]
        for a in ASPECT_MAJOR
    ]
    parts.append(
        _guide_table(
            ['اتصال', 'زاویه', 'طبع', 'قدرت تقریبی', 'یادداشت'],
            aspect_rows,
            table_class='interp-aspects',
        )
    )
    for rule in ASPECT_RULES:
        parts.append(f'<p class="interp-guide-note">• {rule}</p>')

    parts.append('<h4 class="interp-guide-sub">پذیرش نظر (مقبول / نامقبول)</h4>')
    reception_rows = [[r[0], r[1]] for r in ASPECT_RECEPTION]
    parts.append(_guide_table(['نوع', 'معنی'], reception_rows, table_class='interp-reception'))

    parts.append('<h4 class="interp-guide-sub">نظرات فرعی (احکام ایرانی)</h4>')
    secondary_rows = [[r[0], r[1]] for r in ASPECT_SECONDARY]
    parts.append(_guide_table(['نام', 'اثر'], secondary_rows, table_class='interp-secondary'))

    parts.append('<h3 class="interp-guide-section">☉ نسبت کواکب با خورشید</h3>')
    sun_rows = [[r[0], r[1], r[2]] for r in SUN_RELATION_STATES]
    parts.append(_guide_table(['حالت', 'فاصله', 'اثر'], sun_rows, table_class='interp-sun'))
    for rule in SUN_SECT_RULES:
        parts.append(f'<p class="interp-guide-note">• {rule}</p>')

    parts.append('<h3 class="interp-guide-section">△ ارباب مثلثه و خانه‌ها</h3>')
    parts.append(f'<p class="interp-guide-note">{TRIPLICITY_INTERPRETATION_NOTE}</p>')
    tri_house_rows = [[r[0], r[1], r[2], r[3]] for r in HOUSE_TRIPLICITY_TOPICS]
    parts.append(
        _guide_table(
            ['خانه', 'رب اول مثلثه', 'رب دوم', 'رب سوم (شریک)'],
            tri_house_rows,
            table_class='interp-triplicity-houses',
        )
    )

    return '\n'.join(parts)


def render_interpretation_guide_for_prompt() -> str:
    """Compact plain-text interpretation reference appended to AI prompt."""
    lines: list[str] = []
    lines.append('─' * 60)
    lines.append('راهنمای تفسیر (مرجع تحلیل یکپارچه)')
    lines.append('─' * 60)
    lines.append(
        'هیچ نشانه‌ای به‌تنهایی کافی نیست؛ کرامت، خانه، حاکمیت، سکت و اتصالات را با هم ببینید.'
    )
    lines.append('')

    lines.append('【 قواعد کلی 】')
    for rule in INTERPRETATION_PRINCIPLES:
        lines.append(f'  • {rule}')
    lines.append('')

    lines.append('【 سنجش قوت 】')
    for name, desc in STRENGTH_PARAMETERS:
        lines.append(f'  - {name}: {desc}')
    lines.append('')

    lines.append('【 خانه‌ها 】')
    for h in HOUSE_INTERPRETATIONS:
        neg = h['negative'] if h['negative'] != '—' else ''
        line = f"  خانه {h['house']} ({h['title']}): {h['themes']}"
        if neg:
            line += f' | هشدار: {neg}'
        lines.append(line)
    lines.append('')

    lines.append('【 کواکب 】')
    for p in PLANET_INTERPRETATIONS:
        lines.append(
            f"  {p['name']} ({p['role']}): مثبت={p['positive']} | منفی={p['negative']}"
        )
    lines.append('')

    lines.append('【 اتصالات اصلی 】')
    for a in ASPECT_MAJOR:
        lines.append(
            f"  {a['name']} ({a['angle']}): طبع={a['nature']}، قدرت≈{a['power']} — {a['note']}"
        )
    for rule in ASPECT_RULES:
        lines.append(f'  • {rule}')
    lines.append('')

    lines.append('【 نسبت کواکب با شمس 】')
    for state, dist, effect in SUN_RELATION_STATES:
        lines.append(f'  {state} ({dist}): {effect}')
    for rule in SUN_SECT_RULES:
        lines.append(f'  • {rule}')
    lines.append('')

    lines.append('【 ارباب مثلثه و خانه‌ها 】')
    lines.append(f'  {TRIPLICITY_INTERPRETATION_NOTE}')
    lines.append('─' * 60)

    return '\n'.join(lines)

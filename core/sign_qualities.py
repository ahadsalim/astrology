"""Traditional tropical sign qualities: modality, gender, and diurnal sect."""

SIGN_SYMBOL = {
    'حمل': '♈',
    'ثور': '♉',
    'جوزا': '♊',
    'سرطان': '♋',
    'اسد': '♌',
    'سنبله': '♍',
    'میزان': '♎',
    'عقرب': '♏',
    'قوس': '♐',
    'جدی': '♑',
    'دلو': '♒',
    'حوت': '♓',
}


def get_sign_symbol(sign_fa: str) -> str:
    return SIGN_SYMBOL.get(sign_fa, '')


SIGN_MODALITY_FA = {
    'حمل': 'منقلب',
    'سرطان': 'منقلب',
    'میزان': 'منقلب',
    'جدی': 'منقلب',
    'ثور': 'ثابت',
    'اسد': 'ثابت',
    'عقرب': 'ثابت',
    'دلو': 'ثابت',
    'جوزا': 'زوجسدین',
    'سنبله': 'زوجسدین',
    'قوس': 'زوجسدین',
    'حوت': 'زوجسدین',
}

SIGN_MODALITY_TITLE = {
    'منقلب': 'آغازگر، پیشتاز، فعال',
    'ثابت': 'با ثبات، پابرجا، مقاوم',
    'زوجسدین': 'متغیر، منعطف، در حال تغییر و انتقال',
}

SIGN_GENDER_FA = {
    'حمل': 'مذکر',
    'جوزا': 'مذکر',
    'اسد': 'مذکر',
    'میزان': 'مذکر',
    'قوس': 'مذکر',
    'دلو': 'مذکر',
    'ثور': 'مونث',
    'سرطان': 'مونث',
    'سنبله': 'مونث',
    'عقرب': 'مونث',
    'جدی': 'مونث',
    'حوت': 'مونث',
}

SIGN_SECT_FA = {
    'حمل': 'روزی',
    'جوزا': 'روزی',
    'اسد': 'روزی',
    'میزان': 'روزی',
    'قوس': 'روزی',
    'دلو': 'روزی',
    'ثور': 'شبی',
    'سرطان': 'شبی',
    'سنبله': 'شبی',
    'عقرب': 'شبی',
    'جدی': 'شبی',
    'حوت': 'شبی',
}

SIGN_CHARACTER_FA = {
    'حمل': 'عمل‌گرایی',
    'ثور': 'مادیات – هنر – عاطفه',
    'جوزا': 'فکری – ارتباطی (نوسان‌گر)',
    'سرطان': 'احساسات',
    'اسد': 'مدیریت',
    'سنبله': 'علمی – عملیاتی',
    'میزان': 'عاطفه – ظرافت – تعادل',
    'عقرب': 'احساسات پیچیده – احساسات غریزی',
    'قوس': 'علم – اخلاق',
    'جدی': 'مسئولیت – سخت‌کوشی',
    'دلو': 'استقلال‌طلبی – آزاداندیشی – نوآوری',
    'حوت': 'معنویت – احساس',
}

SIGN_RULER_FA = {
    'حمل': 'مریخ',
    'ثور': 'زهره',
    'جوزا': 'عطارد',
    'سرطان': 'قمر',
    'اسد': 'شمس',
    'سنبله': 'عطارد',
    'میزان': 'زهره',
    'عقرب': 'مریخ',
    'قوس': 'مشتری',
    'جدی': 'زحل',
    'دلو': 'زحل',
    'حوت': 'مشتری',
}

SIGN_TRAIT_HEADERS_HTML = (
    '<th>حالت برج</th><th>جنسیت</th>'
)


def get_sign_character_fa(sign_fa: str) -> str:
    return SIGN_CHARACTER_FA.get(sign_fa, '—')


def get_sign_ruler_fa(sign_fa: str) -> str:
    return SIGN_RULER_FA.get(sign_fa, '—')


def format_sign_character_cell_html(sign_fa: str, *, extra_class: str = '') -> str:
    """Sign character/trait cell (houses table, after gender)."""
    if not sign_fa or sign_fa == '—':
        return '<td class="sign-character-cell">—</td>'
    css = f'sign-character-cell {extra_class}'.strip()
    return f'<td class="{css}">{get_sign_character_fa(sign_fa)}</td>'


def format_sign_ruler_cell_html(sign_fa: str) -> str:
    return f'<td class="sign-ruler-cell">{get_sign_ruler_fa(sign_fa)}</td>'


def format_sign_trait_cells_html(sign_fa: str, *, gender_extra_class: str = '') -> str:
    """Two table cells after tropical sign: modality and gender (colored by day/night sect)."""
    if not sign_fa or sign_fa == '—':
        return '<td>—</td><td>—</td>'

    modality = SIGN_MODALITY_FA.get(sign_fa, '—')
    gender = SIGN_GENDER_FA.get(sign_fa, '—')
    sect = SIGN_SECT_FA.get(sign_fa, '—')

    modality_title = SIGN_MODALITY_TITLE.get(modality, '')
    modality_attr = f' title="{modality_title}"' if modality_title else ''

    sect_class = ''
    if sect == 'روزی':
        sect_class = 'sign-sect-day'
    elif sect == 'شبی':
        sect_class = 'sign-sect-night'

    gender_class = f'sign-gender-cell {sect_class} {gender_extra_class}'.strip()
    return (
        f'<td class="sign-modality-cell"{modality_attr}>{modality}</td>'
        f'<td class="{gender_class}">{gender}</td>'
    )

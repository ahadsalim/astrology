"""Traditional house themes (Persian labels for natal chart cusps)."""

HOUSE_MEANINGS_FA = {
    1: 'شخصیت',
    2: 'اموال و منابع',
    3: 'ارتباطات عمومی',
    4: 'خلوت درون و فضاهای خانوادگی',
    5: 'خلاقیت، عشق و فرزندان',
    6: 'سلامت و محیط کار و روابط شغلی',
    7: 'شریک و ازدواج',
    8: 'حوادث و فضاهای متافیزیکی',
    9: 'باورها و سفرهای دور',
    10: 'حرفه و جایگاه اجتماعی',
    11: 'دوستان و آرمان‌ها',
    12: 'دشمن و گرفتاری و تنهایی',
}


def get_house_meaning_fa(house_number: int) -> str:
    return HOUSE_MEANINGS_FA.get(house_number, '—')


# Lower number = higher priority (1 = highest, 12 = lowest).
HOUSE_PRIORITY = {
    1: 1,
    2: 10,
    3: 8,
    4: 6,
    5: 5,
    6: 12,
    7: 4,
    8: 9,
    9: 7,
    10: 2,
    11: 3,
    12: 11,
}

HOUSE_NAME_PINK = {1, 2, 3, 7, 8, 9}


def format_house_number_cell_html(house_number: int) -> str:
    """House index cell: odd houses blue, even houses pink."""
    css_class = 'house-num-odd' if house_number % 2 == 1 else 'house-num-even'
    return f'<td class="house-num-cell {css_class}">{house_number}</td>'


def get_house_priority(house_number: int) -> int | str:
    return HOUSE_PRIORITY.get(house_number, '—')


def format_house_name_cell_html(house_number: int) -> str:
    """House theme cell: houses 1–3 and 7–9 pink, others blue."""
    css_class = 'house-name-pink' if house_number in HOUSE_NAME_PINK else 'house-name-blue'
    return f'<td class="house-name-cell {css_class}">{get_house_meaning_fa(house_number)}</td>'


def format_house_priority_cell_html(house_number: int) -> str:
    return (
        f'<td class="house-priority-cell houses-group-end">'
        f'{get_house_priority(house_number)}</td>'
    )


HOUSE_TABLE_HEADERS_HTML = (
    '<thead class="houses-table-head">'
    '<tr class="houses-head-row1">'
    '<th colspan="3" class="houses-head-group houses-head-group--house">خانه</th>'
    '<th colspan="6" class="houses-head-group houses-head-group--sign">برج</th>'
    '</tr>'
    '<tr class="houses-head-row2">'
    '<th class="houses-head-col">خانه</th>'
    '<th class="houses-head-col">نام</th>'
    '<th class="houses-head-col houses-head-col--group-end">اولویت</th>'
    '<th class="houses-head-col">درجه</th>'
    '<th class="houses-head-col">برج</th>'
    '<th class="houses-head-col">حاکم</th>'
    '<th class="houses-head-col">حالت برج</th>'
    '<th class="houses-head-col">جنسیت</th>'
    '<th class="houses-head-col houses-head-col--group-end">ویژگی برج</th>'
    '</tr>'
    '</thead><tbody class="houses-table-body">'
)

HOUSE_TABLE_FOOTER_HTML = '</tbody>'

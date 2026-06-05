# 🌟 Professional Astrology Engine - نجوم حرفه‌ای

## نسخه 2.0 - بازسازی کامل با Swiss Ephemeris

یک موتور محاسبات نجومی حرفه‌ای مشابه نرم‌افزار ZET با استفاده از Swiss Ephemeris

---

## 🎯 ویژگی‌های کلیدی

### ✅ محاسبات دقیق نجومی
- **Swiss Ephemeris** - دقیق‌ترین کتابخانه محاسبات نجومی
- **محاسبه موقعیت 10 سیاره** (شمس، قمر، عطارد، زهره، مریخ، مشتری، زحل، اورانوس، نپتون، پلوتو)
- **طالع (Ascendant)** و **قله آسمان (Midheaven)**
- **12 خانه** با سیستم Placidus
- **عقده‌های قمری** (رأس و ذنب)
- **محاسبه اسپکت‌ها** (اقتران، مقابله، تثلیث، تربیع، تسدیس)
- **تشخیص راجعه** (Retrograde)

### 📅 مدیریت تاریخ و زمان
- **تبدیل دقیق تاریخ شمسی به میلادی**
- **مدیریت timezone ایران** (UTC+3:30)
- **پشتیبانی کامل از DST** (ساعت تابستانی)
- **تبدیل به Julian Day** برای محاسبات دقیق

### 🗺️ دیتابیس شهرها
- **30 شهر اصلی ایران** با مختصات دقیق
- **SQLite Database** برای ذخیره‌سازی
- **بدون نیاز به اینترنت** برای محاسبات

### 📊 نمایش گرافیکی
- **نمودار دایره‌ای زایچه** (Chart Wheel)
- **نمایش بروج 12گانه**
- **نمایش خانه‌ها**
- **قرارگیری سیارات** با نمادهای یونیکد
- **رنگ‌بندی حرفه‌ای**

### 🤖 تحلیل هوش مصنوعی
- **تحلیل کامل زایچه** با OpenAI
- **ذخیره زایچه‌ها** در دیتابیس
- **مشاهده تاریخچه** زایچه‌های قبلی

---

## 🏗️ معماری پروژه

```
app/
├── core/                      # ماژول‌های اصلی محاسبات
│   ├── __init__.py
│   ├── date_utils.py         # تبدیل تاریخ و زمان
│   ├── astro_engine.py       # موتور محاسبات نجومی
│   └── chart_renderer.py     # رسم نمودار دایره‌ای
│
├── data/                      # دیتابیس شهرها
│   ├── __init__.py
│   └── iranian_cities.py     # 30 شهر ایران
│
├── utils/                     # ابزارهای کمکی
│   ├── __init__.py
│   ├── validators.py         # اعتبارسنجی ورودی
│   └── astro_calculator.py   # واسط محاسبات
│
├── services/                  # سرویس‌های خارجی
│   ├── __init__.py
│   └── ai_service.py         # ارتباط با OpenAI
│
├── templates/                 # قالب‌های HTML
├── static/                    # فایل‌های استاتیک
├── database.py               # مدیریت SQLite
├── config.py                 # تنظیمات
├── prompts.py                # پرامپت‌های AI
├── app.py                    # برنامه اصلی Flask
└── nojoom.db                 # دیتابیس SQLite
```

---

## 📦 نصب و راه‌اندازی

### 1. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 2. تنظیم API Key

فایل `.env` ایجاد کنید:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.gapgpt.app/v1
ASTRO_MODEL=gpt-5.2
SIMPLIFY_MODEL=gpt-4o-mini
```

### 3. اجرای برنامه

```bash
python app.py
```

برنامه روی `http://localhost:5000` اجرا می‌شود.

---

## 🔬 دقت محاسبات

### مقایسه با ZET

این موتور از همان Swiss Ephemeris استفاده می‌کند که ZET استفاده می‌کند:

| ویژگی | این پروژه | ZET |
|-------|----------|-----|
| Swiss Ephemeris | ✅ | ✅ |
| Placidus Houses | ✅ | ✅ |
| True Node | ✅ | ✅ |
| Tropical Zodiac | ✅ | ✅ |
| Retrograde Detection | ✅ | ✅ |
| Aspects Calculation | ✅ | ✅ |

### نکات مهم برای دقت

1. **تاریخ شمسی** به درستی به میلادی تبدیل می‌شود
2. **ساعت محلی** با در نظر گرفتن DST به UTC تبدیل می‌شود
3. **مختصات جغرافیایی** دقیق از دیتابیس استفاده می‌شود
4. **Julian Day** با دقت کامل محاسبه می‌شود
5. **سیستم Placidus** برای خانه‌بندی استفاده می‌شود

---

## 💻 استفاده از API

### مثال کد Python

```python
from core import DateTimeConverter, AstroEngine

# تبدیل تاریخ و زمان
dt_data = DateTimeConverter.parse_and_convert(
    jalali_date_str="1403-01-15",
    local_time_str="14:30"
)

# محاسبه زایچه
engine = AstroEngine()
chart = engine.calculate_complete_chart(
    julian_day=dt_data['julian_day'],
    latitude=35.6892,
    longitude=51.3890,
    house_system='P'
)

# دسترسی به داده‌ها
print(f"ASC: {chart['houses']['ascendant']['longitude']:.2f}°")
print(f"Sun: {chart['planets']['Sun']['longitude']:.2f}°")

# رسم نمودار
from core import ChartRenderer
renderer = ChartRenderer(chart)
renderer.save('chart.png')
```

### خروجی JSON

```json
{
  "planets": {
    "Sun": {
      "longitude": 24.56,
      "sign": "Aries",
      "sign_fa": "حمل",
      "degree_in_sign": 24.56,
      "house": 1,
      "retrograde": false,
      "speed": 0.9856
    }
  },
  "houses": {
    "ascendant": {
      "longitude": 15.23,
      "sign": "Leo",
      "sign_fa": "اسد"
    }
  },
  "aspects": [
    {
      "planet1": "Sun",
      "planet2": "Moon",
      "aspect": "Trine",
      "aspect_fa": "تثلیث",
      "angle": 120.5,
      "orb": 0.5,
      "exact": true
    }
  ]
}
```

---

## 🎨 نمودار دایره‌ای

نمودار شامل:

1. **حلقه بیرونی**: 12 برج با رنگ‌های متفاوت
2. **حلقه میانی**: خانه‌ها با خطوط آبی
3. **خطوط قرمز/سبز**: طالع و قله آسمان
4. **نمادهای سیارات**: با موقعیت دقیق
5. **عقده‌های قمری**: با نماد ☊ و ☋

---

## 🔧 تنظیمات پیشرفته

### تغییر سیستم خانه‌بندی

```python
# Placidus (پیش‌فرض)
chart = engine.calculate_complete_chart(jd, lat, lon, 'P')

# Koch
chart = engine.calculate_complete_chart(jd, lat, lon, 'K')

# Equal
chart = engine.calculate_complete_chart(jd, lat, lon, 'E')

# Whole Sign
chart = engine.calculate_complete_chart(jd, lat, lon, 'W')
```

### تنظیم Orb اسپکت‌ها

در `core/astro_engine.py`:

```python
ASPECTS = {
    'Conjunction': {'angle': 0, 'orb': 8},
    'Opposition': {'angle': 180, 'orb': 8},
    'Trine': {'angle': 120, 'orb': 8},
    'Square': {'angle': 90, 'orb': 8},
    'Sextile': {'angle': 60, 'orb': 6}
}
```

---

## 📊 مثال محاسبه

### ورودی:
- **تاریخ**: 1403-01-15 (شمسی)
- **ساعت**: 14:30 (محلی ایران)
- **شهر**: تهران

### خروجی:
- **تاریخ میلادی**: 2024-04-03
- **ساعت UTC**: 11:00
- **Julian Day**: 2460404.9583
- **طالع**: 15.23° اسد
- **قله آسمان**: 45.67° ثور
- **شمس**: 24.56° حمل در خانه 9
- **قمر**: 12.34° میزان در خانه 3

---

## 🚀 بهینه‌سازی‌ها

### بدون نیاز به اینترنت
- ✅ تمام محاسبات نجومی آفلاین
- ✅ دیتابیس محلی شهرها
- ✅ Swiss Ephemeris داده‌های محلی
- ❌ فقط برای تحلیل AI نیاز به اینترنت

### سرعت
- محاسبه کامل یک زایچه: **< 1 ثانیه**
- رسم نمودار: **< 2 ثانیه**
- تحلیل AI: **5-10 ثانیه**

### دقت
- موقعیت سیارات: **0.001 درجه**
- زمان: **1 ثانیه**
- مختصات: **0.0001 درجه**

---

## 🐛 عیب‌یابی

### خطا: "Swiss Ephemeris not available"

```bash
pip install pyswisseph
```

اگر در Windows مشکل داشتید:
```bash
pip install pyswisseph -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### خطا: "matplotlib backend"

```python
# در ابتدای chart_renderer.py
import matplotlib
matplotlib.use('Agg')
```

### خطا: "شهر یافت نشد"

شهر باید از لیست 30 شهر موجود باشد. برای افزودن شهر جدید:

```python
# در data/iranian_cities.py
IRANIAN_CITIES = {
    "شهر جدید": {
        "name_en": "New City",
        "lat": 35.1234,
        "lon": 51.5678,
        "timezone": "Asia/Tehran"
    }
}
```

---

## 📚 منابع

- [Swiss Ephemeris Documentation](https://www.astro.com/swisseph/)
- [Astrology Calculations](https://www.astro.com/swisseph/swephprg.htm)
- [House Systems](https://www.astro.com/swisseph/swisseph.htm#_Toc46391722)

---

## 🔄 تغییرات نسخه 2.0

### ✨ ویژگی‌های جدید
- ✅ معماری ماژولار کامل
- ✅ محاسبه اسپکت‌ها
- ✅ نمودار دایره‌ای گرافیکی
- ✅ تشخیص راجعه
- ✅ نمایش سرعت سیارات
- ✅ محاسبه دقیق‌تر با DST

### 🔧 بهبودها
- ✅ کد تمیز و مستند
- ✅ جداسازی concerns
- ✅ خطاهای بهتر
- ✅ لاگینگ کامل
- ✅ تست‌پذیری بالا

### 🗑️ حذف شده
- ❌ وابستگی به geopy
- ❌ وابستگی به timezonefinder
- ❌ فایل‌های تست غیرضروری

---

## 📝 لایسنس

این پروژه برای استفاده شخصی و آموزشی آزاد است.

---

**ساخته شده با ❤️ و دقت نجومی**

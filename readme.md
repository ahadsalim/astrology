# Nojoom Atlas

**Nojoom Atlas** یک وب‌اپ فارسی برای محاسبه و تحلیل زایچه تولد و ترانزیت لحظه‌ای است که با تکیه بر **Swiss Ephemeris** داده نجومی دقیق تولید می‌کند و خروجی را برای تحلیل حرفه‌ای (AI-assisted) آماده می‌سازد.

این پروژه برای استفاده واقعی در تحلیل نجومی طراحی شده: از دریافت تاریخ شمسی و شهر تولد، تا تولید جدول‌های کامل کواکب/خانه‌ها/اتصالات، مدیریت شهرها، ذخیره زایچه‌ها، و تولید پرامپت استاندارد تحلیل.

---

## این پروژه چه کاری انجام می‌دهد؟

- محاسبه زایچه تولد با دقت نجومی (Swiss Ephemeris)
- محاسبه سولار ریترن بر اساس شهر انتخابی سالگرد
- محاسبه ترانزیت لحظه‌ای نسبت به چارت تولد
- تولید خروجی ساختاریافته برای تحلیل توسط مدل زبانی
- ساده‌سازی متن تحلیل نجومی با AI
- ذخیره و مشاهده آرشیو زایچه‌ها در SQLite
- مدیریت شهرها و مختصات جغرافیایی از پنل داخلی

---

## قابلیت‌های کلیدی

- **ورودی فارسی کاربر:** تاریخ شمسی، ساعت محلی، شهر تولد، دغدغه تحلیل
- **تبدیل دقیق زمانی:** جلالی -> میلادی/UTC با پشتیبانی ملاحظات زمانی
- **جدول‌های تحلیلی کامل:** کواکب، عقده‌ها، خانه‌ها، اتصالات، حالات
- **نمایش حرفه‌ای:** قالب‌های HTML قابل چاپ
- **Prompt Builder داخلی:** پرامپت آماده برای تحلیل تولد/ترانزیت
- **Persistence:** ذخیره نتایج در `SQLite`
- **API مدیریت شهرها:** افزودن/ویرایش/حذف شهرها از طریق API

---

## تکنولوژی‌ها

- Python 3.10+
- Flask
- pyswisseph (Swiss Ephemeris)
- jdatetime / pytz
- matplotlib / numpy
- OpenAI-compatible API client (`openai`)
- SQLite

---

## ساختار پروژه

```text
app/
├── app.py                 # ورودی اصلی Flask و routeها
├── config.py              # تنظیمات و env
├── database.py            # لایه دیتابیس SQLite
├── prompts.py             # پرامپت‌های تحلیل زایچه/ترانزیت
├── requirements.txt
├── .env.example
│
├── core/                  # موتور و قواعد نجومی
├── utils/                 # محاسبه‌گرها، اعتبارسنجی، فرمت خروجی
├── services/              # سرویس AI
├── data/                  # داده شهرها
├── templates/             # صفحات وب
├── static/                # CSS و فونت
└── doc/                   # مستندات کامل پروژه
```

---

## راه‌اندازی سریع

### 1) نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 2) ساخت فایل تنظیمات محیط

Windows:

```bash
copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

### 3) تنظیم متغیرهای محیطی در `.env`

حداقل این مقادیر را تکمیل کنید:

- `API_KEY`
- `API_URL`
- `ASTRO_MODEL`
- `SIMPLIFY_MODEL`
- `SECRET_KEY`
- `HOST`
- `PORT`

نمونه:

```env
API_KEY=your_api_key_here
API_URL=https://api.gapgpt.app/v1
ASTRO_MODEL=gpt-5.2
SIMPLIFY_MODEL=gpt-4o-mini
FLASK_DEBUG=False
SECRET_KEY=your_secret_key_here
HOST=0.0.0.0
PORT=5000
```

### 4) اجرا

```bash
python app.py
```

سرویس روی آدرس پیش‌فرض زیر در دسترس خواهد بود:

`http://localhost:5000`

---

## مسیرهای اصلی برنامه

- `GET /` صفحه اصلی
- `POST /calculate` محاسبه زایچه تولد + سولار
- `POST /calculate-transit` محاسبه ترانزیت لحظه‌ای
- `POST /view-prompt` ساخت پرامپت تحلیل زایچه
- `POST /view-transit-prompt` ساخت پرامپت تحلیل ترانزیت
- `POST /save` ذخیره زایچه
- `GET /charts` لیست زایچه‌های ذخیره‌شده
- `GET /chart/<id>` مشاهده جزئیات زایچه
- `POST /simplify` ساده‌سازی متن تحلیل
- `GET /cities-admin` پنل مدیریت شهرها

### API شهرها

- `GET /api/cities`
- `POST /api/cities`
- `PUT /api/cities/<id>`
- `DELETE /api/cities/<id>`

---

## دیتابیس

برنامه از SQLite استفاده می‌کند و فایل دیتابیس در مسیر پروژه ایجاد می‌شود:

- `nojoom.db`

جداول اصلی:

- `cities`
- `birth_charts`

مقداردهی اولیه شهرها به‌صورت خودکار انجام می‌شود.

---

## نکات Production

- `FLASK_DEBUG=False` نگه داشته شود.
- `SECRET_KEY` امن و منحصربه‌فرد باشد.
- فایل `.env` هرگز commit نشود.
- برای استقرار واقعی، اجرای پشت Reverse Proxy (مثل Nginx) توصیه می‌شود.

---

## مستندات تکمیلی

اسناد دقیق‌تر در پوشه `doc/` قرار دارند:

- `doc/analysis.md`
- `doc/README.md`
- `doc/CHANGELOG.md`
- `doc/IRAN_DST_DOCUMENTATION.md`
- `doc/PROFESSIONAL_ASTRO_README.md`

---

## نسخه

- Release Tag: `v1.0.0`

---

## مجوز

در صورت نیاز، می‌توانید در ادامه یک `LICENSE` (مثلا MIT) به پروژه اضافه کنید.

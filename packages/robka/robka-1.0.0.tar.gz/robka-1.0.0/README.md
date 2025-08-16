# Robka - کتابخانه ربات‌سازی روبیکا

[![PyPI version](https://badge.fury.io/py/robka.svg)](https://badge.fury.io/py/robka)
[![Python](https://img.shields.io/pypi/pyversions/robka.svg)](https://pypi.org/project/robka/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

کتابخانه‌ای بهینه، ساده و سریع برای ایجاد ربات‌های روبیکا با پشتیبانی کامل از زبان فارسی.

## ویژگی‌های کلیدی

- 🚀 **سرعت بالا**: بهینه‌سازی شده برای عملکرد بهتر
- 🎯 **سادگی**: API ساده و قابل فهم
- 🇮🇷 **پشتیبانی فارسی**: کاملاً فارسی‌سازی شده
- 📦 **سبک**: وابستگی‌های کمتر و حجم کوچک‌تر
- 🔧 **قابل تنظیم**: امکانات پیشرفته برای توسعه‌دهندگان

## نصب

```bash
pip install robka
```

## استفاده سریع

```python
from robka import Client

# ایجاد کلاینت
bot = Client("AUTH_TOKEN")

# ارسال پیام
bot.send_message("CHAT_ID", "سلام! این اولین پیام من است 👋")

# دریافت پیام‌ها
@bot.on_message()
def handle_message(message):
    if message.text == "/start":
        bot.send_message(message.chat_id, "خوش آمدید! 🎉")

# اجرای ربات
bot.run()
```

## مثال‌های بیشتر

### ارسال فایل

```python
# ارسال تصویر
bot.send_photo("CHAT_ID", "path/to/image.jpg", caption="تصویر زیبا 📸")

# ارسال فایل
bot.send_document("CHAT_ID", "path/to/file.pdf")
```

### کار با کیبورد

```python
from robka import InlineKeyboard

keyboard = InlineKeyboard()
keyboard.add_button("دکمه ۱", "callback_1")
keyboard.add_button("دکمه ۲", "callback_2")

bot.send_message("CHAT_ID", "لطفاً یکی را انتخاب کنید:", reply_markup=keyboard)
```

## مستندات

برای مستندات کامل و مثال‌های بیشتر، به [ویکی پروژه](https://github.com/htteX/robka/wiki) مراجعه کنید.

## مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای جزئیات بیشتر فایل [LICENSE](LICENSE) را مطالعه کنید.

## حمایت

اگر از این پروژه استفاده می‌کنید و مفید بوده، لطفاً با دادن ⭐ از آن حمایت کنید!

---

**توسعه‌دهنده**: htteX  
**نسخه**: 1.0.0


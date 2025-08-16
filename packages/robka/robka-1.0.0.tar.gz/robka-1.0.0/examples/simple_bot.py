#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مثال ساده ربات روبیکا با استفاده از کتابخانه robka
Simple Rubika bot example using robka library
"""

from robka import Client, InlineKeyboard

# توکن ربات خود را اینجا قرار دهید
BOT_TOKEN = "YOUR_32_CHARACTER_AUTH_TOKEN_HERE"

# ایجاد کلاینت ربات
bot = Client(BOT_TOKEN)

@bot.on_message()
def handle_message(message):
    """مدیریت پیام‌های دریافتی"""
    
    # پاسخ به دستور /start
    if message.text == "/start":
        welcome_text = """
🎉 سلام! به ربات robka خوش آمدید!

این ربات با استفاده از کتابخانه بهینه robka ساخته شده است.

دستورات موجود:
/start - شروع ربات
/help - راهنما
/info - اطلاعات ربات
/keyboard - نمایش کیبورد نمونه
        """
        bot.send_message(message.chat_id, welcome_text)
    
    # پاسخ به دستور /help
    elif message.text == "/help":
        help_text = """
📚 راهنمای استفاده:

• برای شروع از دستور /start استفاده کنید
• برای دریافت اطلاعات از /info استفاده کنید
• برای مشاهده کیبورد نمونه از /keyboard استفاده کنید

این ربات قابلیت‌های زیر را دارد:
✅ پاسخ به پیام‌های متنی
✅ ارسال کیبورد درون‌خطی
✅ مدیریت دستورات
✅ پشتیبانی کامل از فارسی
        """
        bot.send_message(message.chat_id, help_text)
    
    # پاسخ به دستور /info
    elif message.text == "/info":
        info_text = """
ℹ️ اطلاعات ربات:

📦 نام کتابخانه: robka
🔢 نسخه: 1.0.0
👨‍💻 توسعه‌دهنده: htteX
🚀 ویژگی‌ها: بهینه، سریع و فارسی

🔗 لینک‌های مفید:
• GitHub: https://github.com/htteX/robka
• PyPI: https://pypi.org/project/robka/
        """
        bot.send_message(message.chat_id, info_text)
    
    # پاسخ به دستور /keyboard
    elif message.text == "/keyboard":
        # ساخت کیبورد درون‌خطی
        keyboard = InlineKeyboard()
        keyboard.add_button("🔥 عالی", "awesome")
        keyboard.add_button("👍 خوب", "good")
        keyboard.row()
        keyboard.add_button("📖 مستندات", url="https://github.com/htteX/robka")
        keyboard.add_button("💬 پشتیبانی", "support")
        
        bot.send_message(
            message.chat_id, 
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=keyboard
        )
    
    # پاسخ به پیام‌های عادی
    else:
        if message.has_text:
            # بررسی فارسی بودن متن
            if any(ord(char) >= 0x0600 and ord(char) <= 0x06FF for char in message.text):
                response = f"سلام! شما نوشتید: «{message.text}»\n\n✨ این پیام با robka پردازش شد!"
            else:
                response = f"Hello! You wrote: \"{message.text}\"\n\n✨ This message was processed with robka!"
            
            bot.send_message(message.chat_id, response)


@bot.on_callback_query()
def handle_callback(callback):
    """مدیریت callback های کیبورد درون‌خطی"""
    
    if callback.data == "awesome":
        bot.answer_callback_query(callback.id, "🔥 ممنون! خوشحالیم که robka را دوست دارید!")
    
    elif callback.data == "good":
        bot.answer_callback_query(callback.id, "👍 متشکریم از نظرتان!")
    
    elif callback.data == "support":
        support_text = """
💬 پشتیبانی robka:

برای دریافت پشتیبانی می‌توانید:
• در GitHub issue ایجاد کنید
• با توسعه‌دهنده تماس بگیرید

📧 ایمیل: httex.dev@gmail.com
🐙 GitHub: https://github.com/htteX/robka
        """
        bot.send_message(callback.from_user.user_guid, support_text)
        bot.answer_callback_query(callback.id, "پیام پشتیبانی ارسال شد!")


if __name__ == "__main__":
    print("🤖 ربات robka در حال راه‌اندازی...")
    print("📝 لطفاً توکن ربات خود را در متغیر BOT_TOKEN قرار دهید")
    print("⚡ برای توقف ربات از Ctrl+C استفاده کنید")
    print("-" * 50)
    
    try:
        # اجرای ربات
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 ربات با موفقیت متوقف شد!")
    except Exception as e:
        print(f"❌ خطا در اجرای ربات: {e}")


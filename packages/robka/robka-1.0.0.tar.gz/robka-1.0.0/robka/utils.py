"""
توابع کمکی برای robka
Utility functions for robka
"""

import time
import json
import hashlib
from typing import Dict, Any, Optional
from random import randint


def make_request_data(method: str, data: Dict[str, Any], auth: str) -> Dict[str, Any]:
    """
    ایجاد داده درخواست برای API روبیکا
    Create request data for Rubika API
    
    Args:
        method: نام متد API
        data: داده‌های درخواست
        auth: توکن احراز هویت
        
    Returns:
        داده درخواست آماده
    """
    request_data = {
        'method': method,
        'input': data,
        'client': {
            'app_name': 'Main',
            'app_version': '4.0.7',
            'platform': 'Web',
            'package': 'web.rubika.ir',
            'lang_code': 'fa'
        },
        'auth': auth,
        'tmp_session': generate_tmp_session()
    }
    
    return request_data


def generate_tmp_session() -> str:
    """
    تولید session موقت
    Generate temporary session
    
    Returns:
        session موقت
    """
    timestamp = int(time.time())
    random_num = randint(100000, 999999)
    session_data = f"robka_{timestamp}_{random_num}"
    
    return hashlib.md5(session_data.encode()).hexdigest()


def validate_chat_id(chat_id: str) -> bool:
    """
    اعتبارسنجی شناسه چت
    Validate chat ID
    
    Args:
        chat_id: شناسه چت
        
    Returns:
        True اگر معتبر باشد
    """
    if not chat_id or not isinstance(chat_id, str):
        return False
    
    # شناسه چت باید حداقل 10 کاراکتر باشد
    if len(chat_id) < 10:
        return False
    
    # شناسه چت باید شامل حروف و اعداد باشد
    if not chat_id.replace('_', '').replace('-', '').isalnum():
        return False
    
    return True


def validate_message_text(text: str) -> bool:
    """
    اعتبارسنجی متن پیام
    Validate message text
    
    Args:
        text: متن پیام
        
    Returns:
        True اگر معتبر باشد
    """
    if not text or not isinstance(text, str):
        return False
    
    # حداکثر طول پیام 4096 کاراکتر
    if len(text) > 4096:
        return False
    
    # متن نباید خالی باشد
    if not text.strip():
        return False
    
    return True


def format_file_size(size_bytes: int) -> str:
    """
    فرمت کردن اندازه فایل
    Format file size
    
    Args:
        size_bytes: اندازه به بایت
        
    Returns:
        اندازه فرمت شده
    """
    if size_bytes == 0:
        return "0 بایت"
    
    size_names = ["بایت", "کیلوبایت", "مگابایت", "گیگابایت"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def extract_command(text: str) -> Optional[str]:
    """
    استخراج دستور از متن پیام
    Extract command from message text
    
    Args:
        text: متن پیام
        
    Returns:
        دستور یا None
    """
    if not text or not text.startswith('/'):
        return None
    
    # جدا کردن دستور از پارامترها
    parts = text.split(' ', 1)
    command = parts[0][1:]  # حذف /
    
    return command if command else None


def extract_command_args(text: str) -> list:
    """
    استخراج آرگومان‌های دستور
    Extract command arguments
    
    Args:
        text: متن پیام
        
    Returns:
        لیست آرگومان‌ها
    """
    if not text or not text.startswith('/'):
        return []
    
    parts = text.split(' ')
    if len(parts) <= 1:
        return []
    
    return parts[1:]


def is_persian_text(text: str) -> bool:
    """
    بررسی فارسی بودن متن
    Check if text is Persian
    
    Args:
        text: متن برای بررسی
        
    Returns:
        True اگر فارسی باشد
    """
    if not text:
        return False
    
    persian_chars = 0
    total_chars = 0
    
    for char in text:
        if char.isalpha():
            total_chars += 1
            if '\u0600' <= char <= '\u06FF':  # محدوده حروف فارسی
                persian_chars += 1
    
    if total_chars == 0:
        return False
    
    # اگر بیش از 50% حروف فارسی باشند
    return (persian_chars / total_chars) > 0.5


def clean_html(text: str) -> str:
    """
    پاک کردن تگ‌های HTML از متن
    Clean HTML tags from text
    
    Args:
        text: متن حاوی HTML
        
    Returns:
        متن پاک شده
    """
    import re
    
    if not text:
        return ""
    
    # حذف تگ‌های HTML
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # حذف فاصله‌های اضافی
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text


def escape_markdown(text: str) -> str:
    """
    escape کردن کاراکترهای ویژه markdown
    Escape markdown special characters
    
    Args:
        text: متن برای escape
        
    Returns:
        متن escape شده
    """
    if not text:
        return ""
    
    special_chars = ['*', '_', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text


def generate_message_id() -> str:
    """
    تولید شناسه پیام
    Generate message ID
    
    Returns:
        شناسه پیام
    """
    timestamp = int(time.time() * 1000)
    random_num = randint(1000, 9999)
    
    return f"{timestamp}{random_num}"


def parse_duration(seconds: int) -> str:
    """
    تبدیل ثانیه به فرمت قابل خواندن
    Convert seconds to readable format
    
    Args:
        seconds: تعداد ثانیه
        
    Returns:
        مدت زمان فرمت شده
    """
    if seconds < 60:
        return f"{seconds} ثانیه"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} دقیقه"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours} ساعت و {minutes} دقیقه"
        else:
            return f"{hours} ساعت"


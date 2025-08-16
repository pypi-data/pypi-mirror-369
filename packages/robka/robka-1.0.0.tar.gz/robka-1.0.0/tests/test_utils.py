"""
تست‌های توابع کمکی
Tests for utility functions
"""

import unittest
import sys
import os

# اضافه کردن مسیر پروژه به sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from robka.utils import (
    validate_chat_id,
    validate_message_text,
    format_file_size,
    extract_command,
    extract_command_args,
    is_persian_text,
    clean_html,
    escape_markdown,
    parse_duration
)


class TestUtils(unittest.TestCase):
    """تست‌های توابع کمکی"""
    
    def test_validate_chat_id(self):
        """تست اعتبارسنجی شناسه چت"""
        # شناسه‌های معتبر
        self.assertTrue(validate_chat_id("c0123456789"))
        self.assertTrue(validate_chat_id("u0123456789_abc"))
        self.assertTrue(validate_chat_id("g0123456789-def"))
        
        # شناسه‌های نامعتبر
        self.assertFalse(validate_chat_id(""))
        self.assertFalse(validate_chat_id(None))
        self.assertFalse(validate_chat_id("short"))
        self.assertFalse(validate_chat_id("invalid@chat"))
        self.assertFalse(validate_chat_id(123))
    
    def test_validate_message_text(self):
        """تست اعتبارسنجی متن پیام"""
        # متن‌های معتبر
        self.assertTrue(validate_message_text("سلام"))
        self.assertTrue(validate_message_text("Hello World"))
        self.assertTrue(validate_message_text("متن طولانی " * 100))
        
        # متن‌های نامعتبر
        self.assertFalse(validate_message_text(""))
        self.assertFalse(validate_message_text(None))
        self.assertFalse(validate_message_text("   "))
        self.assertFalse(validate_message_text("x" * 5000))  # خیلی طولانی
        self.assertFalse(validate_message_text(123))
    
    def test_format_file_size(self):
        """تست فرمت کردن اندازه فایل"""
        self.assertEqual(format_file_size(0), "0 بایت")
        self.assertEqual(format_file_size(512), "512.0 بایت")
        self.assertEqual(format_file_size(1024), "1.0 کیلوبایت")
        self.assertEqual(format_file_size(1536), "1.5 کیلوبایت")
        self.assertEqual(format_file_size(1048576), "1.0 مگابایت")
        self.assertEqual(format_file_size(1073741824), "1.0 گیگابایت")
    
    def test_extract_command(self):
        """تست استخراج دستور"""
        self.assertEqual(extract_command("/start"), "start")
        self.assertEqual(extract_command("/help me"), "help")
        self.assertEqual(extract_command("/settings param1 param2"), "settings")
        self.assertIsNone(extract_command("سلام"))
        self.assertIsNone(extract_command(""))
        self.assertIsNone(extract_command("/"))
    
    def test_extract_command_args(self):
        """تست استخراج آرگومان‌های دستور"""
        self.assertEqual(extract_command_args("/start"), [])
        self.assertEqual(extract_command_args("/help me"), ["me"])
        self.assertEqual(extract_command_args("/send file.txt user123"), ["file.txt", "user123"])
        self.assertEqual(extract_command_args("سلام"), [])
        self.assertEqual(extract_command_args(""), [])
    
    def test_is_persian_text(self):
        """تست تشخیص متن فارسی"""
        self.assertTrue(is_persian_text("سلام دنیا"))
        self.assertTrue(is_persian_text("این یک متن فارسی است"))
        self.assertTrue(is_persian_text("فارسی English مخلوط"))  # بیش از 50% فارسی
        self.assertFalse(is_persian_text("Hello World"))
        self.assertFalse(is_persian_text("English فارسی"))  # کمتر از 50% فارسی
        self.assertFalse(is_persian_text("123456"))
        self.assertFalse(is_persian_text(""))
    
    def test_clean_html(self):
        """تست پاک کردن HTML"""
        self.assertEqual(clean_html("<b>سلام</b>"), "سلام")
        self.assertEqual(clean_html("<p>پاراگراف <a href='#'>لینک</a></p>"), "پاراگراف لینک")
        self.assertEqual(clean_html("متن   با    فاصله‌های    زیاد"), "متن با فاصله‌های زیاد")
        self.assertEqual(clean_html(""), "")
        self.assertEqual(clean_html("متن بدون تگ"), "متن بدون تگ")
    
    def test_escape_markdown(self):
        """تست escape کردن markdown"""
        self.assertEqual(escape_markdown("*bold*"), "\\*bold\\*")
        self.assertEqual(escape_markdown("_italic_"), "\\_italic\\_")
        self.assertEqual(escape_markdown("`code`"), "\\`code\\`")
        self.assertEqual(escape_markdown("[link](url)"), "\\[link\\]\\(url\\)")
        self.assertEqual(escape_markdown(""), "")
        self.assertEqual(escape_markdown("متن عادی"), "متن عادی")
    
    def test_parse_duration(self):
        """تست تبدیل مدت زمان"""
        self.assertEqual(parse_duration(30), "30 ثانیه")
        self.assertEqual(parse_duration(90), "1 دقیقه")
        self.assertEqual(parse_duration(150), "2 دقیقه")
        self.assertEqual(parse_duration(3600), "1 ساعت")
        self.assertEqual(parse_duration(3660), "1 ساعت و 1 دقیقه")
        self.assertEqual(parse_duration(7200), "2 ساعت")


if __name__ == '__main__':
    unittest.main()


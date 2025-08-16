"""
کلاس‌های کیبورد برای robka
Keyboard classes for robka
"""

from typing import List, Dict, Any, Optional


class InlineKeyboardButton:
    """
    دکمه کیبورد درون‌خطی
    Inline keyboard button
    """
    
    def __init__(self, text: str, callback_data: Optional[str] = None, 
                 url: Optional[str] = None):
        """
        مقداردهی اولیه دکمه
        Initialize button
        
        Args:
            text: متن دکمه
            callback_data: داده callback
            url: لینک (برای دکمه‌های URL)
        """
        self.text = text
        self.callback_data = callback_data
        self.url = url
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        button_dict = {'text': self.text}
        
        if self.callback_data:
            button_dict['callback_data'] = self.callback_data
        elif self.url:
            button_dict['url'] = self.url
            
        return button_dict


class InlineKeyboard:
    """
    کیبورد درون‌خطی
    Inline keyboard
    """
    
    def __init__(self):
        """مقداردهی اولیه"""
        self.keyboard: List[List[InlineKeyboardButton]] = []
        self.current_row: List[InlineKeyboardButton] = []
    
    def add_button(self, text: str, callback_data: Optional[str] = None,
                   url: Optional[str] = None) -> 'InlineKeyboard':
        """
        افزودن دکمه به ردیف فعلی
        Add button to current row
        
        Args:
            text: متن دکمه
            callback_data: داده callback
            url: لینک
            
        Returns:
            خود کیبورد (برای chain کردن)
        """
        button = InlineKeyboardButton(text, callback_data, url)
        self.current_row.append(button)
        return self
    
    def row(self) -> 'InlineKeyboard':
        """
        شروع ردیف جدید
        Start new row
        
        Returns:
            خود کیبورد
        """
        if self.current_row:
            self.keyboard.append(self.current_row)
            self.current_row = []
        return self
    
    def add_url_button(self, text: str, url: str) -> 'InlineKeyboard':
        """
        افزودن دکمه URL
        Add URL button
        
        Args:
            text: متن دکمه
            url: لینک
            
        Returns:
            خود کیبورد
        """
        return self.add_button(text, url=url)
    
    def add_callback_button(self, text: str, callback_data: str) -> 'InlineKeyboard':
        """
        افزودن دکمه callback
        Add callback button
        
        Args:
            text: متن دکمه
            callback_data: داده callback
            
        Returns:
            خود کیبورد
        """
        return self.add_button(text, callback_data=callback_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری برای ارسال"""
        # اضافه کردن ردیف فعلی اگر خالی نباشد
        if self.current_row:
            self.keyboard.append(self.current_row)
            self.current_row = []
        
        # تبدیل به فرمت مورد نیاز
        keyboard_dict = []
        for row in self.keyboard:
            row_dict = []
            for button in row:
                row_dict.append(button.to_dict())
            keyboard_dict.append(row_dict)
        
        return {
            'inline_keyboard': keyboard_dict
        }


class ReplyKeyboardButton:
    """
    دکمه کیبورد پاسخ
    Reply keyboard button
    """
    
    def __init__(self, text: str, request_contact: bool = False,
                 request_location: bool = False):
        """
        مقداردهی اولیه دکمه
        Initialize button
        
        Args:
            text: متن دکمه
            request_contact: درخواست شماره تماس
            request_location: درخواست موقعیت مکانی
        """
        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        button_dict = {'text': self.text}
        
        if self.request_contact:
            button_dict['request_contact'] = True
        if self.request_location:
            button_dict['request_location'] = True
            
        return button_dict


class ReplyKeyboard:
    """
    کیبورد پاسخ
    Reply keyboard
    """
    
    def __init__(self, resize_keyboard: bool = True, 
                 one_time_keyboard: bool = False):
        """
        مقداردهی اولیه
        Initialize keyboard
        
        Args:
            resize_keyboard: تغییر اندازه خودکار
            one_time_keyboard: مخفی شدن بعد از استفاده
        """
        self.keyboard: List[List[ReplyKeyboardButton]] = []
        self.current_row: List[ReplyKeyboardButton] = []
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
    
    def add_button(self, text: str, request_contact: bool = False,
                   request_location: bool = False) -> 'ReplyKeyboard':
        """
        افزودن دکمه به ردیف فعلی
        Add button to current row
        
        Args:
            text: متن دکمه
            request_contact: درخواست شماره تماس
            request_location: درخواست موقعیت مکانی
            
        Returns:
            خود کیبورد
        """
        button = ReplyKeyboardButton(text, request_contact, request_location)
        self.current_row.append(button)
        return self
    
    def row(self) -> 'ReplyKeyboard':
        """
        شروع ردیف جدید
        Start new row
        
        Returns:
            خود کیبورد
        """
        if self.current_row:
            self.keyboard.append(self.current_row)
            self.current_row = []
        return self
    
    def add_contact_button(self, text: str = "📞 اشتراک شماره تماس") -> 'ReplyKeyboard':
        """
        افزودن دکمه درخواست شماره تماس
        Add contact request button
        
        Args:
            text: متن دکمه
            
        Returns:
            خود کیبورد
        """
        return self.add_button(text, request_contact=True)
    
    def add_location_button(self, text: str = "📍 اشتراک موقعیت مکانی") -> 'ReplyKeyboard':
        """
        افزودن دکمه درخواست موقعیت مکانی
        Add location request button
        
        Args:
            text: متن دکمه
            
        Returns:
            خود کیبورد
        """
        return self.add_button(text, request_location=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری برای ارسال"""
        # اضافه کردن ردیف فعلی اگر خالی نباشد
        if self.current_row:
            self.keyboard.append(self.current_row)
            self.current_row = []
        
        # تبدیل به فرمت مورد نیاز
        keyboard_dict = []
        for row in self.keyboard:
            row_dict = []
            for button in row:
                row_dict.append(button.to_dict())
            keyboard_dict.append(row_dict)
        
        return {
            'keyboard': keyboard_dict,
            'resize_keyboard': self.resize_keyboard,
            'one_time_keyboard': self.one_time_keyboard
        }


class ReplyKeyboardRemove:
    """
    حذف کیبورد پاسخ
    Remove reply keyboard
    """
    
    def __init__(self):
        """مقداردهی اولیه"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            'remove_keyboard': True
        }


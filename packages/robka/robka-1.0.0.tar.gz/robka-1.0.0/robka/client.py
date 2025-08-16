"""
کلاس اصلی کلاینت روبیکا - بهینه‌سازی شده و ساده‌شده
Main Rubika Client Class - Optimized and Simplified
"""

import json
import time
import asyncio
import requests
from typing import Optional, Dict, Any, Callable, List
from threading import Thread

from .encryption import Encryption
from .types import Message, Chat, User
from .exceptions import RobkaException, AuthenticationError, NetworkError
from .utils import make_request_data


class Client:
    """
    کلاینت اصلی روبیکا - بهینه‌سازی شده برای سرعت و سادگی
    Main Rubika Client - Optimized for speed and simplicity
    """
    
    # آدرس‌های سرور روبیکا
    BASE_URL = "https://messengerg2c4.iranlms.ir/"
    UPLOAD_URL = "https://messengerx.iranlms.ir/"
    WS_URL = "wss://msocket1.iranlms.ir:80"
    
    def __init__(self, auth_token: str, timeout: int = 30):
        """
        مقداردهی اولیه کلاینت
        Initialize the client
        
        Args:
            auth_token: توکن احراز هویت
            timeout: مهلت زمانی درخواست‌ها (ثانیه)
        """
        if not auth_token or len(auth_token) != 32:
            raise AuthenticationError("توکن احراز هویت نامعتبر است")
            
        self.auth = auth_token
        self.timeout = timeout
        self.encryption = Encryption()
        self.session = requests.Session()
        self.message_handlers = []
        self.running = False
        
        # تنظیم هدرهای پیش‌فرض
        self.session.headers.update({
            'User-Agent': 'Robka/1.0.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ارسال درخواست به سرور روبیکا
        Send request to Rubika server
        """
        try:
            request_data = make_request_data(method, data, self.auth)
            encrypted_data = self.encryption.encrypt(json.dumps(request_data))
            
            response = self.session.post(
                self.BASE_URL,
                json={'data_enc': encrypted_data},
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise NetworkError(f"خطای شبکه: {response.status_code}")
            
            decrypted_response = self.encryption.decrypt(response.json()['data_enc'])
            return json.loads(decrypted_response)
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"خطای اتصال: {str(e)}")
        except Exception as e:
            raise RobkaException(f"خطای غیرمنتظره: {str(e)}")
    
    def send_message(self, chat_id: str, text: str, reply_to: Optional[str] = None) -> Dict[str, Any]:
        """
        ارسال پیام متنی
        Send text message
        
        Args:
            chat_id: شناسه چت
            text: متن پیام
            reply_to: شناسه پیام برای پاسخ
            
        Returns:
            پاسخ سرور
        """
        data = {
            'object_guid': chat_id,
            'text': text,
            'rnd': int(time.time() * 1000)
        }
        
        if reply_to:
            data['reply_to_message_id'] = reply_to
            
        return self._make_request('sendMessage', data)
    
    def send_photo(self, chat_id: str, photo_path: str, caption: str = "", 
                   reply_to: Optional[str] = None) -> Dict[str, Any]:
        """
        ارسال تصویر
        Send photo
        
        Args:
            chat_id: شناسه چت
            photo_path: مسیر فایل تصویر
            caption: توضیح تصویر
            reply_to: شناسه پیام برای پاسخ
            
        Returns:
            پاسخ سرور
        """
        # آپلود فایل و دریافت file_id
        file_id = self._upload_file(photo_path)
        
        data = {
            'object_guid': chat_id,
            'file_inline': {
                'file_id': file_id,
                'type': 'Image',
                'caption': caption
            },
            'rnd': int(time.time() * 1000)
        }
        
        if reply_to:
            data['reply_to_message_id'] = reply_to
            
        return self._make_request('sendMessage', data)
    
    def send_document(self, chat_id: str, document_path: str, caption: str = "",
                     reply_to: Optional[str] = None) -> Dict[str, Any]:
        """
        ارسال فایل
        Send document
        
        Args:
            chat_id: شناسه چت
            document_path: مسیر فایل
            caption: توضیح فایل
            reply_to: شناسه پیام برای پاسخ
            
        Returns:
            پاسخ سرور
        """
        file_id = self._upload_file(document_path)
        
        data = {
            'object_guid': chat_id,
            'file_inline': {
                'file_id': file_id,
                'type': 'File',
                'caption': caption
            },
            'rnd': int(time.time() * 1000)
        }
        
        if reply_to:
            data['reply_to_message_id'] = reply_to
            
        return self._make_request('sendMessage', data)
    
    def get_messages(self, chat_id: str, max_id: Optional[str] = None, 
                    limit: int = 50) -> Dict[str, Any]:
        """
        دریافت پیام‌های چت
        Get chat messages
        
        Args:
            chat_id: شناسه چت
            max_id: شناسه آخرین پیام
            limit: تعداد پیام‌ها
            
        Returns:
            لیست پیام‌ها
        """
        data = {
            'object_guid': chat_id,
            'sort': 'FromMax',
            'limit': limit
        }
        
        if max_id:
            data['max_id'] = max_id
            
        return self._make_request('getMessages', data)
    
    def delete_message(self, chat_id: str, message_ids: List[str]) -> Dict[str, Any]:
        """
        حذف پیام
        Delete message
        
        Args:
            chat_id: شناسه چت
            message_ids: لیست شناسه پیام‌ها
            
        Returns:
            پاسخ سرور
        """
        data = {
            'object_guid': chat_id,
            'message_ids': message_ids,
            'type': 'Global'
        }
        
        return self._make_request('deleteMessages', data)
    
    def edit_message(self, chat_id: str, message_id: str, new_text: str) -> Dict[str, Any]:
        """
        ویرایش پیام
        Edit message
        
        Args:
            chat_id: شناسه چت
            message_id: شناسه پیام
            new_text: متن جدید
            
        Returns:
            پاسخ سرور
        """
        data = {
            'object_guid': chat_id,
            'message_id': message_id,
            'text': new_text
        }
        
        return self._make_request('editMessage', data)
    
    def _upload_file(self, file_path: str) -> str:
        """
        آپلود فایل به سرور
        Upload file to server
        
        Args:
            file_path: مسیر فایل
            
        Returns:
            شناسه فایل آپلود شده
        """
        # پیاده‌سازی آپلود فایل
        # این بخش نیاز به پیاده‌سازی کامل دارد
        pass
    
    def on_message(self, filters=None):
        """
        دکوراتور برای مدیریت پیام‌ها
        Decorator for message handling
        
        Args:
            filters: فیلترهای پیام
        """
        def decorator(func: Callable):
            self.message_handlers.append((func, filters))
            return func
        return decorator
    
    def run(self):
        """
        اجرای ربات
        Run the bot
        """
        self.running = True
        print("🚀 ربات شروع به کار کرد...")
        
        try:
            while self.running:
                # دریافت پیام‌های جدید و پردازش آن‌ها
                # این بخش نیاز به پیاده‌سازی کامل دارد
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️ ربات متوقف شد.")
            self.running = False
    
    def stop(self):
        """
        توقف ربات
        Stop the bot
        """
        self.running = False


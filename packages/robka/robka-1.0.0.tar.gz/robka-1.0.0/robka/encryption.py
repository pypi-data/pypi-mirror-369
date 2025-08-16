"""
کلاس رمزنگاری بهینه‌شده برای robka
Optimized encryption class for robka
"""

import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class Encryption:
    """
    کلاس رمزنگاری بهینه‌شده
    Optimized encryption class
    """
    
    def __init__(self):
        """مقداردهی اولیه"""
        self.key = b'rubika_key_12345'  # کلید پیش‌فرض (باید از سرور دریافت شود)
        self.iv = b'rubika_iv_123456'   # بردار اولیه (باید تصادفی باشد)
    
    def encrypt(self, data: str) -> str:
        """
        رمزنگاری داده
        Encrypt data
        
        Args:
            data: داده برای رمزنگاری
            
        Returns:
            داده رمزنگاری شده (base64)
        """
        try:
            # تبدیل به bytes
            data_bytes = data.encode('utf-8')
            
            # ایجاد cipher
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            
            # padding و رمزنگاری
            padded_data = pad(data_bytes, AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            
            # تبدیل به base64
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"خطای رمزنگاری: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        رمزگشایی داده
        Decrypt data
        
        Args:
            encrypted_data: داده رمزنگاری شده (base64)
            
        Returns:
            داده رمزگشایی شده
        """
        try:
            # تبدیل از base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # ایجاد cipher
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            
            # رمزگشایی و حذف padding
            decrypted_padded = cipher.decrypt(encrypted_bytes)
            decrypted_data = unpad(decrypted_padded, AES.block_size)
            
            # تبدیل به string
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"خطای رمزگشایی: {str(e)}")
    
    def generate_signature(self, data: str, auth: str) -> str:
        """
        تولید امضای درخواست
        Generate request signature
        
        Args:
            data: داده درخواست
            auth: توکن احراز هویت
            
        Returns:
            امضای درخواست
        """
        try:
            # ترکیب داده و auth
            combined = f"{data}{auth}"
            
            # تولید hash
            hash_obj = hashlib.sha256(combined.encode('utf-8'))
            signature = hash_obj.hexdigest()
            
            return signature
            
        except Exception as e:
            raise Exception(f"خطای تولید امضا: {str(e)}")
    
    def set_keys(self, key: bytes, iv: bytes):
        """
        تنظیم کلید و بردار اولیه
        Set encryption key and IV
        
        Args:
            key: کلید رمزنگاری
            iv: بردار اولیه
        """
        if len(key) != 16:
            raise ValueError("طول کلید باید 16 بایت باشد")
        if len(iv) != 16:
            raise ValueError("طول بردار اولیه باید 16 بایت باشد")
            
        self.key = key
        self.iv = iv
    
    @staticmethod
    def generate_random_key() -> bytes:
        """تولید کلید تصادفی"""
        return get_random_bytes(16)
    
    @staticmethod
    def generate_random_iv() -> bytes:
        """تولید بردار اولیه تصادفی"""
        return get_random_bytes(16)


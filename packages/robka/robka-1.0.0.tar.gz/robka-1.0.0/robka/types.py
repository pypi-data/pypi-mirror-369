"""
انواع داده‌های روبیکا - بهینه‌سازی شده
Rubika Data Types - Optimized
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """
    کلاس کاربر
    User class
    """
    user_guid: str
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool = False
    is_deleted: bool = False
    
    @property
    def full_name(self) -> str:
        """نام کامل کاربر"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def mention(self) -> str:
        """منشن کاربر"""
        if self.username:
            return f"@{self.username}"
        return self.full_name
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """ایجاد شیء کاربر از دیکشنری"""
        return cls(
            user_guid=data.get('user_guid', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name'),
            username=data.get('username'),
            phone=data.get('phone'),
            bio=data.get('bio'),
            is_verified=data.get('is_verified', False),
            is_deleted=data.get('is_deleted', False)
        )


@dataclass
class Chat:
    """
    کلاس چت
    Chat class
    """
    object_guid: str
    title: str
    chat_type: str  # 'User', 'Group', 'Channel'
    description: Optional[str] = None
    username: Optional[str] = None
    member_count: Optional[int] = None
    is_verified: bool = False
    
    @property
    def is_private(self) -> bool:
        """آیا چت خصوصی است؟"""
        return self.chat_type == 'User'
    
    @property
    def is_group(self) -> bool:
        """آیا گروه است؟"""
        return self.chat_type == 'Group'
    
    @property
    def is_channel(self) -> bool:
        """آیا کانال است؟"""
        return self.chat_type == 'Channel'
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chat':
        """ایجاد شیء چت از دیکشنری"""
        return cls(
            object_guid=data.get('object_guid', ''),
            title=data.get('title', ''),
            chat_type=data.get('type', 'User'),
            description=data.get('description'),
            username=data.get('username'),
            member_count=data.get('member_count'),
            is_verified=data.get('is_verified', False)
        )


@dataclass
class MessageEntity:
    """
    موجودیت پیام (لینک، منشن، ...)
    Message entity (link, mention, ...)
    """
    type: str  # 'Bold', 'Italic', 'Mention', 'Hashtag', 'Link', etc.
    offset: int
    length: int
    user_guid: Optional[str] = None
    url: Optional[str] = None


@dataclass
class File:
    """
    کلاس فایل
    File class
    """
    file_id: str
    file_name: str
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    
    @property
    def is_image(self) -> bool:
        """آیا فایل تصویر است؟"""
        return self.mime_type.startswith('image/')
    
    @property
    def is_video(self) -> bool:
        """آیا فایل ویدیو است؟"""
        return self.mime_type.startswith('video/')
    
    @property
    def is_audio(self) -> bool:
        """آیا فایل صوتی است؟"""
        return self.mime_type.startswith('audio/')
    
    @property
    def is_document(self) -> bool:
        """آیا فایل سند است؟"""
        return not (self.is_image or self.is_video or self.is_audio)


@dataclass
class Message:
    """
    کلاس پیام
    Message class
    """
    message_id: str
    chat_id: str
    from_user: Optional[User]
    text: Optional[str] = None
    file: Optional[File] = None
    reply_to: Optional['Message'] = None
    forward_from: Optional[User] = None
    entities: List[MessageEntity] = None
    date: Optional[datetime] = None
    edit_date: Optional[datetime] = None
    is_edited: bool = False
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = []
    
    @property
    def has_text(self) -> bool:
        """آیا پیام متن دارد؟"""
        return bool(self.text and self.text.strip())
    
    @property
    def has_file(self) -> bool:
        """آیا پیام فایل دارد؟"""
        return self.file is not None
    
    @property
    def is_reply(self) -> bool:
        """آیا پیام پاسخ است؟"""
        return self.reply_to is not None
    
    @property
    def is_forward(self) -> bool:
        """آیا پیام فوروارد است؟"""
        return self.forward_from is not None
    
    @property
    def content_type(self) -> str:
        """نوع محتوای پیام"""
        if self.has_file:
            if self.file.is_image:
                return 'photo'
            elif self.file.is_video:
                return 'video'
            elif self.file.is_audio:
                return 'audio'
            else:
                return 'document'
        elif self.has_text:
            return 'text'
        else:
            return 'unknown'
    
    def get_entities_by_type(self, entity_type: str) -> List[MessageEntity]:
        """دریافت موجودیت‌های پیام بر اساس نوع"""
        return [entity for entity in self.entities if entity.type == entity_type]
    
    def get_mentions(self) -> List[MessageEntity]:
        """دریافت منشن‌های پیام"""
        return self.get_entities_by_type('Mention')
    
    def get_hashtags(self) -> List[MessageEntity]:
        """دریافت هشتگ‌های پیام"""
        return self.get_entities_by_type('Hashtag')
    
    def get_links(self) -> List[MessageEntity]:
        """دریافت لینک‌های پیام"""
        return self.get_entities_by_type('Link')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """ایجاد شیء پیام از دیکشنری"""
        # پردازش کاربر فرستنده
        from_user = None
        if 'author_object_guid' in data:
            from_user = User(
                user_guid=data['author_object_guid'],
                first_name=data.get('author_title', 'نامشخص')
            )
        
        # پردازش فایل
        file_obj = None
        if 'file_inline' in data:
            file_data = data['file_inline']
            file_obj = File(
                file_id=file_data.get('file_id', ''),
                file_name=file_data.get('file_name', ''),
                file_size=file_data.get('size', 0),
                mime_type=file_data.get('mime', ''),
                width=file_data.get('width'),
                height=file_data.get('height'),
                duration=file_data.get('time')
            )
        
        # پردازش تاریخ
        date_obj = None
        if 'time' in data:
            try:
                date_obj = datetime.fromtimestamp(int(data['time']))
            except (ValueError, TypeError):
                pass
        
        return cls(
            message_id=data.get('message_id', ''),
            chat_id=data.get('object_guid', ''),
            from_user=from_user,
            text=data.get('text'),
            file=file_obj,
            date=date_obj,
            is_edited=data.get('is_edited', False)
        )


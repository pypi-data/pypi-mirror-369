#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robka Types - کلاس‌های نوع داده برای robka
Type classes for robka library
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime


class RobkaObject:
    """کلاس پایه برای تمام اشیاء robka"""
    
    def __init__(self, data: Dict[str, Any] = None):
        self._raw_data = data or {}
        self._parse_data()
    
    def _parse_data(self):
        """پردازش داده‌های خام"""
        pass
    
    @property
    def raw_data(self) -> Dict[str, Any]:
        """دسترسی به داده‌های خام"""
        return self._raw_data
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return self._raw_data


class User(RobkaObject):
    """کلاس کاربر"""
    
    def _parse_data(self):
        data = self._raw_data
        self.user_guid: str = data.get("user_guid", "")
        self.username: Optional[str] = data.get("username")
        self.first_name: str = data.get("first_name", "")
        self.last_name: Optional[str] = data.get("last_name")
        self.bio: Optional[str] = data.get("bio")
        self.phone: Optional[str] = data.get("phone")
        self.is_verified: bool = data.get("is_verified", False)
        self.is_bot: bool = data.get("is_bot", False)
        self.is_contact: bool = data.get("is_contact", False)
        self.is_mutual_contact: bool = data.get("is_mutual_contact", False)
        self.is_deleted: bool = data.get("is_deleted", False)
        self.avatar_id: Optional[str] = data.get("avatar_id")
        self.online_status: Optional[str] = data.get("online_status")
        self.last_online: Optional[int] = data.get("last_online")
    
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
    
    def __str__(self):
        return self.full_name
    
    def __repr__(self):
        return f"User(user_guid='{self.user_guid}', username='{self.username}', name='{self.full_name}')"


class Chat(RobkaObject):
    """کلاس چت (گروه، کانال، چت خصوصی)"""
    
    def _parse_data(self):
        data = self._raw_data
        self.chat_id: str = data.get("object_guid", data.get("chat_id", ""))
        self.chat_type: str = data.get("type", "")
        self.title: Optional[str] = data.get("title")
        self.username: Optional[str] = data.get("username")
        self.description: Optional[str] = data.get("description")
        self.avatar_id: Optional[str] = data.get("avatar_id")
        self.member_count: int = data.get("count_members", 0)
        self.is_verified: bool = data.get("is_verified", False)
        self.is_mute: bool = data.get("is_mute", False)
        self.is_pin: bool = data.get("is_pin", False)
        self.join_link: Optional[str] = data.get("join_link")
        self.last_message: Optional[Dict] = data.get("last_message")
        self.unread_count: int = data.get("unread_count", 0)
    
    @property
    def is_private(self) -> bool:
        """آیا چت خصوصی است؟"""
        return self.chat_type.lower() in ["user", "bot"]
    
    @property
    def is_group(self) -> bool:
        """آیا گروه است؟"""
        return self.chat_type.lower() == "group"
    
    @property
    def is_channel(self) -> bool:
        """آیا کانال است؟"""
        return self.chat_type.lower() == "channel"
    
    def __str__(self):
        return self.title or self.chat_id
    
    def __repr__(self):
        return f"Chat(chat_id='{self.chat_id}', type='{self.chat_type}', title='{self.title}')"


class File(RobkaObject):
    """کلاس فایل"""
    
    def _parse_data(self):
        data = self._raw_data
        self.file_id: str = data.get("file_id", "")
        self.dc_id: str = data.get("dc_id", "")
        self.access_hash_rec: str = data.get("access_hash_rec", "")
        self.file_name: str = data.get("file_name", "")
        self.file_size: int = data.get("size", 0)
        self.mime_type: str = data.get("mime", "")
        self.file_type: str = data.get("type", "")
        self.width: int = data.get("width", 0)
        self.height: int = data.get("height", 0)
        self.duration: float = data.get("time", 0.0)
        self.thumb_inline: Optional[str] = data.get("thumb_inline")
        self.music_performer: Optional[str] = data.get("music_performer")
        self.auto_play: bool = data.get("auto_play", False)
    
    @property
    def is_image(self) -> bool:
        """آیا فایل تصویر است؟"""
        return self.file_type.lower() == "image"
    
    @property
    def is_video(self) -> bool:
        """آیا فایل ویدئو است؟"""
        return self.file_type.lower() == "video"
    
    @property
    def is_audio(self) -> bool:
        """آیا فایل صوتی است؟"""
        return self.file_type.lower() in ["voice", "music"]
    
    @property
    def is_document(self) -> bool:
        """آیا فایل سند است؟"""
        return self.file_type.lower() == "file"
    
    @property
    def is_gif(self) -> bool:
        """آیا فایل GIF است؟"""
        return self.file_type.lower() == "gif"
    
    def __str__(self):
        return self.file_name
    
    def __repr__(self):
        return f"File(file_id='{self.file_id}', name='{self.file_name}', type='{self.file_type}')"


class Contact(RobkaObject):
    """کلاس مخاطب"""
    
    def _parse_data(self):
        data = self._raw_data
        self.user_guid: str = data.get("user_guid", "")
        self.phone: str = data.get("phone_number", "")
        self.first_name: str = data.get("first_name", "")
        self.last_name: Optional[str] = data.get("last_name")
    
    @property
    def full_name(self) -> str:
        """نام کامل مخاطب"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def __str__(self):
        return f"{self.full_name} ({self.phone})"
    
    def __repr__(self):
        return f"Contact(user_guid='{self.user_guid}', name='{self.full_name}', phone='{self.phone}')"


class Location(RobkaObject):
    """کلاس موقعیت مکانی"""
    
    def _parse_data(self):
        data = self._raw_data
        self.latitude: float = data.get("latitude", 0.0)
        self.longitude: float = data.get("longitude", 0.0)
    
    def __str__(self):
        return f"({self.latitude}, {self.longitude})"
    
    def __repr__(self):
        return f"Location(latitude={self.latitude}, longitude={self.longitude})"


class PollOption(RobkaObject):
    """کلاس گزینه نظرسنجی"""
    
    def _parse_data(self):
        data = self._raw_data
        self.option_index: int = data.get("option_index", 0)
        self.text: str = data.get("text", "")
        self.vote_count: int = data.get("vote_count", 0)
        self.is_chosen: bool = data.get("is_chosen", False)
    
    def __str__(self):
        return self.text
    
    def __repr__(self):
        return f"PollOption(index={self.option_index}, text='{self.text}', votes={self.vote_count})"


class Poll(RobkaObject):
    """کلاس نظرسنجی"""
    
    def _parse_data(self):
        data = self._raw_data
        self.poll_id: str = data.get("poll_id", "")
        self.question: str = data.get("question", "")
        self.is_anonymous: bool = data.get("is_anonymous", True)
        self.is_quiz: bool = data.get("type", "") == "Quiz"
        self.total_votes: int = data.get("total_vote_count", 0)
        self.is_closed: bool = data.get("is_closed", False)
        
        # پردازش گزینه‌ها
        self.options: List[PollOption] = []
        for option_data in data.get("options", []):
            self.options.append(PollOption(option_data))
    
    def __str__(self):
        return self.question
    
    def __repr__(self):
        return f"Poll(poll_id='{self.poll_id}', question='{self.question}', options={len(self.options)})"


class Message(RobkaObject):
    """کلاس پیام"""
    
    def _parse_data(self):
        data = self._raw_data
        self.message_id: str = data.get("message_id", "")
        self.chat_id: str = data.get("object_guid", "")
        self.text: Optional[str] = data.get("text")
        self.message_type: str = data.get("type", "")
        self.is_mine: bool = data.get("is_mine", False)
        self.is_edited: bool = data.get("is_edited", False)
        self.time: int = data.get("time", 0)
        self.reply_to_message_id: Optional[str] = data.get("reply_to_message_id")
        
        # پردازش فرستنده
        author_data = data.get("author_object_guid")
        if author_data:
            self.from_user = User(author_data) if isinstance(author_data, dict) else None
            self.author_guid = author_data if isinstance(author_data, str) else author_data.get("user_guid", "")
        else:
            self.from_user = None
            self.author_guid = ""
        
        # پردازش فایل
        file_data = data.get("file_inline")
        self.file = File(file_data) if file_data else None
        
        # پردازش مخاطب
        contact_data = data.get("contact")
        self.contact = Contact(contact_data) if contact_data else None
        
        # پردازش موقعیت مکانی
        location_data = data.get("location")
        self.location = Location(location_data) if location_data else None
        
        # پردازش نظرسنجی
        poll_data = data.get("poll")
        self.poll = Poll(poll_data) if poll_data else None
        
        # پردازش فراداده (فرمت‌بندی)
        self.metadata: List[Dict] = data.get("metadata", {}).get("meta_data_parts", [])
        
        # پردازش فوروارد
        self.forwarded_from: Optional[Dict] = data.get("forwarded_from")
        self.forwarded_no_link: Optional[Dict] = data.get("forwarded_no_link")
        
        # پردازش رویداد
        self.event_data: Optional[Dict] = data.get("event_data")
    
    @property
    def datetime(self) -> datetime:
        """تاریخ و زمان پیام"""
        return datetime.fromtimestamp(self.time)
    
    @property
    def is_text(self) -> bool:
        """آیا پیام متنی است؟"""
        return self.message_type.lower() == "text"
    
    @property
    def is_media(self) -> bool:
        """آیا پیام شامل فایل است؟"""
        return self.file is not None
    
    @property
    def is_photo(self) -> bool:
        """آیا پیام عکس است؟"""
        return self.file and self.file.is_image
    
    @property
    def is_video(self) -> bool:
        """آیا پیام ویدئو است؟"""
        return self.file and self.file.is_video
    
    @property
    def is_audio(self) -> bool:
        """آیا پیام صوتی است؟"""
        return self.file and self.file.is_audio
    
    @property
    def is_document(self) -> bool:
        """آیا پیام سند است؟"""
        return self.file and self.file.is_document
    
    @property
    def is_contact(self) -> bool:
        """آیا پیام مخاطب است؟"""
        return self.contact is not None
    
    @property
    def is_location(self) -> bool:
        """آیا پیام موقعیت مکانی است؟"""
        return self.location is not None
    
    @property
    def is_poll(self) -> bool:
        """آیا پیام نظرسنجی است؟"""
        return self.poll is not None
    
    @property
    def is_forwarded(self) -> bool:
        """آیا پیام فوروارد شده است؟"""
        return self.forwarded_from is not None or self.forwarded_no_link is not None
    
    @property
    def is_reply(self) -> bool:
        """آیا پیام پاسخ به پیام دیگری است؟"""
        return self.reply_to_message_id is not None
    
    @property
    def is_event(self) -> bool:
        """آیا پیام رویدادی است؟"""
        return self.event_data is not None
    
    def __str__(self):
        if self.text:
            return self.text[:50] + "..." if len(self.text) > 50 else self.text
        elif self.is_photo:
            return "[عکس]"
        elif self.is_video:
            return "[ویدئو]"
        elif self.is_audio:
            return "[صوت]"
        elif self.is_document:
            return "[سند]"
        elif self.is_contact:
            return "[مخاطب]"
        elif self.is_location:
            return "[موقعیت مکانی]"
        elif self.is_poll:
            return "[نظرسنجی]"
        else:
            return f"[{self.message_type}]"
    
    def __repr__(self):
        return f"Message(message_id='{self.message_id}', chat_id='{self.chat_id}', type='{self.message_type}')"


# Type aliases for convenience
MessageType = Union[str, Message]
ChatType = Union[str, Chat]
UserType = Union[str, User]


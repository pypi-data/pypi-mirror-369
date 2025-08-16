"""
تست‌های کلاس‌های نوع داده
Tests for data type classes
"""

import unittest
from datetime import datetime
import sys
import os

# اضافه کردن مسیر پروژه به sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from robka.types import User, Chat, Message, File, MessageEntity


class TestUser(unittest.TestCase):
    """تست‌های کلاس User"""
    
    def test_user_creation(self):
        """تست ایجاد کاربر"""
        user = User(
            user_guid="user123",
            first_name="علی",
            last_name="احمدی",
            username="ali_ahmadi"
        )
        
        self.assertEqual(user.user_guid, "user123")
        self.assertEqual(user.first_name, "علی")
        self.assertEqual(user.last_name, "احمدی")
        self.assertEqual(user.username, "ali_ahmadi")
    
    def test_full_name_property(self):
        """تست خاصیت نام کامل"""
        user_with_lastname = User("user1", "علی", "احمدی")
        user_without_lastname = User("user2", "علی")
        
        self.assertEqual(user_with_lastname.full_name, "علی احمدی")
        self.assertEqual(user_without_lastname.full_name, "علی")
    
    def test_mention_property(self):
        """تست خاصیت منشن"""
        user_with_username = User("user1", "علی", username="ali_ahmadi")
        user_without_username = User("user2", "علی", "احمدی")
        
        self.assertEqual(user_with_username.mention, "@ali_ahmadi")
        self.assertEqual(user_without_username.mention, "علی احمدی")
    
    def test_from_dict(self):
        """تست ایجاد کاربر از دیکشنری"""
        data = {
            'user_guid': 'user123',
            'first_name': 'علی',
            'last_name': 'احمدی',
            'username': 'ali_ahmadi',
            'is_verified': True
        }
        
        user = User.from_dict(data)
        
        self.assertEqual(user.user_guid, 'user123')
        self.assertEqual(user.first_name, 'علی')
        self.assertEqual(user.last_name, 'احمدی')
        self.assertEqual(user.username, 'ali_ahmadi')
        self.assertTrue(user.is_verified)


class TestChat(unittest.TestCase):
    """تست‌های کلاس Chat"""
    
    def test_chat_creation(self):
        """تست ایجاد چت"""
        chat = Chat(
            object_guid="chat123",
            title="گروه تست",
            chat_type="Group"
        )
        
        self.assertEqual(chat.object_guid, "chat123")
        self.assertEqual(chat.title, "گروه تست")
        self.assertEqual(chat.chat_type, "Group")
    
    def test_chat_type_properties(self):
        """تست خواص نوع چت"""
        private_chat = Chat("chat1", "علی", "User")
        group_chat = Chat("chat2", "گروه", "Group")
        channel_chat = Chat("chat3", "کانال", "Channel")
        
        self.assertTrue(private_chat.is_private)
        self.assertFalse(private_chat.is_group)
        self.assertFalse(private_chat.is_channel)
        
        self.assertFalse(group_chat.is_private)
        self.assertTrue(group_chat.is_group)
        self.assertFalse(group_chat.is_channel)
        
        self.assertFalse(channel_chat.is_private)
        self.assertFalse(channel_chat.is_group)
        self.assertTrue(channel_chat.is_channel)


class TestFile(unittest.TestCase):
    """تست‌های کلاس File"""
    
    def test_file_creation(self):
        """تست ایجاد فایل"""
        file_obj = File(
            file_id="file123",
            file_name="test.jpg",
            file_size=1024,
            mime_type="image/jpeg"
        )
        
        self.assertEqual(file_obj.file_id, "file123")
        self.assertEqual(file_obj.file_name, "test.jpg")
        self.assertEqual(file_obj.file_size, 1024)
        self.assertEqual(file_obj.mime_type, "image/jpeg")
    
    def test_file_type_properties(self):
        """تست خواص نوع فایل"""
        image_file = File("f1", "image.jpg", 1024, "image/jpeg")
        video_file = File("f2", "video.mp4", 2048, "video/mp4")
        audio_file = File("f3", "audio.mp3", 512, "audio/mpeg")
        doc_file = File("f4", "doc.pdf", 256, "application/pdf")
        
        self.assertTrue(image_file.is_image)
        self.assertFalse(image_file.is_video)
        self.assertFalse(image_file.is_audio)
        self.assertFalse(image_file.is_document)
        
        self.assertTrue(video_file.is_video)
        self.assertTrue(audio_file.is_audio)
        self.assertTrue(doc_file.is_document)


class TestMessage(unittest.TestCase):
    """تست‌های کلاس Message"""
    
    def test_message_creation(self):
        """تست ایجاد پیام"""
        user = User("user1", "علی")
        message = Message(
            message_id="msg123",
            chat_id="chat123",
            from_user=user,
            text="سلام دنیا"
        )
        
        self.assertEqual(message.message_id, "msg123")
        self.assertEqual(message.chat_id, "chat123")
        self.assertEqual(message.from_user, user)
        self.assertEqual(message.text, "سلام دنیا")
    
    def test_message_properties(self):
        """تست خواص پیام"""
        text_message = Message("msg1", "chat1", None, text="سلام")
        file_message = Message("msg2", "chat1", None, file=File("f1", "test.jpg", 1024, "image/jpeg"))
        empty_message = Message("msg3", "chat1", None)
        
        self.assertTrue(text_message.has_text)
        self.assertFalse(text_message.has_file)
        self.assertEqual(text_message.content_type, "text")
        
        self.assertFalse(file_message.has_text)
        self.assertTrue(file_message.has_file)
        self.assertEqual(file_message.content_type, "photo")
        
        self.assertFalse(empty_message.has_text)
        self.assertFalse(empty_message.has_file)
        self.assertEqual(empty_message.content_type, "unknown")
    
    def test_message_entities(self):
        """تست موجودیت‌های پیام"""
        message = Message("msg1", "chat1", None, text="سلام @ali_ahmadi")
        
        # افزودن موجودیت منشن
        mention_entity = MessageEntity("Mention", 5, 11, user_guid="user123")
        message.entities.append(mention_entity)
        
        mentions = message.get_mentions()
        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0].type, "Mention")
        self.assertEqual(mentions[0].user_guid, "user123")


if __name__ == '__main__':
    unittest.main()


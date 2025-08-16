"""
استثناهای کتابخانه robka
Robka Library Exceptions
"""


class RobkaException(Exception):
    """
    کلاس پایه برای تمام استثناهای robka
    Base class for all robka exceptions
    """
    def __init__(self, message: str = "خطای عمومی robka"):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(RobkaException):
    """
    خطای احراز هویت
    Authentication error
    """
    def __init__(self, message: str = "خطای احراز هویت"):
        super().__init__(message)


class NetworkError(RobkaException):
    """
    خطای شبکه
    Network error
    """
    def __init__(self, message: str = "خطای اتصال به شبکه"):
        super().__init__(message)


class InvalidParameterError(RobkaException):
    """
    خطای پارامتر نامعتبر
    Invalid parameter error
    """
    def __init__(self, message: str = "پارامتر نامعتبر"):
        super().__init__(message)


class FileNotFoundError(RobkaException):
    """
    خطای فایل یافت نشد
    File not found error
    """
    def __init__(self, message: str = "فایل یافت نشد"):
        super().__init__(message)


class UploadError(RobkaException):
    """
    خطای آپلود فایل
    File upload error
    """
    def __init__(self, message: str = "خطای آپلود فایل"):
        super().__init__(message)


class RateLimitError(RobkaException):
    """
    خطای محدودیت نرخ درخواست
    Rate limit error
    """
    def __init__(self, message: str = "محدودیت نرخ درخواست"):
        super().__init__(message)


class ServerError(RobkaException):
    """
    خطای سرور
    Server error
    """
    def __init__(self, message: str = "خطای سرور"):
        super().__init__(message)


class TimeoutError(RobkaException):
    """
    خطای انقضای زمان
    Timeout error
    """
    def __init__(self, message: str = "انقضای زمان درخواست"):
        super().__init__(message)


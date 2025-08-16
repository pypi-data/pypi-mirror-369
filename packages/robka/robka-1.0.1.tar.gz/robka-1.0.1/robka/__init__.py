#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robka - کتابخانه مدرن و بهینه‌شده پایتون برای API روبیکا
Modern, optimized Python library for Rubika API

Author: htteX
Version: 1.0.1
License: MIT
"""

__version__ = "1.0.1"
__author__ = "htteX"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2024 htteX"

# Core imports
from .client import Bot as Client
from .rubino import Rubino
from .types import *
from .exceptions import *
from . import filters

# Legacy compatibility
Bot = Client

# Convenience imports
__all__ = [
    # Core classes
    "Client",
    "Bot",  # Legacy compatibility
    "Rubino",
    
    # Types
    "Message",
    "User", 
    "Chat",
    "File",
    "Contact",
    "Location",
    "Poll",
    "PollOption",
    
    # Exceptions
    "RobkaException",
    "AuthenticationError",
    "InvalidInputError", 
    "TooManyRequestsError",
    "NetworkError",
    "FileError",
    
    # Legacy exceptions
    "InvalidAuth",
    "NotRegistered", 
    "TooRequests",
    
    # Filters module
    "filters",
    
    # Version info
    "__version__",
    "__author__",
    "__license__",
]

# Welcome message
def _show_welcome():
    """نمایش پیام خوش‌آمدگویی"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        
        console = Console()
        
        title = Text("Robka", style="bold cyan")
        subtitle = Text(f"نسخه {__version__} - ساخته شده توسط {__author__}", style="dim")
        
        content = Text.assemble(
            title, "\n",
            subtitle, "\n\n",
            "کتابخانه مدرن و بهینه‌شده پایتون برای API روبیکا", "\n",
            "Modern, optimized Python library for Rubika API", "\n\n",
            "🚀 سرعت بالا | 🎯 سادگی | 🌐 پشتیبانی کامل", "\n",
            "📚 مستندات: https://robka.readthedocs.io/", "\n",
            "🐛 گزارش باگ: https://github.com/httex/robka/issues"
        )
        
        panel = Panel(
            content,
            title="[bold green]خوش آمدید![/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        console.print(panel)
        
    except ImportError:
        # Fallback for when rich is not available
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                            Robka                             ║
║                      نسخه {__version__} - htteX                      ║
╠══════════════════════════════════════════════════════════════╣
║  کتابخانه مدرن و بهینه‌شده پایتون برای API روبیکا              ║
║  Modern, optimized Python library for Rubika API           ║
║                                                              ║
║  🚀 سرعت بالا | 🎯 سادگی | 🌐 پشتیبانی کامل                ║
║                                                              ║
║  📚 مستندات: https://robka.readthedocs.io/                  ║
║  🐛 گزارش باگ: https://github.com/httex/robka/issues        ║
╚══════════════════════════════════════════════════════════════╝
        """)

# Show welcome message on import (can be disabled by setting ROBKA_NO_WELCOME=1)
import os
if not os.environ.get("ROBKA_NO_WELCOME"):
    _show_welcome()


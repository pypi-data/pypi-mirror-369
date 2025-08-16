from setuptools import setup, find_packages

requires = ["requests", "pycryptodome", "urllib3", "tqdm", "aiohttp", "rich", "websocket-client", "schedule"]
version = "1.0.0"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="robka",
    version=version,
    description="کتابخانه‌ای بهینه و ساده برای ایجاد ربات‌های روبیکا - Optimized and simple library for creating Rubika bots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/htteX/robka",
    download_url="https://github.com/htteX/robka/releases/latest",
    author="htteX",
    author_email="httex.dev@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: Persian",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    keywords="rubika bot api library python robka روبیکا ربات",
    project_urls={
        "Bug Reports": "https://github.com/htteX/robka/issues",
        "Source": "https://github.com/htteX/robka",
        "Documentation": "https://github.com/htteX/robka/wiki",
    },
    python_requires=">=3.7",
    packages=find_packages(),
    zip_safe=False,
    install_requires=requires
)


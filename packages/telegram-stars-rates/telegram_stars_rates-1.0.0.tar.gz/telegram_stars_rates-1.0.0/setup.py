#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="telegram-stars-rates",
    version="1.0.0",
    author="Telegram Stars Team",
    author_email="dev@telegram-stars.com",
    description="Real-time Telegram Stars to USDT exchange rates via Fragment blockchain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/telegram-stars/rates",
    project_urls={
        "Bug Tracker": "https://github.com/telegram-stars/rates/issues",
        "Documentation": "https://github.com/telegram-stars/rates#readme",
        "Web Converter": "https://telegram-stars.github.io/rates",
        "Source Code": "https://github.com/telegram-stars/rates",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    python_requires=">=3.7",
    install_requires=["requests>=2.25.0"],
    entry_points={
        "console_scripts": [
            "telegram-stars-rates=telegram_stars_rates.cli:main",
        ],
    },
    keywords="telegram stars ton fragment cryptocurrency exchange rates blockchain usdt converter",
    zip_safe=False,
    include_package_data=True,
)
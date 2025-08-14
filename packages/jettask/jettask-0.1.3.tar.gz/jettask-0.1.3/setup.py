from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_long_description():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    return "JetTask - A high-performance distributed task queue system"

# 读取 requirements.txt
def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

setup(
    name="jettask",
    version="0.1.3",
    author="JetTask Team",
    author_email="support@jettask.io",
    description="A high-performance distributed task queue system with web monitoring",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jettask",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0",
            "flake8>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jettask=jettask.core.cli:main",
            "jettask-webui=jettask.webui.backend.main:run_server",
            "jettask-monitor=jettask.webui.run_monitor:main",
        ],
    },
    include_package_data=True,
    package_data={
        "jettask": [
            "webui/static/**/*",
            "webui/frontend/dist/**/*",
            "webui/schema.sql",
            "webui/*.html",
        ],
    },
    zip_safe=False,
)
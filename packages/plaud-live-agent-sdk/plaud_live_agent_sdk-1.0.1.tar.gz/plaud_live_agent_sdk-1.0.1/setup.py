from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Plaud Live Agent SDK - 实时AI助手客户端SDK"

setup(
    name="plaud-live-agent-sdk",
    version="1.0.1",
    author="Plaud AI",
    author_email="dev-support@plaud.ai",
    description="Live Agent SDK - 实时AI助手客户端SDK",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/plaud-ai/plaud-live-agent-dev",
    packages=find_packages(include=["live_agent_sdk", "live_agent_sdk.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "livekit>=1.0.0",
        "livekit-api>=1.0.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "audio": [
            "sounddevice>=0.4.0",
        ],
    },
    keywords="plaud, livekit, webrtc, audio, real-time, ai, assistant",
    project_urls={
        "Bug Reports": "https://github.com/plaud-ai/plaud-live-agent-dev/issues",
        "Source": "https://github.com/plaud-ai/plaud-live-agent-dev",
        "Documentation": "https://github.com/plaud-ai/live-agent-sdk/blob/main/README.md",
    },
) 
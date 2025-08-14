# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name="plugllm",
    version="0.1.2",
    author="Yash Kumar Firoziya",
    author_email="ykfiroziya@gmail.com",
    description="Unified LLM API interface for OpenAI, Gemini, Mistral, Groq and more.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/firoziya/plugllm",
    project_urls={
        "Documentation": "https://github.com/firoziya/plugllm#readme",
        "Source Code": "https://github.com/firoziya/plugllm",
    },
    packages=find_packages(),
    install_requires=[
        "requests>=2.20.0",
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires='>=3.7',
    keywords="llm api openai gemini mistral groq ai chatbot",
    license="MIT",
)

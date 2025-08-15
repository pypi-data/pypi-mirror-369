from setuptools import setup, find_packages

setup(
    name="autoterminal",
    version="0.1.0",
    description="智能终端工具，基于LLM将自然语言转换为终端命令(create by claude 4 sonnet)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="wds",
    author_email="wdsnpshy@163.com",
    url="https://github.com/wds-dxh/autoterminal",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
    ],
    entry_points={
        'console_scripts': [
            'at=autoterminal.main:main',
        ],
    },
    python_requires='>=3.10',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    keywords=["terminal", "ai", "llm", "command-line", "automation"],
)

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="audit-log-client",
    version="1.4.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Python client for audit logging services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/audit-log-client",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'httpx>=0.23.0',
        'pydantic>=1.10.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-asyncio>=0.20.0',
            'twine>=4.0.0',
            'build>=0.10.0'
        ]
    },
    keywords="audit logging security monitoring",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/audit-log-client/issues",
        "Documentation": "https://github.com/yourusername/audit-log-client/wiki",
    },
)
"""
Setup script for basicsec-mcp package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="basicsec-mcp",
    version="1.0.0",
    author="Vlatko Kosturjak",
    author_email="vlatko.kosturjak@marlink.com",
    description="Model Context Protocol server for DNS and email security scanning using basicsec",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marlinkcyber/basicsec-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "basicsec>=1.0.0",
        "mcp>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "basicsec-mcp=basicsec_mcp.server:main",
        ],
    },
    keywords="security dns email spf dmarc dnssec scanner mcp",
    project_urls={
        "Bug Reports": "https://github.com/marlinkcyber/basicsec-mcp/issues",
        "Source": "https://github.com/marlinkcyber/basicsec-mcp",
        "Documentation": "https://basicsec-mcp.readthedocs.io/",
    },
)
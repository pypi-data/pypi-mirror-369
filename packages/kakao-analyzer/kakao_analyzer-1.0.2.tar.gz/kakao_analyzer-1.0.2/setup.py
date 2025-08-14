"""Setup script for Kakao Talk Analyzer"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

# Read LICENSE
license_path = Path(__file__).parent / "LICENSE"
license_text = license_path.read_text(encoding='utf-8') if license_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding='utf-8').strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="kakao-analyzer",
    version="1.0.2",
    author="xistoh162108, Claude AI",
    author_email="xistoh162108@kaist.ac.kr",
    description="Comprehensive analysis tool for KakaoTalk chat exports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xistoh162108/kakaotalk_analyzer",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "full": [
            "sentence-transformers>=2.0",
            "transformers>=4.0",
            "torch>=1.9",
        ]
    },
    entry_points={
        "console_scripts": [
            "kakao-analyzer=kakao_analyzer.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "kakao_analyzer": ["*.py"],
    },
    keywords="kakao kakaotalk chat analysis nlp korean messaging",
    project_urls={
        "Bug Reports": "https://github.com/xistoh162108/kakaotalk_analyzer/issues",
        "Documentation": "https://github.com/xistoh162108/kakaotalk_analyzer/blob/main/README.md",
        "Source": "https://github.com/xistoh162108/kakaotalk_analyzer",
    },
)
from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "AI Video Assistant - Natural Language Video Processing Tool"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'requests>=2.25.0',
        'pathlib2>=2.3.0; python_version < "3.4"',
    ]

setup(
    name="clivid",
    version="1.0.2",
    author="Donald Duck",
    author_email="themuskinrusk2022@protonmail.me",
    description="CLI Video Assistant - AI-powered video processing with natural language interface",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/localhost969/clivid",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Conversion",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "twine>=3.0",
            "wheel>=0.36",
        ],
    },
    entry_points={
        "console_scripts": [
            "clivid=clivid.cli:main",
            "cv=clivid.cli:main",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "clivid": ["tasks/*.py"],
    },
    keywords="cli video processing ffmpeg natural language assistant automation clivid",
    project_urls={
        "Bug Reports": "https://github.com/localhost969/clivid/issues",
        "Source": "https://github.com/localhost969/clivid",
        "Documentation": "https://github.com/localhost969/clivid#readme",
    },
)

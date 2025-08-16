from setuptools import setup, find_packages
from os import path
import re

current_dir = path.abspath(path.dirname(__file__))

with open(path.join(current_dir, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

def get_version():
    with open(path.join(current_dir, "llvd", "__init__.py"), "r") as f:
        content = f.read()
    return re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content).group(1)
setup(
    name="llvd",
    version=get_version(),
    url="https://github.com/knowbee/llvd.git",
    author="Igwaneza Bruce",
    author_email="knowbeeinc@gmail.com",
    description="Linkedin Learning Video Downloader CLI Tool",
    long_description=readme,
    long_description_content_type="text/markdown",
    platforms="any",
    python_requires=">=3.6",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "beautifulsoup4>=4.12.2",  # Latest stable, maintains BS4 compatibility
        "certifi>=2023.7.22",      # Security updates
        "chardet>=5.2.0",          # Security and bug fixes
        "click>=8.1.7",            # Latest stable with bug fixes
        "idna>=3.4",               # Keep current as it's a core dependency
        "requests>=2.31.0",        # Latest stable with security updates
        "soupsieve>=2.5",          # Compatible with latest beautifulsoup4
        "tqdm>=4.66.1",            # Latest stable with bug fixes
        "urllib3>=2.0.7",          # Latest stable with security updates
        "click-spinner>=0.1.10",   # Keep current as it's a stable release
        "texttable>=1.7.0"        # Keep current as it's a stable release
    ],
    entry_points={"console_scripts": ["llvd = llvd.cli:main"]},
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)

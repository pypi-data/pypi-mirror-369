from setuptools import setup, find_packages
from pathlib import Path

ROOT = Path(__file__).parent
README = (ROOT / "README.md").read_text(encoding="utf-8")

setup(
    name="ElgatoWavePy",
    version="0.1.5",
    packages=find_packages(exclude=("tests", "examples")),
    install_requires=[
        "websockets>=12.0",
    ],
    author="SteepyTheFrenchMaker",
    description="Control Elgato Wave Link (2.0.6+) volumes/outputs via WebSocket.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Ste3py/ElgatoWavePy",
    project_urls={
        "Documentation": "https://github.com/Ste3py/ElgatoWavePy/wiki",
        "Source": "https://github.com/Ste3py/ElgatoWavePy",
        "Issues": "https://github.com/Ste3py/ElgatoWavePy/issues",
    },
    license="MIT",
    license_files=("LICENSE",),
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    zip_safe=False,
)

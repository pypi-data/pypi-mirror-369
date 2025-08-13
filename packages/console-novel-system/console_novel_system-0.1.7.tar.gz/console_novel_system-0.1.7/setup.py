from setuptools import setup
from pathlib import Path

here = Path(__file__).parent

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="console-novel-system",
    packages=["cns"],
    version="0.1.7",
    author="Error Dev",
    author_email="3rr0r.d3v@gmail.com",
    description="A system to help create \"visual novels\", but run in the console.",
    install_requires=["requests", "packaging", "colorama"],
    python_requires=">=3.6",
    license="Proprietary",
    license_files=(
        "LICENSE.md",
        "LICENSE",
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Environment :: Console",
        "Natural Language :: English",
    ],
)

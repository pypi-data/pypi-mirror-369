import setuptools
from pathlib import Path
setuptools.setup(
    name="jeslorpdf",
    version="0.1.0",
    author="Jeslor Ssozi",
    packages=setuptools.find_packages(exclude=["text", "data"]),
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",

)
